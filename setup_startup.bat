@echo off
chcp 65001 >nul
echo Configuring App-Eyes_Protector to run at startup...

:: Get absolute path of EyesProtector.exe in current directory
set "EXE_PATH=%~dp0dist\EyesProtector.exe"

:: Check if exe exists
if not exist "%EXE_PATH%" (
    echo [ERROR] EyesProtector.exe not found! Please check if compilation was successful.
    pause
    exit /b
)

:: Set startup folder path
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_PATH=%STARTUP_FOLDER%\App-Eyes_Protector.lnk"

:: Create shortcut via PowerShell
echo Creating shortcut at: %SHORTCUT_PATH%
powershell -Command "$wshell = New-Object -ComObject WScript.Shell; $shortcut = $wshell.CreateShortcut('%SHORTCUT_PATH%'); $shortcut.TargetPath = '%EXE_PATH%'; $shortcut.WorkingDirectory = '%~dp0dist'; $shortcut.Save()"

echo.
echo ==============================================
echo Setup successful! App-Eyes_Protector will automatically run on next startup.
echo To test it right now, double click EyesProtector.exe in the dist folder.
echo ==============================================
pause
