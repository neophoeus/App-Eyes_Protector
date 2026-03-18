# Changelog

All notable changes to App-Eyes Protector are documented here.

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
