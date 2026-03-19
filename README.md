# App-Eyes Protector

[English](#english) | [繁體中文](#繁體中文)

---

## English

A highly lightweight, zero-dependency, immersive eye protection assistant for Windows.

**Latest Release:** v1.8  
**Release Notes:** See [CHANGELOG.md](CHANGELOG.md)

> **What is the 20-20-20 Rule?**  
> It is a golden rule recommended by the American Academy of Ophthalmology (AAO) and professional doctors: **"Every 20 minutes spent using a screen, you should try to look away at something that is 20 feet away from you for a total of 20 seconds."**
>
> This app is specifically designed based on this medical principle, providing you with a stress-free, natural, and smooth 20-second break guidance to effectively soothe ciliary muscle fatigue and prevent Digital Eye Strain (DES).

### 💡 Core Highlights

1. **High-Quality Undisturbed Persistence**: Automatically hides in the background. Only a high-quality "semi-transparent rounded rectangular eye" floating widget stays in the corner of the screen. Hovering the mouse allows you to quickly and safely exit without forcibly interrupting your workflow.
2. **Rendering Aesthetics, Immersive Relaxation**: Discarding traditional rigid static images, it uses pure mathematical calculations to generate 3D geometric falling leaves and breeze animations, creating a 20-second breathing moment where "your heartbeat slows down with the screen".
3. **Green & Lightweight, Ready to Use**: Zero external package dependencies, no installation required. It consists of a single Python executable (.exe) that purely calls Windows native APIs, along with simple startup/shutdown scripts.
4. **Smarter and Calmer Break Flow**: Idle time, full-screen playback, and presentation mode now use distinct reminder pause strategies, while the full-screen break view has been simplified into a cleaner split layout with a lower-power animation profile.

### ⚙️ Technical Principles

- **Environment Detection & Power Friendly**: Intelligently determines whether the user is in full-screen gaming, watching a video, or presenting by combining Windows native API (`SHQueryUserNotificationState`), foreground full-screen window detection, and hardware input monitoring (`GetLastInputInfo`). Even if the mouse is still moving, full-screen playback or presentation mode will pause reminder timing. Moreover, it boasts an ultra-optimized event loop that **will not prevent Windows from automatically turning off the display or entering sleep mode**.
- **Reason-Aware Reminder Freeze**: The timer now distinguishes between idle absence and full-screen focus. Idle resets the elapsed reminder time, while full-screen playback or presentation freezes the timer in place and uses transition debounce to avoid jitter when entering or leaving full-screen mode.
- **Smart Pause**: Need absolute focus? Just unfold the widget and click the pause (`⏸`) button. The eye protector icon will smoothly transition into a newly designed, canvas-drawn "closed eye" indicator, and the timer will freeze. Resuming the timer will automatically start counting from zero, keeping the flow going naturally.
- **Rendering Engine**: Zero image file dependencies, entirely built using the Python `tkinter.Canvas` native drawing tool. It combines mathematical geometry (trigonometric functions and random variables) to construct a lower-power falling leaf animation and features a pure-code-rendered high-quality transparent floating UI with custom-drawn eye icons.
- **Ultra-Lightweight Deployment**: Discards all external third-party packages and uses PyInstaller to package into a single background executable (`EyesProtector.exe`), paired with BAT batch scripts for easy auto-startup on boot and uninstallation.

### 🚀 Quick Start

#### Get the Executable

This project has been compiled into a single portable executable using PyInstaller. You can find `EyesProtector.exe` directly in the `dist` folder.

#### Set Up Auto-Startup on Boot

- **Enable Auto-Protection**: Double-click `setup_startup.bat` to automatically add it to your Windows startup items.
- **Disable Auto-Protection**: Double-click `remove_startup.bat` to easily remove it.

#### Manual Testing and Operation

- **Test Animation Effects**: You can run `EyesProtector.exe --test` from the terminal to immediately test the 10-second reminder and 5-second break.
- **Keyboard Shortcuts**: When the popup appears, press **Enter** to instantly start the 20-second break, or press **Escape** to snooze for 5 minutes.
- **Interrupt Break**: When the full-screen leaves are falling, if you urgently need to return to work, click the `✕` symbol in the top-right corner to end the break early and return to background timing.
- **Pause / Exit Program**: To completely close or pause the eye protection assistant, move your mouse over the "semi-transparent eye floating widget" in the bottom-right corner. You can click `⏸` to pause the protection, or click the red `✕` on the expanded panel to safely end it.

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

1. Run `EyesProtector.exe --test` and confirm the floating widget appears near the bottom-right corner.
2. Hover the widget and verify the pause and close controls expand correctly.
3. Click pause, wait 10 seconds, and confirm no reminder dialog appears while paused.
4. Resume and confirm the reminder countdown restarts from zero instead of resuming the old elapsed time.
5. When the reminder dialog appears, press `Esc` and confirm the next reminder is delayed by about 5 seconds in test mode.
6. Trigger the reminder again, press `Enter`, and confirm the full-screen break opens and counts down.
7. During the break, click the top-right `✕` and confirm the break ends immediately without delayed follow-up callbacks.
8. Relaunch the app while it is already running and confirm the single-instance prompt appears.

---

## 繁體中文

一款極輕量、零依賴的 Windows 沉浸式護眼助理。

**最新版本：** v1.8  
**版本說明：** 請見 [CHANGELOG.md](CHANGELOG.md)

> **什麼是 20-20-20 護眼法則？**  
> 這是由美國眼科醫學會（AAO）與專業醫師廣泛推廣的黃金護眼指南：**「每使用螢幕 20 分鐘，就把視線移開看 20 呎（約 6 公尺）遠的物體，持續 20 秒鐘。」**
>
> 本應用程式正是基於此醫學原理量身打造，為您提供無壓力、最自然流暢的 20 秒休息引導，有效舒緩睫狀肌疲勞並預防數位眼疲勞症候群（DES）。

### 💡 核心亮點

1. **高質感無擾常駐**：平時自動隱藏於系統背景，僅在畫面角落常駐一顆高質感的「半透明方形圓角眼睛」懸浮窗格，滑鼠移入即可快速安全退出，不強暴中斷您的工作心流。
2. **算繪美學，沉浸放鬆**：捨棄傳統呆板的靜態圖，運用純數學運算生成 3D 幾何落葉與微風動畫，打造 20 秒「心跳跟著畫面慢下來」的呼吸時刻。
3. **綠色輕量，隨開即用**：零外部套件依賴、免安裝。由一支純粹呼叫 Windows 原生 API 的 Python 單一執行檔 (.exe) 與簡易的開關腳本構成。
4. **提醒邏輯更穩、休息畫面更俐落**：離席、全螢幕播放與簡報模式現在採用不同停表策略；全螢幕休息畫面則改為更乾淨的雙欄版面，並使用更省電的動畫設定。

### ⚙️ 技術原理

- **環境與電源偵測**：透過結合 Windows 底層原生 API (`SHQueryUserNotificationState`)、前景全螢幕視窗判定與硬體事件 (`GetLastInputInfo`)，智慧判斷使用者是否看影片、玩遊戲、簡報或離開座位，避免打擾。即使滑鼠仍有移動，只要正在全螢幕播放或簡報也會停止倒數。更具備極度優化的事件迴圈，**絕不會阻擋 Windows 系統自動關閉螢幕或進入休眠狀態**。
- **原因分流停表策略**：現在會區分「離席」與「全螢幕專注」兩種 busy 原因。離席時會將提醒倒數歸零；全螢幕播放或簡報時則凍結目前進度，並加入進出場 debounce，避免全螢幕切換瞬間造成計時抖動。
- **貼心暫停模式**：需要絕對專注？將滑鼠移至懸浮窗並點擊暫停 (`⏸`) 按鈕。護眼圖示將平滑切換為高質感的「閉眼休息」專屬繪製圖示，且計時器完全凍結；當再次恢復防護時會自動「從零開始重新計時」，給予最無壓力的轉場體驗。
- **渲染引擎**：零圖檔依賴，完全使用 Python `tkinter.Canvas` 原生繪圖工具。結合數學幾何（三角函數與隨機變數）建構更省電的落葉動畫，並具備純代碼渲染的高質感去背懸浮 UI 與專屬繪製的狀態圖示。
- **極輕量部署**：捨棄所有外部第三方套件，並透過 PyInstaller 打包為單一背景執行檔 (`EyesProtector.exe`)，搭配 BAT 批次腳本達成簡易的開機自動啟動與卸載。

### 🚀 快速上手

#### 取得執行檔

本專案已透過 PyInstaller 編譯為單一免安裝執行檔。您可以直接在 `dist` 資料夾中找到 `EyesProtector.exe`。

#### 設定開機自動啟動

- **開啟自動保護**：點擊兩下 `setup_startup.bat`，即可自動將其加入 Windows 開機啟動項目。
- **取消自動保護**：點擊兩下 `remove_startup.bat` 即可輕鬆解除。

#### 手動測試與操作

- **測試動畫效果**：您可以從終端機執行 `EyesProtector.exe --test` 來立即測試 10 秒提醒與 5 秒休息。
- **鍵盤快捷鍵支援**：當倒數視窗跳出時，可直接按下 **Enter** 鍵進入 20 秒大休息，或是按下 **Escape** 鍵將提醒延遲 5 分鐘。
- **中斷休息**：當全螢幕樹葉飄落時，若需緊急回到工作，點擊畫面右上角的 `✕` 符號即可提早結束本次休息並退回背景計時。
- **暫停或退出程式**：若欲暫停測量或完全關閉護眼助理，請對著畫面右下角的「半透明眼睛懸浮窗格」移入滑鼠，展開面板後可點擊 `⏸` 按鈕進入凍結暫停模式，或點擊紅色 `✕` 安全結束常駐。

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

1. 執行 `EyesProtector.exe --test`，確認右下角出現懸浮窗。
2. 滑鼠移入懸浮窗，確認暫停與關閉按鈕會正確展開。
3. 點擊暫停後等待 10 秒，確認暫停期間不會跳出提醒視窗。
4. 重新恢復後，確認提醒倒數會從零重新開始，而不是沿用先前進度。
5. 當提醒視窗出現時按下 `Esc`，確認 test 模式下約 5 秒後才再次提醒。
6. 再次觸發提醒後按下 `Enter`，確認全螢幕休息視窗正常顯示並倒數。
7. 在休息視窗中點擊右上角 `✕`，確認可以立即結束，且不會殘留延遲 callback。
8. 在程式已執行時再次啟動，確認單實例提示視窗正常出現。
