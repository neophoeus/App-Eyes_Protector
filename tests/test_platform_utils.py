import subprocess
import unittest
from unittest import mock

from eyes_protector import platform_utils
from eyes_protector.core import BUSY_REASON_FULLSCREEN, BUSY_REASON_NONE


class PlatformUtilsTests(unittest.TestCase):
    def test_get_platform_busy_reason_uses_notification_state(self):
        with mock.patch(
            "eyes_protector.platform_utils._query_user_notification_state",
            return_value=3,
        ):
            with mock.patch(
                "eyes_protector.platform_utils._foreground_window_covers_monitor",
                return_value=False,
            ):
                self.assertEqual(
                    platform_utils.get_platform_busy_reason(), BUSY_REASON_FULLSCREEN
                )

    def test_get_platform_busy_reason_detects_fullscreen_window_even_with_activity(
        self,
    ):
        with mock.patch(
            "eyes_protector.platform_utils._query_user_notification_state",
            return_value=None,
        ):
            with mock.patch(
                "eyes_protector.platform_utils._foreground_window_covers_monitor",
                return_value=True,
            ):
                self.assertEqual(
                    platform_utils.get_platform_busy_reason(), BUSY_REASON_FULLSCREEN
                )

    def test_get_platform_busy_reason_returns_none_when_not_busy(self):
        with mock.patch(
            "eyes_protector.platform_utils._query_user_notification_state",
            return_value=None,
        ):
            with mock.patch(
                "eyes_protector.platform_utils._foreground_window_covers_monitor",
                return_value=False,
            ):
                self.assertEqual(
                    platform_utils.get_platform_busy_reason(), BUSY_REASON_NONE
                )

    def test_check_single_instance_exits_when_mutex_creation_fails(self):
        root = mock.Mock()
        with mock.patch(
            "eyes_protector.platform_utils.create_single_instance_mutex",
            return_value=(0, 0),
        ):
            with mock.patch(
                "eyes_protector.platform_utils.messagebox.showerror"
            ) as error_mock:
                with self.assertRaises(SystemExit) as exit_info:
                    platform_utils.check_single_instance(root)

        self.assertEqual(exit_info.exception.code, 1)
        root.withdraw.assert_called_once()
        root.attributes.assert_called_once_with("-topmost", True)
        error_mock.assert_called_once()

    def test_get_closable_instance_image_name_returns_none_in_source_mode(self):
        with mock.patch.object(platform_utils.sys, "frozen", False, create=True):
            self.assertIsNone(platform_utils.get_closable_instance_image_name())

    def test_get_closable_instance_image_name_uses_frozen_executable_name(self):
        with mock.patch.object(platform_utils.sys, "frozen", True, create=True):
            with mock.patch.object(
                platform_utils.sys, "executable", r"C:\Apps\EyesProtector.exe"
            ):
                self.assertEqual(
                    platform_utils.get_closable_instance_image_name(),
                    "EyesProtector.exe",
                )

    def test_force_close_existing_instance_skips_when_no_safe_image_name(self):
        with mock.patch(
            "eyes_protector.platform_utils.get_closable_instance_image_name",
            return_value=None,
        ):
            with mock.patch("eyes_protector.platform_utils.subprocess.run") as run_mock:
                self.assertFalse(platform_utils.force_close_existing_instance())
                run_mock.assert_not_called()

    def test_force_close_existing_instance_targets_current_executable_only(self):
        completed = subprocess.CompletedProcess(args=["taskkill"], returncode=0)
        with mock.patch(
            "eyes_protector.platform_utils.get_closable_instance_image_name",
            return_value="EyesProtector.exe",
        ):
            with mock.patch(
                "eyes_protector.platform_utils.subprocess.run", return_value=completed
            ) as run_mock:
                self.assertTrue(platform_utils.force_close_existing_instance())
                run_mock.assert_called_once()
                args = run_mock.call_args.args[0]
                self.assertEqual(
                    args, ["taskkill", "/F", "/IM", "EyesProtector.exe", "/T"]
                )

    def test_check_single_instance_keeps_mutex_on_success(self):
        root = mock.Mock()
        mutex = object()
        with mock.patch(
            "eyes_protector.platform_utils.create_single_instance_mutex",
            return_value=(mutex, 0),
        ):
            platform_utils.check_single_instance(root)

        self.assertIs(root.mutex, mutex)


if __name__ == "__main__":
    unittest.main()
