@echo off
cd /d "%~dp0"
python tools\firstlight_collect.py
if errorlevel 1 pause
