import io
import sys
import unittest
from unittest import mock

from eyes_protector.app import main


class TestAppCLI(unittest.TestCase):
    def test_help_flag_long(self):
        stdout_mock = io.StringIO()
        with mock.patch("sys.stdout", stdout_mock):
            with self.assertRaises(SystemExit) as cm:
                main(["main.py", "--help"])

        self.assertEqual(cm.exception.code, 0)
        output = stdout_mock.getvalue()
        self.assertIn("App-Eyes Protector", output)
        self.assertIn("--test", output)
        self.assertIn("--help", output)
        self.assertIn("--interval", output)
        self.assertIn("--mute", output)
        self.assertIn("--lang", output)

    def test_help_flag_short(self):
        stdout_mock = io.StringIO()
        with mock.patch("sys.stdout", stdout_mock):
            with self.assertRaises(SystemExit) as cm:
                main(["main.py", "-h"])

        self.assertEqual(cm.exception.code, 0)
        output = stdout_mock.getvalue()
        self.assertIn("App-Eyes Protector", output)

    @mock.patch("eyes_protector.app.enable_high_dpi_mode")
    @mock.patch("eyes_protector.app.check_single_instance")
    @mock.patch("eyes_protector.app.EyesProtectorController")
    @mock.patch("tkinter.Tk")
    def test_normal_startup(self, mock_tk, mock_controller, mock_check, mock_dpi):
        mock_root = mock.MagicMock()
        mock_tk.return_value = mock_root

        main(["main.py"])

        mock_dpi.assert_called_once()
        mock_tk.assert_called_once()
        mock_root.withdraw.assert_called_once()
        mock_check.assert_called_once_with(mock_root)
        mock_controller.assert_called_once()
        mock_root.mainloop.assert_called_once()

    @mock.patch("eyes_protector.app.set_language")
    @mock.patch("eyes_protector.app.enable_high_dpi_mode")
    @mock.patch("eyes_protector.app.check_single_instance")
    @mock.patch("eyes_protector.app.EyesProtectorController")
    @mock.patch("tkinter.Tk")
    def test_language_applied_from_cli_before_single_instance_check(
        self, mock_tk, mock_controller, mock_check, mock_dpi, mock_set_lang
    ):
        call_order = []
        mock_set_lang.side_effect = lambda code: call_order.append(("set_language", code))
        mock_check.side_effect = lambda root: call_order.append(("check_single_instance", root))
        mock_root = mock.MagicMock()
        mock_tk.return_value = mock_root

        main(["main.py", "--lang", "ko"])

        mock_set_lang.assert_called_once_with("ko")
        self.assertEqual(
            call_order,
            [("set_language", "ko"), ("check_single_instance", mock_root)],
        )


if __name__ == "__main__":
    unittest.main()
