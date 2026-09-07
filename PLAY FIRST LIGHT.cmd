@echo off
cd /d "%~dp0"
python tools\firstlight_playtest.py play
if errorlevel 1 pause
