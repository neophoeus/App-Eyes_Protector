@echo off
setlocal

set "VENV_PYTHON=%~dp0..\.venv\Scripts\python.exe"
set "PYTHON_CMD=python"

if exist "%VENV_PYTHON%" (
	set "PYTHON_CMD=%VENV_PYTHON%"
)

echo Using Python: %PYTHON_CMD%
echo Installing/Updating pyinstaller...
"%PYTHON_CMD%" -m pip install pyinstaller

echo Start packing main.py...
:: --noconsole: Do not display a console window behind the application
:: --onefile: Create a single executable file
:: --name: Specify the name of the output executable
:: --noconfirm: Do not ask for confirmation, overwrite directly
"%PYTHON_CMD%" -m PyInstaller --noconsole --onefile --name EyesProtector --noconfirm main.py

if errorlevel 1 (
	echo.
	echo Build failed. If dist\EyesProtector.exe is running, close it and try again.
	pause
	exit /b 1
)

echo.
echo ==============================================
echo Build finished! The executable is located in the dist folder.
echo Filename: dist\EyesProtector.exe
echo ==============================================
pause
