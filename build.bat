@echo off
setlocal
pushd "%~dp0"

set "VENV_PYTHON=%~dp0..\.venv\Scripts\python.exe"
set "PYTHON_CMD=python"

if exist "%VENV_PYTHON%" (
	set "PYTHON_CMD=%VENV_PYTHON%"
)

echo Using Python: %PYTHON_CMD%
echo Installing/Updating development dependencies...
"%PYTHON_CMD%" -m pip install -r "%~dp0requirements-dev.txt"

echo Generating release assets...
"%PYTHON_CMD%" "%~dp0tools\generate_release_assets.py"

if errorlevel 1 (
	echo.
	echo Asset generation failed.
	pause
	popd
	exit /b 1
)

echo Start packing EyesProtector.spec...
"%PYTHON_CMD%" -m PyInstaller --noconfirm EyesProtector.spec

if errorlevel 1 (
	echo.
	echo Build failed. If dist\EyesProtector.exe is running, close it and try again.
	pause
	popd
	exit /b 1
)

echo.
echo ==============================================
echo Build finished! The executable is located in the dist folder.
echo Filename: dist\EyesProtector.exe
echo ==============================================
pause
popd
