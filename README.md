# App-Eyes Protector

[English] | [繁體中文](README.zh-TW.md)

---

A highly lightweight, zero-dependency, immersive eye protection assistant for Windows.

**Latest Release:** v3.3  
**Release Notes:** See [CHANGELOG.md](CHANGELOG.md)

> **What is the 20-20-20 Rule?**  
> It is a golden rule recommended by the American Academy of Ophthalmology (AAO) and professional doctors: **"Every 20 minutes spent using a screen, you should try to look away at something that is 20 feet away from you for a total of 20 seconds."**
>
> This app is specifically designed based on this medical principle, providing you with a stress-free, natural, and smooth 20-second break guidance to soothe ciliary muscle fatigue and prevent Digital Eye Strain (DES).

### 💡 Core Highlights

1. **High-Quality Undisturbed Persistence**: Automatically hides in the background. Only a high-quality "semi-transparent rounded rectangular eye" floating widget stays in the corner of the screen. Hovering the mouse allows you to quickly and safely pause or exit without forcibly interrupting your workflow.
2. **Minimalist Top Banner Warning**: Instead of an intrusive center popup or fullscreen blocking during countdown, the screen dims gently from 0% to 50% opacity over **10 seconds**. A solid, clean pill-shaped warning card (thick bright mint-green outline, deep green background, and sharp white text) is displayed at the top center of the screen. It is fully click-through (`WS_EX_TRANSPARENT | WS_EX_LAYERED`), minimizing distraction so you can finish active tasks uninterrupted.
3. **Solid Background Break Screen**: Once the 10-second warning ends, the app transitions to the actual 20-second break with a **100% solid opacity background** (no transparency/dimming). The central card has been completely removed to provide a spacious fullscreen layout featuring a large centered progress ring, digital timer, and clean AAO guidance text.
4. **Green & Lightweight, Ready to Use**: Zero external package dependencies, no installation required. It consists of a single Python executable (.exe) that purely calls Windows native APIs, along with simple startup/shutdown scripts.
5. **Forest Dark Mode & Low-Power Circular Progress**: Overhauled with a premium dark forest green theme (`#0d130f` background and `#113d23` cards) to minimize screen emission. Includes a clean circular progress ring that ticks at 1Hz (once per second) during countdowns. Elements scale dynamically to monitor size, using native Windows DPI awareness for sharper 4K rendering.

### ⚙️ Technical Principles

- **Environment Detection & Power Friendly**: Intelligently determines whether the user is in full-screen gaming, watching a video, or presenting by combining Windows native API (`SHQueryUserNotificationState`), foreground full-screen window detection, and hardware input monitoring (`GetLastInputInfo`). Even if the mouse is still moving, full-screen playback or presentation mode will pause reminder timing. Moreover, it boasts an ultra-optimized event loop that **will not prevent Windows from automatically turning off the display or entering sleep mode**.
- **Reason-Aware Reminder Freeze**: The timer now distinguishes between idle absence and full-screen focus. Idle resets the elapsed reminder time, while full-screen playback or presentation freezes the timer in place and uses transition debounce to avoid jitter when entering or leaving full-screen mode.
- **Smart Pause**: Need absolute focus? Just unfold the widget and click the canvas-drawn pause control. The eye protector icon will smoothly transition into a canvas-drawn "closed eye" indicator, and the timer will freeze. Resuming the timer will automatically start counting from zero, keeping the flow going naturally.
- **Rendering Engine**: Zero image file dependencies, entirely built using the Python `tkinter.Canvas` native drawing tool. Fonts are configured using pixel-based units (negative integer sizing) to bypass Windows double-scaling bugs and render sharply alongside the canvas on 4K displays.
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
5. When the fading warning starts, verify that the screen dims from 0% to 50% opacity and displays a solid, bright green bordered pill banner at the top center showing remaining seconds, and check that you can click and type behind the overlay.
6. Verify that after warning counts down to 0, the screen transitions to a completely solid (100% alpha) background with a large centered progress ring and no central card.
7. During the break, click the top-right close chip and confirm the break ends immediately without delayed follow-up callbacks.
8. Relaunch the app while it is already running and confirm the single-instance prompt appears.
9. Open the floating widget and click the close control; confirm the app exits cleanly without orphaned windows or repeated shutdown prompts.
