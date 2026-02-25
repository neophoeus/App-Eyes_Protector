@echo off
echo 安裝/更新 pyinstaller...
python -m pip install pyinstaller

echo 開始打包 main.py...
:: --noconsole: 不要螢幕背後黑視窗
:: --onefile: 產出單一執行檔
:: --name: 指定輸出的執行檔名稱
:: --noconfirm: 不要詢問是否覆蓋，直接覆蓋
python -m PyInstaller --noconsole --onefile --name EyesProtector --noconfirm main.py

echo.
echo ==============================================
echo 打包完成！執行檔已經放在 dist 資料夾內。
echo 檔名: dist\EyesProtector.exe
echo ==============================================
pause
