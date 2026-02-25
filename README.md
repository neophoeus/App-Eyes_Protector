# App-Eyes Protector

[English](#english) | [繁體中文](#繁體中文)

---

## English

A highly lightweight, zero-dependency, immersive eye protection assistant for Windows.

> **What is the 20-20-20 Rule?**  
> It is a golden rule recommended by the American Academy of Ophthalmology (AAO) and professional doctors: **"Every 20 minutes spent using a screen, you should try to look away at something that is 20 feet away from you for a total of 20 seconds."**
>
> This app is specifically designed based on this medical principle, providing you with a stress-free, natural, and smooth 20-second break guidance to effectively soothe ciliary muscle fatigue and prevent Digital Eye Strain (DES).

### 💡 Core Highlights

1. **High-Quality Undisturbed Persistence**: Automatically hides in the background. Only a high-quality "semi-transparent rounded rectangular eye" floating widget stays in the corner of the screen. Hovering the mouse allows you to quickly and safely exit without forcibly interrupting your workflow.
2. **Rendering Aesthetics, Immersive Relaxation**: Discarding traditional rigid static images, it uses pure mathematical calculations to generate 3D geometric falling leaves and breeze animations, creating a 20-second breathing moment where "your heartbeat slows down with the screen".
3. **Green & Lightweight, Ready to Use**: Zero external package dependencies, no installation required. It consists of a single Python executable (.exe) that purely calls Windows native APIs, along with simple startup/shutdown scripts.

### ⚙️ Technical Principles

* **Environment Detection**: Intelligently determines whether the user is in full-screen gaming, watching a video, or sleeping mode by directly calling the Windows underlying native API (`ctypes.windll.shell32.SHQueryUserNotificationState`) to avoid any disruption.
* **Rendering Engine**: Zero image file dependencies, entirely built using the Python `tkinter.Canvas` native drawing tool. It combines mathematical geometry (trigonometric functions and random variables) to construct falling leaf polygons and features a pure-code-rendered high-quality transparent floating UI.
* **Ultra-Lightweight Deployment**: Discards all external third-party packages (such as Pillow, Pystray) and uses PyInstaller to package into a single background executable (`EyesProtector.exe`), paired with BAT batch scripts for easy auto-startup on boot and uninstallation.

### 🚀 Quick Start

#### Get the Executable

This project has been compiled into a single portable executable using PyInstaller. You can find `EyesProtector.exe` directly in the `dist` folder.

#### Set Up Auto-Startup on Boot

* **Enable Auto-Protection**: Double-click `setup_startup.bat` to automatically add it to your Windows startup items.
* **Disable Auto-Protection**: Double-click `remove_startup.bat` to easily remove it.

#### Manual Testing and Operation

* **Test Animation Effects**: You can run `EyesProtector.exe --test` from the terminal to immediately test the 10-second reminder and 5-second break.
* **Interrupt Break**: When the full-screen leaves are falling, if you urgently need to return to work, click the `✕` symbol in the top-right corner to end the break early and return to background timing.
* **Exit Program**: To completely close the eye protection assistant, move your mouse over the "semi-transparent eye floating widget" in the bottom-right corner and click the red `✕` on the expanded panel to safely end it.

### 🛠️ Development and Building

If you want to modify the source code and recompile it yourself, ensure you have Python 3 installed, and run the build script in the root directory:

```bash
pip install pyinstaller
.\build.bat
```

After the build is complete, the latest executable `EyesProtector.exe` will be generated in the `dist` directory.

---

## 繁體中文

一款極輕量、零依賴的 Windows 沉浸式護眼助理。

> **什麼是 20-20-20 護眼法則？**  
> 這是由美國眼科醫學會（AAO）與專業醫師廣泛推廣的黃金護眼指南：**「每使用螢幕 20 分鐘，就把視線移開看 20 呎（約 6 公尺）遠的物體，持續 20 秒鐘。」**
>
> 本應用程式正是基於此醫學原理量身打造，為您提供無壓力、最自然流暢的 20 秒休息引導，有效舒緩睫狀肌疲勞並預防數位眼疲勞症候群（DES）。

### 💡 核心亮點

1. **高質感無擾常駐**：平時自動隱藏於系統背景，僅在畫面角落常駐一顆高質感的「半透明方形圓角眼睛」懸浮窗格，滑鼠移入即可快速安全退出，不強暴中斷您的工作心流。
2. **算繪美學，沉浸放鬆**：捨棄傳統呆板的靜態圖，運用純數學運算生成 3D 幾何落葉與微風動畫，打造 20 秒「心跳跟著畫面慢下來」的呼吸時刻。
3. **綠色輕量，隨開即用**：零外部套件依賴、免安裝。由一支純粹呼叫 Windows 原生 API 的 Python 單一執行檔 (.exe) 與簡易的開關腳本構成。

### ⚙️ 技術原理

* **環境偵測**：透過直接呼叫 Windows 底層原生 API (`ctypes.windll.shell32.SHQueryUserNotificationState`)，智慧判斷使用者是否處於全螢幕遊戲、看影片或休眠狀態，避免干擾。
* **渲染引擎**：零圖檔依賴，完全使用 Python `tkinter.Canvas` 原生繪圖工具。結合數學幾何（三角函數與隨機變數）建構落葉多邊形，並具備純代碼渲染的高質感去背懸浮 UI。
* **極輕量部署**：捨棄所有外部第三方套件（如 Pillow、Pystray），並透過 PyInstaller 打包為單一背景執行檔 (`EyesProtector.exe`)，搭配 BAT 批次腳本達成簡易的開機自動啟動與卸載。

### 🚀 快速上手

#### 取得執行檔

本專案已透過 PyInstaller 編譯為單一免安裝執行檔。您可以直接在 `dist` 資料夾中找到 `EyesProtector.exe`。

#### 設定開機自動啟動

* **開啟自動保護**：點擊兩下 `setup_startup.bat`，即可自動將其加入 Windows 開機啟動項目。
* **取消自動保護**：點擊兩下 `remove_startup.bat` 即可輕鬆解除。

#### 手動測試與操作

* **測試動畫效果**：您可以從終端機執行 `EyesProtector.exe --test` 來立即測試 10 秒提醒與 5 秒休息。
* **中斷休息**：當全螢幕樹葉飄落時，若需緊急回到工作，點擊畫面右上角的 `✕` 符號即可提早結束本次休息並退回背景計時。
* **退出程式**：若欲完全關閉護眼助理，請對著畫面右下角的「半透明眼睛懸浮窗格」移入滑鼠，點擊展開面板上的紅色 `✕` 即可安全結束常駐。

### 🛠️ 開發與編譯

如果您想自行修改原始碼並重新編譯，請確認您已安裝 Python 3，並執行根目錄下的打包腳本：

```bash
pip install pyinstaller
.\build.bat
```

編譯完成後，最新的執行檔 `EyesProtector.exe` 將會產生在 `dist` 目錄下。
