@echo off
rem Starts the system on Windows: Docker services, then the desktop window
setlocal
cd /d "%~dp0"
set "WEB_URL=http://localhost:5173"
set "DESKTOP_URL=%WEB_URL%/desktop.html"

if not exist ".env" (
  echo Missing .env file. See section 2 of RUNGUIDE.md.
  exit /b 1
)
docker info >nul 2>&1
if errorlevel 1 (
  echo Docker is not running. Open Docker Desktop, wait until it is ready, then run this again.
  exit /b 1
)

echo Starting PhishGuard. The first run takes several minutes.
docker compose up -d --build
if errorlevel 1 exit /b 1

echo Waiting for the detection service...
for /l %%i in (1,1,60) do (
  curl.exe -fs http://localhost:8080/api/health 2>nul | findstr "true" >nul && goto ready
  ping -n 3 127.0.0.1 >nul
)
echo The detection service did not start. Check it with: docker compose logs api
exit /b 1

:ready
set "BROWSER="
for %%p in (
  "%ProgramFiles%\Google\Chrome\Application\chrome.exe"
  "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
  "%LocalAppData%\Google\Chrome\Application\chrome.exe"
  "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"
  "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
) do (
  if not defined BROWSER if exist %%p set "BROWSER=%%~p"
)

rem A separate profile always opens a new window, whatever browser windows are already open
if defined BROWSER (
  start "" "%BROWSER%" --app=%DESKTOP_URL% --window-size=580,100 --user-data-dir="%LocalAppData%\PhishGuard\browser" --no-first-run --no-default-browser-check
) else (
  echo Chrome or Edge was not found, so the desktop window cannot open.
)

echo.
echo PhishGuard is running.
echo   Web UI:  %WEB_URL%
echo   Stop:    docker compose down
