import json
import tempfile
import unittest
from pathlib import Path

from eyes_protector.config import (
    AppConfig,
    get_default_config_path,
    load_config,
)


class LoadConfigTests(unittest.TestCase):
    def test_loads_test_profile(self):
        config = load_config(["main.py", "--test"])
        self.assertEqual(config.break_interval, 10)
        self.assertEqual(config.snooze_interval, 5)
        self.assertEqual(config.break_duration, 5)
        self.assertEqual(config.idle_threshold, 20)
        self.assertEqual(config.fullscreen_transition_ticks, 1)
        self.assertEqual(config.warning_duration, 5)
        self.assertTrue(config.sound_enabled)
        self.assertIsNone(config.language)

    def test_loads_default_profile(self):
        config = load_config(["main.py"])
        self.assertEqual(config.break_interval, 20 * 60)
        self.assertEqual(config.snooze_interval, 5 * 60)
        self.assertEqual(config.break_duration, 20)
        self.assertEqual(config.idle_threshold, 300)
        self.assertEqual(config.fullscreen_transition_ticks, 2)
        self.assertEqual(config.warning_duration, 10)
        self.assertTrue(config.sound_enabled)
        self.assertIsNone(config.language)

    def test_cli_flags_override(self):
        argv = [
            "main.py",
            "--interval", "1500",
            "--break-seconds", "30",
            "--warning-seconds", "15",
            "--snooze-minutes", "3.5",
            "--mute",
            "--lang", "ja",
        ]
        config = load_config(argv)
        self.assertEqual(config.break_interval, 1500)
        self.assertEqual(config.break_duration, 30)
        self.assertEqual(config.warning_duration, 15)
        self.assertEqual(config.snooze_interval, 210)  # 3.5 * 60
        self.assertFalse(config.sound_enabled)
        self.assertEqual(config.language, "ja")

    def test_cli_flags_clamping(self):
        argv = [
            "main.py",
            "--interval", "1",       # Below min 5
            "--break-seconds", "1000", # Above max 600
            "--warning-seconds", "0",  # Below min 1
            "--snooze-seconds", "9999",# Above max 3600
        ]
        config = load_config(argv)
        self.assertEqual(config.break_interval, 5)
        self.assertEqual(config.break_duration, 600)
        self.assertEqual(config.warning_duration, 1)
        self.assertEqual(config.snooze_interval, 3600)

    def test_loads_json_config(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(
                {
                    "break_interval": 1800,
                    "snooze_interval": 120,
                    "break_duration": 25,
                    "warning_duration": 12,
                    "idle_threshold": 400,
                    "sound_enabled": False,
                    "language": "ko",
                },
                f,
            )
            temp_path = f.name

        try:
            config = load_config(["main.py"], config_path=temp_path)
            self.assertEqual(config.break_interval, 1800)
            self.assertEqual(config.snooze_interval, 120)
            self.assertEqual(config.break_duration, 25)
            self.assertEqual(config.warning_duration, 12)
            self.assertEqual(config.idle_threshold, 400)
            self.assertFalse(config.sound_enabled)
            self.assertEqual(config.language, "ko")

            # CLI flag takes precedence over JSON config
            config_cli_override = load_config(
                ["main.py", "--interval", "2400", "--lang", "zh-TW"],
                config_path=temp_path,
            )
            self.assertEqual(config_cli_override.break_interval, 2400)
            self.assertEqual(config_cli_override.language, "zh-TW")
            self.assertFalse(config_cli_override.sound_enabled)  # Kept from JSON
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_loads_corrupted_json_or_missing_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            f.write("{ invalid json [[]")
            corrupt_path = f.name

        try:
            config = load_config(["main.py"], config_path=corrupt_path)
            self.assertEqual(config.break_interval, 20 * 60)
            self.assertTrue(config.sound_enabled)

            non_existent = Path(corrupt_path).parent / "does_not_exist_98765.json"
            config_missing = load_config(["main.py"], config_path=non_existent)
            self.assertEqual(config_missing.break_interval, 20 * 60)
        finally:
            Path(corrupt_path).unlink(missing_ok=True)

    def test_test_profile_with_mute_and_lang(self):
        config = load_config(["main.py", "--test", "--mute", "--lang", "zh-CN"])
        self.assertEqual(config.break_interval, 10)
        self.assertFalse(config.sound_enabled)
        self.assertEqual(config.language, "zh-CN")

    def test_get_default_config_path(self):
        path = get_default_config_path()
        self.assertIsInstance(path, Path)
        self.assertTrue(str(path).endswith("config.json"))

    def test_extreme_cli_inputs_and_invalid_config_path(self):
        config = load_config(
            [
                "main.py",
                "--config",
                "bad\x00path.json",
                "--snooze-minutes",
                "inf",
                "--interval",
                "not-an-int",
            ]
        )
        self.assertEqual(config.break_interval, 20 * 60)
        self.assertEqual(config.snooze_interval, 5 * 60)

        config_nan = load_config(["main.py", "--snooze-minutes", "nan"])
        self.assertEqual(config_nan.snooze_interval, 5 * 60)

    def test_json_boolean_and_type_coercion_guards(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(
                {
                    "break_interval": True,
                    "sound_enabled": "false",
                    "language": "fr-FR",
                },
                f,
            )
            temp_path = f.name

        try:
            config = load_config(["main.py"], config_path=temp_path)
            self.assertEqual(config.break_interval, 20 * 60)
            self.assertTrue(config.sound_enabled)
            self.assertIsNone(config.language)
        finally:
            Path(temp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
