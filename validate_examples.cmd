@echo off
if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" "%~dp0dev_utils\validate_examples.py" %*
) else (
    python "%~dp0dev_utils\validate_examples.py" %*
)
