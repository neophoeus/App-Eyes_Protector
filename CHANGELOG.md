# Changelog

All notable changes to App-Eyes Protector are documented here.

## v3.5 - 2026-07-04

### Optimized
- **I18n Translation Optimizations**: Refined and improved user experience for translations in English, Traditional/Simplified Chinese, Japanese, and Korean.
- **Single-instance Mutex Terminology**: Standardized Mutex error warnings to use proper local terminology (e.g. "二重起動防止", "중복 실행 방지").

### Fixed
- **Chinese Sublanguage Detection**: Resolved a bug in the Windows LCID sublanguage parser to correctly route Hong Kong (`0x03`) and Macau (`0x05`) to `zh-TW`, and Singapore (`0x04`) and Malaysia (`0x06`) to `zh-CN`.

## v3.4 - 2026-07-04

### Added
- **Multi-language Support (i18n)**: Implemented automatic Windows display language detection supporting Simplified Chinese, Japanese, Korean, English, and Traditional Chinese.
- **Dynamic Sizing Adaptations**: Integrated text length measurements to dynamically scale and adjust layout parameters of the floating widget and warning banner card.
- **Headless Unit Testing Support**: Added offline text width calculations allowing the test suite to execute successfully in standard mock environments without a graphical Tk context.

## v3.3 - 2026-07-04

### Added

- **Top Warning Countdown Pill**: Implemented a separate top warning window with 100% solid opacity containing a styled pill-shaped card (thick bright mint-green outline, deep green background, and white text) for a clearer, non-intrusive countdown experience.
- **Redesigned Break Screen**: Overhauled the fullscreen break experience to use a completely solid background (1.0 alpha) and removed the central card to render a spacious, minimalist layout with centered elements.
- **Pixel-based Font Sizing**: Configured text elements to use absolute pixel sizes (negative integers) to bypass Windows double-scaling bugs and prevent text clipping on high-DPI displays.
- **Bilingual Documentation**: Separated README documentation into Traditional Chinese (`README.md`) and English (`README.en.md`) versions.

### Changed

- **Warning Duration**: Reduced default production warning countdown duration from 20 seconds to 10 seconds.
- **Warning Opacity Transition**: Adjusted the main warning overlay to fade from 0.0 to 0.50 opacity instead of 0.15 to 0.85.

### Verification

- Unit tests: `python -m unittest discover -s tests -v`
- Manual smoke test: `python main.py --test`

## v3.2 - 2026-07-01

### Optimized

- **Warning Fading Optimization**: Throttled warning screen opacity updates to 2Hz, reducing Desktop Window Manager (DWM) composition/blending workload, and adjusted the warning timer tick rate to 5Hz.
- **Canvas Rendering Optimization**: Throttled text updates so that the countdown timer digits and warning guide text are refreshed only when the remaining seconds value changes (1Hz).
- **Idle Polling Optimization**: Dynamically decreased background polling rate from 1s to 5s when the user is idle, significantly minimizing CPU wakeups when the user is away from the computer.
- **Unit Tests**: Added `test_idle_state_polling_rate_deceleration` to verify the idle polling deceleration behavior.

### Verification

- Unit tests: `python -m unittest discover -s tests -v`
- Manual smoke test: `python main.py --test`

## v3.1 - 2026-07-01

### Added

- **Command Line Help Support**: Added support for `-h` and `--help` CLI flags to print usage instructions directly to standard output and exit safely without initiating GUI components.
- **App Startup Unit Tests**: Added unit testing suite (`tests/test_app.py`) to verify parameter parsing and successful initializations.

### Verification

- Unit tests: `python -m unittest discover -s tests -v`
- Manual smoke test: `python main.py --help`

## v3.0 - 2026-07-01

### Added

- **Pre-break Fading Warning Overlay**: A non-interactive, click-through full-screen overlay that starts at 5% opacity and fades to 85% opacity over a warning duration (20 seconds), giving you ample time to finish typing or clicking before the break starts.
- **Click-Through Window Integration**: Added Windows native API support (`WS_EX_TRANSPARENT | WS_EX_LAYERED`) to make the warning window completely pass clicks and keyboard events to underlying applications.
- **Low-Power Circular Progress Ring**: A clean mint-green circular progress ring drawn on the canvas that ticks at 1Hz (once per second) during warning (filling up) and rest break (draining down).
- **Forest Dark Mode (森林暗色模式)**: Overhauled the entire visual layout with a sleek forest dark green theme (`#0d130f` background and `#16201a` cards) to minimize screen emission and reduce eye strain.
- **Fading Pause Control**: The floating widget remains fully visible and interactive during the warning phase, enabling users to click "Pause" to instantly dismiss the warning and pause protection.

### Removed

- The intrusive `CenterReminderDialog` that grabbed focus and interrupted active keyboard typing or mouse clicking.

### Changed

- Re-themed the floating widget with dark translucent forest colors, utilizing mint-green accents for protecting state and amber for paused state.
- Enclosed the countdown timer and guide text in a beautifully centered container card on the fullscreen break view.
- Redesigned the full-screen layout to scale responsively based on monitor dimensions, supporting 4K resolutions with grand proportions, matching fonts, and large rounded corners (8% of card height).
- Upgraded pre-break warning fade-in animation from 1Hz to 10Hz for buttery-smooth transitions.
- Fixed a Win32 API pointer size truncation issue on 64-bit Windows, ensuring click-through works reliably.
- Pre-mapped the Toplevel window during initialization to force wrapper handle creation, resolving the click-through race condition on the first warning.
- Re-aligned and updated the test suite to verify the `STATE_WARNING` transitions and ensure zero regressions.

### Verification

- Unit tests: `python -m unittest discover -s tests -v`
- Manual smoke test: `python main.py --test`

## v2.1 - 2026-06-05

### Added

- A feature to trigger a 20-second break immediately by clicking the open eye icon in the floating widget.
- Comprehensive unit tests covering the immediate break trigger on the floating widget's eye icon, as well as when the eye is closed or when clicking outside.
- Hardened unit tests covering user decisions in the single-instance resolution prompt (User chooses "Yes" with successful or failed close, and user chooses "No").

### Changed

- Enhanced the floating widget's hover expand/collapse mechanism to physically resize the window geometry (between collapsed 44px and expanded width) and slide it horizontally, ensuring the window positions properly against screen edges without clipping.
- Added boundary checks during floating widget dragging to prevent it from being moved off-screen.
- Added post-drag DPI self-adaptation to dynamically scale the floating widget's metrics, canvas size, background shapes, fonts, and controls when moved across displays of different DPIs.
- Excluded the current process PID from `taskkill` filter during single instance resolution to avoid self-termination when checking/closing older instances.
- Updated the VSCode workspace settings with organized imports on save, default formatting, basic type checking mode, and temporary folder exclusions.
- Updated `build.bat` build script to locate python interpreter within local `.venv` subdirectory.

### Verification

- Unit tests: `python -m unittest discover -s tests -v`
- Manual smoke test: `EyesProtector.exe --test`

## v2.0 - 2026-04-06

### Added

- Windows DPI awareness bootstrap and DPI geometry helpers were added so the reminder dialog and floating widget can render sharply on 4K displays while keeping their apparent on-screen size close to the previous behavior.
- Lightweight UI geometry smoke tests were added to cover DPI scaling helpers, reminder dialog sizing, floating widget geometry, and the full-screen card layout.
- Controller and platform utility tests were expanded to cover DPI bootstrap fallback, full-screen break startup rollback, and the hardened quit flow.

### Changed

- The full-screen break page was redesigned around a large centered countdown with guide, completion, and interruption copy placed directly beneath it on a minimalist static backdrop.
- The full-screen break experience was simplified into a calmer matcha-toned canvas with a softer early-exit hover chip and lower visual noise.
- The floating widget now uses refreshed canvas-drawn eye, pause/play, and close controls instead of emoji-style glyph rendering.
- The moving leaf animation was removed entirely, lowering break-screen power usage and leaving a static calm backdrop.
- The top-right early-exit affordance on the full-screen break page is now a clearer close chip instead of a lone text glyph.

### Fixed

- Starting a full-screen break now restores the prior runtime state and floating-widget visibility if the break window fails to initialize.
- App shutdown now ignores repeated quit requests and hides all windows before deferred destruction, avoiding Tk teardown races and orphaned UI.

### Verification

- Unit tests: `python -m unittest discover -s tests -v`
- Manual smoke test: `EyesProtector.exe --test`

## v1.8 - 2026-03-19

### Added

- Busy-reason handling now distinguishes between idle absence and full-screen focus, allowing the reminder timer to apply different pause behavior depending on the situation.
- Full-screen transition debounce was added so reminder timing does not jitter when videos, presentations, or full-screen apps enter and leave focus.
- Core, controller, config, and platform utility tests were expanded to cover busy-reason classification and the new debounce flow.

### Changed

- Idle inactivity now resets elapsed reminder time, while full-screen playback or presentation mode freezes the elapsed time instead of clearing it.
- The full-screen break page now uses a cleaner two-column layout, with the 20-20-20 rule on the left and a large countdown display on the right.
- Break animation resource usage was reduced by simplifying leaf geometry, lowering the animation rate to 8 FPS, fixing the leaf count at six, and slightly enlarging each leaf for readability.
- README was updated to reflect the new stop-timer strategy and the simplified full-screen break experience.

### Verification

- Automated tests: `python -m pytest`
- Manual smoke test: `EyesProtector.exe --test`

## v1.7 - 2026-03-18

### Added

- Full-screen foreground window detection now pauses reminder timing during video playback or presentations even when input activity continues.
- Controller scheduling tests were added to cover pause, snooze, break start, break finish, and quit flows.
- Platform utility tests were added for full-screen busy detection, mutex creation failure handling, and safe instance shutdown behavior.

### Changed

- Reminder polling now stops while paused, while the reminder dialog is open, and during a full-screen break, reducing unnecessary background wakeups.
- Floating widget action clicks now use canvas hit-testing instead of fixed x-coordinate ranges.
- Floating widget collapse behavior now uses delayed pointer re-checking to reduce hover flicker around window edges.
- README documentation was updated to reflect the new full-screen playback and presentation pause behavior.

### Fixed

- Single-instance forced shutdown no longer targets generic executable names such as `main.exe`; it only targets the packaged executable when it is safe to do so.
- Single-instance mutex creation failures now show an explicit error dialog and exit cleanly.

### Verification

- Unit tests: `python -m unittest discover -s tests -v`
- Manual smoke test: `EyesProtector.exe --test`

---

# 版本紀錄

App-Eyes Protector 的重要變更統一記錄於此。

## v3.0 - 2026-07-01

### 新增

- **漸進式無干擾全螢幕預警**：當護眼時間到時，會先以 5% 的不透明度漸漸顯現，並在 20 秒內慢慢加深至 85%。此預警視窗完全「滑鼠穿透」（Click-through）且不搶奪焦點，讓您能不受干擾地完成正在輸入的字句或點選的按鈕。
- **滑鼠穿透視窗技術**：整合 Windows 原生 API（`WS_EX_TRANSPARENT | WS_EX_LAYERED`），使透明預警畫面可以將所有點擊與按鍵事件傳遞至下方的應用程式。
- **超低功耗環形進度條**：在卡片中央繪製薄荷綠的環形進度條，僅在每秒計時更新時重繪（1Hz 頻率）。預警時順時針填滿，休息時逆時針消退。
- **森林暗色模式（Forest Dark Mode）**：全面換上極低功耗且護眼的深森林綠背景（`#0d130f`）與深綠卡片（`#16201a`），降低螢幕亮度與眼部負擔。
- **預警快速中斷**：預警期間右下角懸浮球依然保持顯示，您可隨時點選「暫停」以立即關閉預警畫面。

### 移除

- 移除原先會突然搶佔焦點與鍵盤輸入、打斷打字點選的中央提醒對話框（`CenterReminderDialog`）。

### 調整

- 將懸浮視窗調整為半透明深綠森林風格，保護中顯示薄荷綠，暫停中顯示溫馨琥珀色。
- 全螢幕休息畫面中的倒數與護眼指引文字，現在被收納在視覺層次更精美的中央圓角卡片中。
- 重新設計全螢幕版面為響應式自適應比例，支援 4K 螢幕大尺寸卡片、大圓角（卡片高度 8%）與等比例字型。
- 將預警畫面的漸變更新頻率從 1Hz 提升至 10Hz，帶來絲滑柔和的動畫效果。
- 修正 64 位元 Windows 系統下的 Win32 API 指標長度截斷問題，確保滑鼠穿透 100% 穩定生效。
- 程式啟動時預先映射（Pre-map）全螢幕視窗，強制系統建立外框控制代碼，徹底解決第一次預警時穿透樣式因異步載入而失效的問題。
- 更新單元測試套件以符合 `STATE_WARNING` 的新流程與懸浮窗狀態。

### 驗證

- 單元測試：`python -m unittest discover -s tests -v`
- 手動 smoke test：`python main.py --test`

## v2.1 - 2026-06-05

### 新增

- 新增點擊懸浮視窗「睜開的眼睛圖示」可立即啟動 20 秒大休息的功能。
- 新增針對懸浮視窗眼睛圖示點擊的單元測試（包含點擊睜開的眼睛啟動休息、點擊閉上的眼睛不啟動，以及點擊眼睛外部區域等場景）。
- 新增單實例提示視窗處理邏輯的完整單元測試（包含使用者選擇「是」以關閉舊實例的成功/失敗路徑，以及使用者選擇「否」的路徑）。

### 調整

- 優化懸浮視窗收合與展開的幾何調整機制，實際切換視窗寬度（於收合 44px 與展開寬度之間）並在靠右時進行水平滑動位移，避免展開時超出螢幕或收合時位移不正確。
- 新增懸浮視窗拖曳時的螢幕邊界檢查，防止視窗被拖曳出螢幕範圍。
- 新增懸浮視窗拖曳釋放後的 DPI 自適應更新，當跨螢幕拖曳導致 DPI 改變時，動態更新縮放幾何、背景、字型、按鈕 Hitbox 等。
- 強化單實例檢查的強制關閉邏輯，在 `taskkill` 時排除當前進程 PID，避免新啟動的實例誤殺自己。
- 更新 `.vscode/settings.json` 以支援存檔自動排版、自動整理 Import、基礎型別檢查與排除打包暫存目錄。
- 更新 `build.bat` 打包腳本，使其能優先尋找本地目錄下的 `.venv` Python 解譯器。

### 驗證

- 單元測試：`python -m unittest discover -s tests -v`
- 手動 smoke test：`EyesProtector.exe --test`

## v2.0 - 2026-04-06

### 新增

- 新增 Windows DPI awareness 啟動流程與 DPI 幾何 helper，讓提醒視窗與懸浮視窗在 4K 螢幕上能以更清晰的原生解析度呈現，同時維持接近原本的視覺尺寸。
- 新增輕量級 UI 幾何 smoke tests，覆蓋 DPI 縮放 helper、提醒視窗尺寸、懸浮視窗幾何與全螢幕卡片版面計算。
- 擴充 controller 與 platform utility 測試，補上 DPI 啟動 fallback、全螢幕休息啟動失敗回滾與退出流程強化的覆蓋。

### 調整

- 全螢幕休息頁改為中央大倒數，並將提醒說明、完成後文字與提早中斷文字統一放在倒數下方，形成更極簡的全螢幕構圖。
- 全螢幕休息體驗進一步簡化為更安靜的抹茶色靜態背景，並搭配更柔和的提早結束 hover 圓形按鈕，降低視覺噪音。
- 懸浮窗改為重新繪製的 canvas 眼睛圖示與 pause/play、close 控制元件，不再依賴 emoji 風格符號。
- 直接移除落葉動態背景，改用靜態且更省電的休息頁背景。
- 全螢幕右上角的提早結束入口改為更清楚的 close chip，不再只顯示單一文字符號。

### 修正

- 若全螢幕休息視窗初始化失敗，現在會正確回復先前 runtime 狀態與懸浮窗可見性，不會卡在半進入休息的中間狀態。
- 退出程式時現在會忽略重複 quit 請求，並先隱藏所有視窗再延後銷毀，避免 Tk 關閉競態與殘留視窗。

### 驗證

- 單元測試：`python -m unittest discover -s tests -v`
- 手動 smoke test：`EyesProtector.exe --test`

## v1.8 - 2026-03-19

### 新增

- 新增 busy 原因分類，區分「離席」與「全螢幕專注」，讓提醒倒數可依情境採用不同停表策略。
- 新增全螢幕進出場 debounce，避免影片、簡報或全螢幕應用切換時造成計時抖動。
- 擴充 core、controller、config 與 platform utility 測試，覆蓋 busy 原因分流與 debounce 流程。

### 調整

- 使用者離席時，提醒累積時間會歸零；全螢幕播放或簡報時，則改為凍結目前進度，不再直接清空。
- 全螢幕休息頁改為更乾淨的左右雙欄版面，左側顯示 20-20-20 規則，右側以大字倒數為主視覺。
- 休息動畫改為更省資源的設定，包含簡化葉片幾何、降為 8 FPS、固定 6 片葉子，並微幅放大葉片提升可讀性。
- README 已同步更新新的停表策略與全螢幕休息體驗說明。

### 驗證

- 自動化測試：`python -m pytest`
- 手動 smoke test：`EyesProtector.exe --test`

## v1.7 - 2026-03-18

### 新增

- 新增前景全螢幕視窗判定，播放全螢幕影片或進入簡報時，即使仍有滑鼠或鍵盤活動也會停止倒數。
- 新增 controller 排程測試，覆蓋暫停、稍後提醒、開始休息、結束休息與退出流程。
- 新增平台層測試，覆蓋全螢幕 busy 判定、mutex 建立失敗處理，以及安全關閉既有實例行為。

### 調整

- 倒數輪詢在暫停中、提醒視窗顯示中與全螢幕休息中會停止，減少不必要的背景喚醒。
- 懸浮窗按鈕點擊改為使用 canvas 實際命中判定，不再依賴固定 x 座標範圍。
- 懸浮窗收合改為延遲後再次檢查指標位置，降低邊界閃動與誤收合。
- README 已同步更新全螢幕播放與簡報模式會暫停倒數的說明。

### 修正

- 單實例強制關閉不再對 `main.exe` 之類的泛用程序名執行 `taskkill`，只會在安全情況下針對打包後執行檔處理。
- 單實例 mutex 建立失敗時，現在會顯示明確錯誤訊息並安全退出。

### 驗證

- 單元測試：`python -m unittest discover -s tests -v`
- 手動 smoke test：`EyesProtector.exe --test`
