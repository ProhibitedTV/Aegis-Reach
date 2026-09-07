@echo off
cd /d "%~dp0"
echo FIRST LIGHT QA is observational only. You remain in full manual control.
python tools\firstlight_playtest.py qa
if errorlevel 1 pause
