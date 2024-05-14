import json
import os
import functools


class ColorCap:
    GRAY_256 = 1
    RGB_16 = 2
    RGB_24 = 3

class NoProjectError(Exception):
    pass

class Context:
    cfg_path: str
    project_dir: str = None

    def __init__(self, cfg_path: str):
        self.cfg_path = cfg_path
        if os.path.exists(cfg_path):
            with open(cfg_path, 'r') as fp:
                data = json.load(fp)
                self.project_dir = data.get('project_dir', None)

    def save(self):
        with open(self.cfg_path, 'w') as fp:
            data = {
                'project_dir': self.project_dir
            }
            json.dump(data, fp, indent=2)


class Project:
    project_dir: str
    cfg_path: str
    raw: dict = {}
    
    frame_width: int = 512
    frame_height: int = 288  
    frame_count: int = 480
    color_cap: int = ColorCap.RGB_24
    use_scene_detector: bool = False

    def __init__(self, project_dir: str):
        self.project_dir = project_dir 
        cfg_path = os.path.join(project_dir, 'project-config.json')
        self.cfg_path = cfg_path
        if os.path.exists(cfg_path):
            with open(cfg_path, 'r') as fp:
                raw = json.load(fp)
        self._load_from_raw()
    
    def _load_from_raw(self):
        pass

    def _store_raw(self):
        pass

    def save(self):
        self._store_raw()
        with open(self.cfg_path, 'w') as fp:
            json.dump(self.raw, fp, indent=2)


def is_unix():
    try:
        if os.path.exists('/tmp'):
            return True
    except:
        pass
    return False


def user_data_dir():
    if is_unix():
        dir_name = os.path.expanduser('~/.diffusion_wrapper')
    else:
        dir_name = os.path.expandvars('%APPDATA%\diffusion_wrapper')
    if not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)
    return os.path.abspath(dir_name)


@functools.cache
def get_context():
    context_file = os.path.join(user_data_dir(), 'context.json')
    return Context(context_file)


@functools.cache
def get_project_directory():
    return get_context().project_dir


@functools.cache
def get_project():
    if get_project_directory():
        project_dir = os.path.join(get_project_directory())
        return Project(project_dir)
    raise NoProjectError()


def get_temp_dir():
    pd = get_project().project_dir
    temp_dir = os.path.join(pd, 'temp')
    return temp_dir