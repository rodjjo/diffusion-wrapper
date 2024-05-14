if exist venv/ (
    echo Virtual env already exists.
) else (
    python -m venv venv
)

@echo off
call .\venv\Scripts\activate.bat
@echo on

.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m pip install -r requirements-torch.txt