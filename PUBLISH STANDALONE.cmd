@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if not defined AEGIS_STANDALONE_DIR set "AEGIS_STANDALONE_DIR=C:\AegisReachBuilds\First-Light"
set "TAG=%~1"
if "%TAG%"=="" set "TAG=v0.2.0-alpha"

if /I "%TAG:~0,1%"=="v" (
  set "SAFE_TAG=%TAG:~1%"
) else (
  set "SAFE_TAG=%TAG%"
)

set "PACKAGE=dist\Aegis-Reach-First-Light-%SAFE_TAG%-win64.zip"
set "CHECKSUM=%PACKAGE%.sha256"
set "NOTES=dist\Aegis-Reach-First-Light-%SAFE_TAG%-win64-release-notes.md"

echo ============================================================
echo  AEGIS REACH: FIRST LIGHT - PUBLISH WINDOWS STANDALONE
echo ============================================================
echo Tag: %TAG%
echo Export: %AEGIS_STANDALONE_DIR%
echo.

where gh >nul 2>nul
if errorlevel 1 (
  echo ERROR: GitHub CLI ^(gh^) is required and must be authenticated.
  echo Install/authenticate gh, then run this command again.
  exit /b 1
)

gh release view "%TAG%" --repo ProhibitedTV/Aegis-Reach >nul 2>nul
if not errorlevel 1 (
  echo ERROR: GitHub release %TAG% already exists. Refusing to replace it.
  exit /b 1
)

python -B tools\firstlight_standalone.py package --root "%AEGIS_STANDALONE_DIR%" --tag "%TAG%" --output-dir dist
if errorlevel 1 exit /b 1

for /f %%i in ('git rev-parse HEAD') do set "GIT_SHA=%%i"
if "%GIT_SHA%"=="" (
  echo ERROR: Could not resolve the source git commit.
  exit /b 1
)

echo.
echo Publishing %TAG% from source commit %GIT_SHA%...
gh release create "%TAG%" "%PACKAGE%" "%CHECKSUM%" ^
  --repo ProhibitedTV/Aegis-Reach ^
  --target "%GIT_SHA%" ^
  --title "Aegis Reach: First Light - Windows Standalone %TAG%" ^
  --notes-file "%NOTES%" ^
  --prerelease
if errorlevel 1 exit /b 1

echo.
echo STANDALONE RELEASE PUBLISHED: %TAG%
exit /b 0
