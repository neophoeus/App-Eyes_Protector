@echo off
chcp 65001 >nul
echo ===================================================
echo     App-Eyes Protector - Remove Startup Script
echo ===================================================
echo.

set STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set SHORTCUT_PATH=%STARTUP_DIR%\App-Eyes_Protector.lnk

if exist "%SHORTCUT_PATH%" (
    echo [RUN] Removing shortcut from your startup folder...
    del "%SHORTCUT_PATH%"
    echo.
    echo [SUCCESS] Successfully removed App-Eyes Protector from startup!
    echo The eye protector will no longer run automatically in the background.
) else (
    echo [INFO] App-Eyes Protector was not configured to run on startup,
    echo        or the shortcut has already been removed.
)

echo.
pause
