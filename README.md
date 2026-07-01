# App-Eyes Protector

[English](#english) | [繁體中文](#繁體中文)

---

## English

A highly lightweight, zero-dependency, immersive eye protection assistant for Windows.

**Latest Release:** v3.1  
**Release Notes:** See [CHANGELOG.md](CHANGELOG.md)

> **What is the 20-20-20 Rule?**  
> It is a golden rule recommended by the American Academy of Ophthalmology (AAO) and professional doctors: **"Every 20 minutes spent using a screen, you should try to look away at something that is 20 feet away from you for a total of 20 seconds."**
>
> This app is specifically designed based on this medical principle, providing you with a stress-free, natural, and smooth 20-second break guidance to effectively soothe ciliary muscle fatigue and prevent Digital Eye Strain (DES).

### 💡 Core Highlights

1. **High-Quality Undisturbed Persistence**: Automatically hides in the background. Only a high-quality "semi-transparent rounded rectangular eye" floating widget stays in the corner of the screen. Hovering the mouse allows you to quickly and safely exit without forcibly interrupting your workflow.
2. **Non-Interactive Fading Warning Overlay**: Instead of an intrusive popup dialog, the screen gently fades in over a 20-second warning duration. It is click-through (`WS_EX_TRANSPARENT | WS_EX_LAYERED`), allowing you to finish active tasks uninterrupted before the actual rest begins.
3. **Green & Lightweight, Ready to Use**: Zero external package dependencies, no installation required. It consists of a single Python executable (.exe) that purely calls Windows native APIs, along with simple startup/shutdown scripts.
4. **Forest Dark Mode & Low-Power Circular Progress**: Overhauled with a premium dark forest green theme (`#0d130f` background and `#16201a` cards) to minimize screen emission. Includes a clean circular progress ring that ticks at 1Hz (once per second) during countdowns. Card dimensions scale dynamically to 55% of the screen width for great presence on 4K displays, with dynamic fonts and elegant large rounded corners (8% of card height).

### ⚙️ Technical Principles

- **Environment Detection & Power Friendly**: Intelligently determines whether the user is in full-screen gaming, watching a video, or presenting by combining Windows native API (`SHQueryUserNotificationState`), foreground full-screen window detection, and hardware input monitoring (`GetLastInputInfo`). Even if the mouse is still moving, full-screen playback or presentation mode will pause reminder timing. Moreover, it boasts an ultra-optimized event loop that **will not prevent Windows from automatically turning off the display or entering sleep mode**.
- **Reason-Aware Reminder Freeze**: The timer now distinguishes between idle absence and full-screen focus. Idle resets the elapsed reminder time, while full-screen playback or presentation freezes the timer in place and uses transition debounce to avoid jitter when entering or leaving full-screen mode.
- **Smart Pause**: Need absolute focus? Just unfold the widget and click the canvas-drawn pause control. The eye protector icon will smoothly transition into a newly designed, canvas-drawn "closed eye" indicator, and the timer will freeze. Resuming the timer will automatically start counting from zero, keeping the flow going naturally.
- **Rendering Engine**: Zero image file dependencies, entirely built using the Python `tkinter.Canvas` native drawing tool. It now uses native Windows DPI awareness for sharper 4K rendering, paired with pure-code floating UI controls and icons for more consistent visual output.
- **Safer Break Startup and Exit**: If the full-screen break window cannot initialize, the app now restores the previous runtime state instead of leaving the session half-transitioned. Quit requests are also guarded so repeated clicks cannot trigger a broken shutdown sequence.
- **Ultra-Lightweight Deployment**: Discards all external third-party packages and uses PyInstaller to package into a single background executable (`EyesProtector.exe`), paired with BAT batch scripts for easy auto-startup on boot and uninstallation.

### 🚀 Quick Start

#### Get the Executable

This project has been compiled into a single portable executable using PyInstaller. You can find `EyesProtector.exe` directly in the `dist` folder.

#### Set Up Auto-Startup on Boot

- **Enable Auto-Protection**: Double-click `setup_startup.bat` to automatically add it to your Windows startup items.
- **Disable Auto-Protection**: Double-click `remove_startup.bat` to easily remove it.

#### Manual Testing and Operation

- **Show CLI Help Instructions**: Run `EyesProtector.exe --help` or `-h` to print detailed option descriptions and exit cleanly.
- **Test Animation Effects**: You can run `EyesProtector.exe --test` from the terminal to immediately test the 10-second reminder and 5-second break.
- **Pre-Break Warning & Postpone**: When the warning starts, you can hover over the floating widget in the bottom-right corner and click the canvas-drawn pause control to immediately dismiss the warning and pause protection.
- **Interrupt Break**: If you urgently need to return to work during a break, click the top-right close chip to end the break early and return to background timing.
- **Pause / Exit Program**: To completely close or pause the eye protection assistant, move your mouse over the "semi-transparent eye floating widget" in the bottom-right corner. You can click the canvas-drawn pause control to pause protection, or click the red close control on the expanded panel to safely end it.

### 🛠️ Development and Building

If you want to modify the source code and recompile it yourself, ensure you have Python 3 installed, and run the build script in the root directory:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements-dev.txt
.\build.bat
```

If the build fails while replacing `dist\EyesProtector.exe`, close any running `EyesProtector.exe` process first and rerun the script.

After the build is complete, the latest executable `EyesProtector.exe` will be generated in the `dist` directory.

#### Run Automated Tests

```bash
python -m unittest discover -s tests -v
```

#### Manual Verification Checklist

1. Run `EyesProtector.exe --test` and confirm the floating widget appears near the bottom-right corner and renders sharply on a 4K display.
2. Hover the widget and verify the pause and close controls expand correctly, with the canvas-drawn icons remaining crisp.
3. Click pause, wait 10 seconds, and confirm no warning overlay appears while paused.
4. Resume and confirm the reminder countdown restarts from zero instead of resuming the old elapsed time.
5. When the fading warning starts, verify that you can click and type behind the overlay.
6. Verify that the circular progress arc fills up in warning mode and drains in rest mode, and that the screen becomes opaque and interactive after the warning reaches 0.
7. During the break, click the top-right close chip and confirm the break ends immediately without delayed follow-up callbacks.
8. Relaunch the app while it is already running and confirm the single-instance prompt appears.
9. Open the floating widget and click the close control; confirm the app exits cleanly without orphaned windows or repeated shutdown prompts.

---

## 繁體中文

一款極輕量、零依賴的 Windows 沉浸式護眼助理。

**最新版本：** v3.1  
**版本說明：** 請見 [CHANGELOG.md](CHANGELOG.md)

> **什麼是 20-20-20 護眼法則？**  
> 這是由美國眼科醫學會（AAO）與專業醫師廣泛推廣的黃金護眼指南：**「每使用螢幕 20 分鐘，就把視線移開看 20 呎（約 6 公尺）遠的物體，持續 20 秒鐘。」**
>
> 本應用程式正是基於此醫學原理量身打造，為您提供無壓力、最自然流暢的 20 秒休息引導，有效舒緩睫狀肌疲勞並預防數位眼疲勞症候群（DES）。

### 💡 核心亮點

1. **高質感無擾常駐**：平時自動隱藏於系統背景，僅在畫面角落常駐一顆高質感的「半透明方形圓角眼睛」懸浮窗格，滑鼠移入即可快速安全退出，不強暴中斷您的工作心流。
2. **漸進式無干擾全螢幕預警**：當護眼時間到時，會先以 5% 的不透明度漸漸顯現，並在 20 秒預警期內慢慢加深。預警視窗完全支援「滑鼠穿透」（Click-through）且不搶奪焦點，讓您能不受干擾地完成正在輸入的字句或點選的按鈕。
3. **綠色輕量，隨開即用**：零外部套件依賴、免安裝。由一支純粹呼叫 Windows 原生 API 的 Python 單一執行檔 (.exe) 與簡易的開關腳本構成。
4. **低功耗森林暗色模式與環形進度條**：全面換上極低功耗且護眼的深森林綠背景（`#0d130f`）與深綠卡片（`#16201a`）。卡片中央帶有薄荷綠的環形進度條，更新頻率限制在超低功耗的 `1Hz`（一秒一次）。休息卡片會根據螢幕解析度動態拉伸至螢幕寬度的 `55%`（在 4K 螢幕上高達 1920 像素寬），並搭配超大優雅圓角（高度 8%）與等比例自適應字型。

### ⚙️ 技術原理

- **環境與電源偵測**：透過結合 Windows 底層原生 API (`SHQueryUserNotificationState`)、前景全螢幕視窗判定與硬體事件 (`GetLastInputInfo`)，智慧判斷使用者是否看影片、玩遊戲、簡報或離開座位，避免打擾。即使滑鼠仍有移動，只要正在全螢幕播放或簡報也會停止倒數。更具備極度優化的事件迴圈，**絕不會阻擋 Windows 系統自動關閉螢幕或進入休眠狀態**。
- **原因分流停表策略**：現在會區分「離席」與「全螢幕專注」兩種 busy 原因。離席時會將提醒倒數歸零；全螢幕播放或簡報時則凍結目前進度，並加入進出場 debounce，避免全螢幕切換瞬間造成計時抖動。
- **貼心暫停模式**：需要絕對專注？將滑鼠移至懸浮窗並點擊重新繪製的 canvas 暫停控制。護眼圖示會平滑切換為高質感的「閉眼休息」專屬繪製圖示，且計時器完全凍結；當再次恢復防護時會自動「從零開始重新計時」，給予最無壓力的轉場體驗。
- **渲染引擎**：零圖檔依賴，完全使用 Python `tkinter.Canvas` 原生繪圖工具，並透過 Windows DPI awareness 提升 4K 螢幕上的清晰度，搭配純代碼渲染的懸浮 UI 控制與專屬狀態圖示。
- **更安全的休息切換與退出流程**：若全螢幕休息視窗初始化失敗，程式現在會自動回復到原本狀態，不會卡在半切換狀態；退出請求也有防重入保護，避免重複點擊造成異常關閉流程。
- **極輕量部署**：捨棄所有外部第三方套件，並透過 PyInstaller 打包為單一背景執行檔 (`EyesProtector.exe`)，搭配 BAT 批次腳本達成簡易的開機自動啟動與卸載。

### 🚀 快速上手

#### 取得執行檔

本專案已透過 PyInstaller 編譯為單一免安裝執行檔。您可以直接在 `dist` 資料夾中找到 `EyesProtector.exe`。

#### 設定開機自動啟動

- **開啟自動保護**：點擊兩下 `setup_startup.bat`，即可自動將其加入 Windows 開機啟動項目。
- **取消自動保護**：點擊兩下 `remove_startup.bat` 即可輕鬆解除。

#### 手動測試與操作

- **顯示命令列說明**：執行 `EyesProtector.exe --help` 或 `-h` 印出詳細的執行參數說明。
- **測試動畫效果**：您可以從終端機執行 `EyesProtector.exe --test` 來立即測試 10 秒提醒與 5 秒休息。
- **預警中斷與暫停**：在預警畫面漸進顯現時，您可以將滑鼠移至懸浮窗點選暫停，以立即收回預警畫面並暫停防護。
- **中斷休息**：若需緊急回到工作，點擊全螢幕右上角的 close chip 即可提早結束本次休息並退回背景計時。
- **暫停或退出程式**：若欲暫停測量或完全關閉護眼助理，請對著畫面右下角的「半透明眼睛懸浮窗格」移入滑鼠，展開面板後可點擊 canvas 暫停控制進入凍結暫停模式，或點擊紅色 close 控制安全結束常駐。

### 🛠️ 開發與編譯

如果您想自行修改原始碼並重新編譯，請確認您已安裝 Python 3，並執行根目錄下的打包腳本：

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements-dev.txt
.\build.bat
```

若打包時無法覆寫 `dist\EyesProtector.exe`，請先關閉正在執行的 `EyesProtector.exe` 後再重新執行。

編譯完成後，最新的執行檔 `EyesProtector.exe` 將會產生在 `dist` 目錄下。

#### 執行自動化測試

```bash
python -m unittest discover -s tests -v
```

#### 手動驗證清單

1. 執行 `EyesProtector.exe --test`，確認右下角出現懸浮窗，且在 4K 螢幕上仍保持清晰。
2. 滑鼠移入懸浮窗，確認暫停與關閉控制會正確展開，且重新繪製的 canvas 圖示保持銳利。
3. 點擊暫停後等待 10 秒，確認暫停期間不會跳出預警視窗。
4. 重新恢復後，確認提醒倒數會從零重新開始，而不是沿用先前進度。
5. 當漸進式預警畫面出現時，確認可以穿透點擊與打字。
6. 確認預警結束後，進度條切換至休息模式，畫面變為不透明且防護介入，圓環進度條每秒重繪一次（1Hz 頻率）。
7. 在休息視窗中點擊右上角 close chip，確認可以立即結束，且不會殘留延遲 callback。
8. 在程式已執行時再次啟動，確認單實例提示視窗正常出現。
9. 展開懸浮窗後點擊 close 控制，確認程式會乾淨退出，不會殘留視窗或出現重複關閉提示。
