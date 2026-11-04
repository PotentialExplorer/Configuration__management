@echo off
rem Запуск эмулятора: run.bat [параметры]
cd /d "%~dp0"
set PYTHONPATH=src
python -m shell_emulator %*
