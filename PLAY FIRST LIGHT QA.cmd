@echo off
cd /d "%~dp0"
python tools\firstlight_playtest.py qa
if errorlevel 1 pause
