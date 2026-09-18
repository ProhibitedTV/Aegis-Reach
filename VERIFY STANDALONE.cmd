@echo off
setlocal
cd /d "%~dp0"

if not defined AEGIS_STANDALONE_DIR set "AEGIS_STANDALONE_DIR=C:\AegisReachBuilds\First-Light"

echo Verifying standalone export at:
echo   %AEGIS_STANDALONE_DIR%
echo.

python -B tools\firstlight_standalone.py verify --root "%AEGIS_STANDALONE_DIR%" --manifest "%AEGIS_STANDALONE_DIR%\standalone-manifest.json"
set "RC=%ERRORLEVEL%"

if not "%RC%"=="0" (
  echo.
  echo STANDALONE VERIFICATION FAILED.
  exit /b %RC%
)

echo.
echo STANDALONE VERIFICATION PASSED.
echo Next: run PUBLISH STANDALONE.cmd v0.2.0-alpha
exit /b 0
