@echo off
echo Installing/Updating pyinstaller...
python -m pip install pyinstaller

echo Start packing main.py...
:: --noconsole: Do not display a console window behind the application
:: --onefile: Create a single executable file
:: --name: Specify the name of the output executable
:: --noconfirm: Do not ask for confirmation, overwrite directly
python -m PyInstaller --noconsole --onefile --name EyesProtector --noconfirm main.py

echo.
echo ==============================================
echo Build finished! The executable is located in the dist folder.
echo Filename: dist\EyesProtector.exe
echo ==============================================
pause
