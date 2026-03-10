import unittest

from eyes_protector.config import load_config


class LoadConfigTests(unittest.TestCase):
    def test_loads_test_profile(self):
        config = load_config(["main.py", "--test"])
        self.assertEqual(config.break_interval, 10)
        self.assertEqual(config.snooze_interval, 5)
        self.assertEqual(config.break_duration, 5)
        self.assertEqual(config.idle_threshold, 20)

    def test_loads_default_profile(self):
        config = load_config(["main.py"])
        self.assertEqual(config.break_interval, 20 * 60)
        self.assertEqual(config.snooze_interval, 5 * 60)
        self.assertEqual(config.break_duration, 20)
        self.assertEqual(config.idle_threshold, 300)


if __name__ == "__main__":
    unittest.main()
