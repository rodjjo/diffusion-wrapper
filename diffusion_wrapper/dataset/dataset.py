
import io
import hashlib
import json
import os
import subprocess

import cv2 as cv
import click
from scenedetect.detectors import AdaptiveDetector

from diffusion_wrapper.config import ColorCap, get_project, get_temp_dir


def check_tools():
    try:
        subprocess.check_call([
            'ffmpeg', '-version'
        ], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        raise Exception("ffmpeg not installed or not in the PATH environment variable")


def get_hash(video_path: str):
    with open(video_path, 'rb') as fp:
        if not fp:
            return None
        fp.seek(0, io.SEEK_END)
        file_size = fp.tell()
        if file_size < 64000 * 3:
            return None
        fp.seek(0)
        buffer = []
        buffer.append(fp.read(64000))
        fp.seek(file_size // 2)
        buffer.append(fp.read(64000))
        fp.seek(64001, io.SEEK_END)
        buffer.append(fp.read(64000))
        su = hashlib.md5(usedforsecurity=False)
        for b in buffer:
            su.update(b)
        return f'{su.hexdigest()}-{str(file_size)}'
    
    
class WrapperSceneDetector(AdaptiveDetector):
    def __init__(self, enabled=True):
        super().__init__()
        self.enabled = enabled

    def process_frame(self,  frame_num, frame_img):
        if not self.enabled:
            return False
        result = super().process_frame(frame_num, frame_img)
        return len(result) > 0

    def post_process(self, scene_list):
        pass


class DataSetEntry:
    original_path: str
    original_hash: str = None
    label: str = ''

    @classmethod
    def from_video(cls, filepath: str):
        result = cls()
        result.original_path = filepath
        result.original_hash = get_hash(filepath)
        result.label = ''
        return result
    
    @classmethod
    def from_config(cls, original_path: str, original_hash: str, label: str = ''):
        result = cls()
        result.original_path = original_path
        result.original_hash = original_hash
        result.label = label
        return result

    @classmethod
    def from_dict(cls, d: dict):
        return cls.from_config(d['op'], d['oh'], d['lb'])

    @property
    def id(self) -> str:
        return self.original_hash
    
    @property
    def video_path(self):
        return os.path.join(get_project().project_dir, f'dataset/{self.id}.mp4')
    
    @property
    def valid(self) -> bool:
        return self.original_hash is not None
    
    def to_dict(self):
        return {
            "op": self.original_path,
            "oh": self.original_hash,
            "lb": self.label,
        }
    
    def iterate_frames(self):
        cap = cv.VideoCapture(self.video_path)

        detector = WrapperSceneDetector(
            enabled=get_project().use_scene_detector
        )

        frame_count = get_project().frame_count
        frames = []
        color = get_project().color_cap 
        has_new_scene = False
        frame_number = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            has_new_scene = detector.process_frame(frame_number, frame)
            frame_number += 1
            if color == ColorCap.GRAY_256:
                frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            elif color == ColorCap.RGB_16:
                frame = cv.cvtColor(frame, cv.COLOR_BGR2BGR565)
            frames.append(frame)
            if len(frames) >= frame_count:
                yield { 'frames': frames, 'label': self.label, 'new_scene': has_new_scene, 'id': self.id }
                frames = []
        cap.release()


def convert_video(d: DataSetEntry):
    if os.path.exists(d.video_path):
        return
    dir_name = os.path.dirname(d.video_path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)
    vw = get_project().frame_width
    vh = get_project().frame_height
    subprocess.check_call([
        'ffmpeg', '-i', d.original_path, '-c:v', 'libx264', '-crf', '15.0', '-an', '-s', f'{vw}x{vh}', d.video_path
    ])


class DataSet:
    dataset_path: str = ''
    items: dict = {}

    def __init__(self) -> None:
        self.dataset_path = os.path.join(get_project().project_dir, 'dataset.json')
        if os.path.exists(self.dataset_path):
            with open(self.dataset_path, 'r') as fp:
                self.items = json.load(fp)

    def add_file(self, file_path):
        entry = DataSetEntry.from_video(file_path)
        if entry.valid is False:
            return
        if entry.id not in self.items:
            convert_video(entry)
            self.items[entry.id] = entry.to_dict()

    def add_directory(self, dir_path):
        for dirpath, dirnames, filenames in os.walk(dir_path):
            for d in dirnames:
                if d in ('.', '..'):
                    continue
                self.add_directory(os.path.join(dirpath, d))
            for filename in filenames:  
                self.add_file(os.path.join(dirpath, filename))
        with open(f'{self.dataset_path}_', 'w') as fp:
            json.dump(self.items, fp)
        try:
            os.remove(self.dataset_path)
        except FileNotFoundError:
            pass
        os.rename(f'{self.dataset_path}_', self.dataset_path)

    def iterate_frames(self):
        for k in self.items.keys():
            d = DataSetEntry.from_dict(self.items[k])
            for f in d.iterate_frames():
                yield f


@click.group()
def dataset_group():
    check_tools()


@dataset_group.command
@click.option('--path', type=str, required=True)
def add_directory(path):
    dataset = DataSet()
    dataset.add_directory(os.path.abspath(path))


@dataset_group.command
@click.option('--path', type=str, required=True)
def add_file(path):
    dataset = DataSet()
    dataset.add_file(os.path.abspath(path))


@dataset_group.command
def test_frames():
    dataset = DataSet()
    temp_dir = os.path.join(get_temp_dir(), 'test-frames')
    os.makedirs(temp_dir, exist_ok=True)
    for i1, f in enumerate(dataset.iterate_frames()):
        for i2, img in enumerate(f['frames']):
            cv.imwrite(os.path.join(temp_dir, f'{i1}-{i2}.jpg'), img)
