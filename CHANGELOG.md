# Changelog

All notable changes to App-Eyes Protector are documented here.

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
