import unittest
from unittest import mock

from eyes_protector.i18n import t, set_language, get_system_language, TRANSLATIONS


class TestI18n(unittest.TestCase):
    def setUp(self):
        # Store original language to restore after tests
        from eyes_protector.i18n import _lang
        self.original_lang = _lang

    def tearDown(self):
        # Restore original language state
        import eyes_protector.i18n
        eyes_protector.i18n._lang = self.original_lang

    def test_set_language_sets_supported_languages(self):
        for lang in TRANSLATIONS.keys():
            set_language(lang)
            self.assertEqual(get_system_language(), lang)

    def test_set_language_ignores_invalid_languages(self):
        set_language("zh-TW")
        set_language("invalid-lang-code")
        self.assertEqual(get_system_language(), "zh-TW")

    def test_translation_retrieval(self):
        set_language("en")
        self.assertEqual(t("countdown"), "Every 20 minutes, look 20 feet away for 20 seconds")
        self.assertEqual(t("complete"), "Break complete, ease back into work")
        self.assertEqual(t("warning_text", remaining=5), "Break starting soon (5s remaining) | Click the floating widget to pause")

        set_language("zh-TW")
        self.assertEqual(t("countdown"), "每20分鐘，花20秒鐘，看20呎外")
        self.assertEqual(t("warning_text", remaining=10), "休息即將開始 (還有 10 秒)  |  可點選右下角懸浮球暫停")

        set_language("zh-CN")
        self.assertEqual(t("countdown"), "每20分钟，花20秒钟，看20英尺外")

        set_language("ja")
        self.assertEqual(t("countdown"), "20分ごとに20秒間、20フィート（約6m）先を見ましょう")

        set_language("ko")
        self.assertEqual(t("countdown"), "20분마다 20초 동안 20피트(약 6m) 먼 곳을 바라보세요")

    def test_fallback_language_to_english_on_unknown(self):
        set_language("en")
        import eyes_protector.i18n
        eyes_protector.i18n._lang = "nonexistent-lang"
        # t should fallback to English values
        self.assertEqual(t("countdown"), "Every 20 minutes, look 20 feet away for 20 seconds")

    @mock.patch("ctypes.windll.kernel32.GetUserDefaultUILanguage")
    def test_get_system_language_ctypes_zh_tw(self, mock_get_lang):
        mock_get_lang.return_value = 0x0404  # zh-TW
        import eyes_protector.i18n
        eyes_protector.i18n._lang = None
        self.assertEqual(get_system_language(), "zh-TW")

    @mock.patch("ctypes.windll.kernel32.GetUserDefaultUILanguage")
    def test_get_system_language_ctypes_zh_cn(self, mock_get_lang):
        mock_get_lang.return_value = 0x0804  # zh-CN
        import eyes_protector.i18n
        eyes_protector.i18n._lang = None
        self.assertEqual(get_system_language(), "zh-CN")

    @mock.patch("ctypes.windll.kernel32.GetUserDefaultUILanguage")
    def test_get_system_language_ctypes_ja(self, mock_get_lang):
        mock_get_lang.return_value = 0x0411  # ja
        import eyes_protector.i18n
        eyes_protector.i18n._lang = None
        self.assertEqual(get_system_language(), "ja")

    @mock.patch("ctypes.windll.kernel32.GetUserDefaultUILanguage")
    def test_get_system_language_ctypes_ko(self, mock_get_lang):
        mock_get_lang.return_value = 0x0412  # ko
        import eyes_protector.i18n
        eyes_protector.i18n._lang = None
        self.assertEqual(get_system_language(), "ko")

    @mock.patch("ctypes.windll.kernel32.GetUserDefaultUILanguage")
    def test_get_system_language_ctypes_en(self, mock_get_lang):
        mock_get_lang.return_value = 0x0409  # en-US
        import eyes_protector.i18n
        eyes_protector.i18n._lang = None
        self.assertEqual(get_system_language(), "en")


if __name__ == "__main__":
    unittest.main()
