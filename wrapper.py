import os
import sys
import subprocess

if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    py_exe = os.path.join(BASE_DIR, 'venv/Scripts/python.exe')
    subprocess.check_call([os.path.join(BASE_DIR, 'venv/Scripts/python.exe'), '-m', 'diffusion_wrapper'] + sys.argv[1:])