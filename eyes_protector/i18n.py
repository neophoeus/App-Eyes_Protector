import ctypes
import locale

_lang = None


def get_system_language():
    global _lang
    if _lang is not None:
        return _lang

    # 1. Try Windows API via ctypes for UI language
    try:
        lcid = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        primary_lang = lcid & 0x3ff
        if primary_lang == 0x04:  # Chinese
            sublang = lcid >> 10
            if sublang in (0x02, 0x04, 0x06):  # zh-CN (0x02), zh-SG (0x04), zh-MY (0x06)
                _lang = "zh-CN"
            else:
                _lang = "zh-TW"
        elif primary_lang == 0x11:  # Japanese
            _lang = "ja"
        elif primary_lang == 0x12:  # Korean
            _lang = "ko"
        elif primary_lang == 0x09:  # English
            _lang = "en"
        if _lang:
            return _lang
    except Exception:
        pass

    # 2. Fallback to standard Python locale
    try:
        lang, _ = locale.getlocale()
        if not lang:
            lang, _ = locale.getdefaultlocale()
        if lang:
            lang = lang.lower()
            if "zh_cn" in lang or "chinese_china" in lang or "hans" in lang:
                _lang = "zh-CN"
            elif "zh" in lang or "chinese" in lang:
                _lang = "zh-TW"
            elif "ja" in lang or "japanese" in lang:
                _lang = "ja"
            elif "ko" in lang or "korean" in lang:
                _lang = "ko"
    except Exception:
        pass

    if _lang is None:
        _lang = "en"  # Default to English
    return _lang


def set_language(lang_code):
    global _lang
    if lang_code in TRANSLATIONS:
        _lang = lang_code


TRANSLATIONS = {
    "zh-TW": {
        "countdown": "每20分鐘，花20秒鐘，看20英尺 (約6公尺) 外",
        "complete": "休息已完成，放鬆回到工作",
        "skipped": "已返回工作，稍後將再次提醒",
        "warning_text": "休息即將開始 (剩餘 {remaining} 秒)  |  可點選右下角懸浮球暫停",
        "paused": "已暫停",
        "protecting": "保護中",
        "err_mutex": "無法建立單一執行個體鎖定，程式即將結束。\n請稍後再試，或重新啟動 Windows 後再執行。",
        "ask_force_close": "護眼助理目前正在背景進行倒數計時。\n\n您想要完全「強制關閉」此程式嗎？\n(按「是」將會結束常駐保護)",
        "info_manual_close": "目前僅支援在打包執行檔 (.exe) 模式下自動關閉既有執行個體。\n請手動結束舊的護眼程式後再重新啟動。",
    },
    "zh-CN": {
        "countdown": "每20分钟，花20秒钟，看20英尺 (约6米) 外",
        "complete": "休息已完成，轻松回到工作",
        "skipped": "已返回工作，稍后将再次提醒",
        "warning_text": "休息即将开始 (剩余 {remaining} 秒)  |  可点击右下角悬浮球暂停",
        "paused": "已暂停",
        "protecting": "保护中",
        "err_mutex": "无法建立单实例锁定，程序即将结束。\n请稍后再试，或重新启动 Windows 后再运行。",
        "ask_force_close": "护眼助理正在后台为您倒计时。\n\n您确定要完全“强制关闭”此软件吗？\n(点击“是”将结束常驻保护)",
        "info_manual_close": "目前仅支持在打包可执行文件 (.exe) 模式下自动关闭已有实例。\n请手动结束旧的护眼程序后再重新启动。",
    },
    "ja": {
        "countdown": "20分ごとに20秒間、20フィート（約6m）先を見ましょう",
        "complete": "休憩が完了しました。ゆっくりと業務に戻りましょう",
        "skipped": "作業を再開しました。しばらくしてからまた通知します。",
        "warning_text": "まもなく休憩が始まります（残り {remaining} 秒） | 右下のフローティングボタンで一時停止できます",
        "paused": "一時停止中",
        "protecting": "保護中",
        "err_mutex": "二重起動防止用のロックを作成できないため、プログラムを終了します。\nしばらく待ってから再試行するか、Windowsを再起動してから再度実行してください。",
        "ask_force_close": "アイプロテクターはバックグラウンドで稼働（カウントダウン）中です。\n\nこのソフトを完全に「強制終了」しますか？\n（「はい」をクリックすると常駐保護が終了します）",
        "info_manual_close": "現在、パッケージ化された実行可能ファイル（EXE）モードでのみ、既存プロセスの自動終了に対応しています。\n古いアイプロテクターを手動で終了してから再起動してください。",
    },
    "ko": {
        "countdown": "20분마다 20초 동안 20피트(약 6m) 먼 곳을 바라보세요",
        "complete": "휴식이 완료되었습니다. 편안한 마음으로 업무에 복귀하세요.",
        "skipped": "업무에 복귀했습니다. 잠시 후 다시 알림이 제공됩니다.",
        "warning_text": "잠시 후 휴식이 시작됩니다({remaining}초 남음) | 우측 하단 플로팅 버튼으로 일시 중지할 수 있습니다",
        "paused": "일시 중지됨",
        "protecting": "보호 중",
        "err_mutex": "중복 실행 방지 잠금을 생성할 수 없어 프로그램을 종료합니다.\n잠시 후 다시 시도하거나 Windows를 재부팅한 후 실행해 주세요.",
        "ask_force_close": "눈 보호 도우미가 백그라운드에서 작동 중입니다.\n\n이 프로그램을 완전히 '강제 종료'하시겠습니까?\n('예'를 누르면 상주 보호가 해제됩니다)",
        "info_manual_close": "현재 패키징된 실행 파일(.exe) 모드에서만 기존 실행 인스턴스를 자동으로 종료할 수 있습니다.\n기존 눈 보호 프로그램을 수동으로 종료한 후 다시 실행해 주세요.",
    },
    "en": {
        "countdown": "Every 20 minutes, look 20 feet (about 6m) away for 20 seconds",
        "complete": "Break complete, ease back to work.",
        "skipped": "Returned to work. We will remind you later.",
        "warning_text": "Break starting soon ({remaining}s remaining) | Click the floating widget to pause",
        "paused": "Paused",
        "protecting": "Protecting",
        "err_mutex": "Failed to create a single-instance lock. The program will exit.\nPlease try again later or restart Windows.",
        "ask_force_close": "Eyes Protector is currently active in the background.\n\nDo you want to completely force close this program?\n(Clicking 'Yes' will exit background protection)",
        "info_manual_close": "Automatically closing existing instances is only supported in packaged executable (.exe) mode.\nPlease manually close the running instance and try again.",
    },
}


def t(key, **kwargs):
    lang = get_system_language()
    val = TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(
        key, TRANSLATIONS["en"].get(key, "")
    )
    if kwargs:
        return val.format(**kwargs)
    return val
