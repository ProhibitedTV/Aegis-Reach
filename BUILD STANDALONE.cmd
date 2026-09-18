@echo off
setlocal
cd /d "%~dp0"

if not defined AEGIS_STANDALONE_DIR set "AEGIS_STANDALONE_DIR=C:\AegisReachBuilds\First-Light"

echo ============================================================
echo  AEGIS REACH: FIRST LIGHT - PREPARE STANDALONE EXPORT
echo ============================================================
echo.
echo Export target:
echo   %AEGIS_STANDALONE_DIR%
echo.

if not exist "%AEGIS_STANDALONE_DIR%" mkdir "%AEGIS_STANDALONE_DIR%"

dir /b "%AEGIS_STANDALONE_DIR%" 2>nul | findstr . >nul
if not errorlevel 1 (
  echo WARNING: The export directory is not empty.
  echo MAX may overwrite or mix files with an older standalone build.
  echo Clear it manually if you want a completely clean export.
  echo.
)

echo Running First Light rebuild, load-safety and preflight registration...
python -B tools\firstlight_playtest.py deploy
if errorlevel 1 (
  echo.
  echo PREP FAILED. GameGuru MAX was not launched.
  exit /b 1
)

echo.
echo Launching the registered Aegis Reach project in GameGuru MAX...
python -B tools\firstlight_playtest.py play
if errorlevel 1 exit /b 1

start "" explorer.exe "%AEGIS_STANDALONE_DIR%"

echo.
echo ------------------------------------------------------------
echo IN GAMEGURU MAX:
echo   1. Open Storyboard for Aegis Reach.
echo   2. Make sure FIRST LIGHT is the intended playable mission.
echo   3. Choose Save Standalone Game.
echo   4. Export to:
echo      %AEGIS_STANDALONE_DIR%
echo   5. Exit MAX when the export is complete.
echo   6. Run VERIFY STANDALONE.cmd.
echo ------------------------------------------------------------
echo.
exit /b 0
