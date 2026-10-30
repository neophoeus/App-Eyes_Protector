import subprocess
import unittest
from unittest import mock

from eyes_protector import platform_utils
from eyes_protector.core import (
    BUSY_REASON_FULLSCREEN,
    BUSY_REASON_IDLE,
    BUSY_REASON_NONE,
)


class PlatformUtilsTests(unittest.TestCase):
    def test_enable_high_dpi_mode_prefers_per_monitor_v2(self):
        with mock.patch(
            "eyes_protector.platform_utils._try_set_per_monitor_dpi_awareness_v2",
            return_value=True,
        ):
            with mock.patch(
                "eyes_protector.platform_utils._try_set_per_monitor_dpi_awareness"
            ) as per_monitor_mock:
                with mock.patch(
                    "eyes_protector.platform_utils._try_set_system_dpi_awareness"
                ) as system_mock:
                    self.assertEqual(
                        platform_utils.enable_high_dpi_mode(), "per-monitor-v2"
                    )
                    per_monitor_mock.assert_not_called()
                    system_mock.assert_not_called()

    def test_enable_high_dpi_mode_falls_back_to_system(self):
        with mock.patch(
            "eyes_protector.platform_utils._try_set_per_monitor_dpi_awareness_v2",
            return_value=False,
        ):
            with mock.patch(
                "eyes_protector.platform_utils._try_set_per_monitor_dpi_awareness",
                return_value=False,
            ):
                with mock.patch(
                    "eyes_protector.platform_utils._try_set_system_dpi_awareness",
                    return_value=True,
                ):
                    self.assertEqual(platform_utils.enable_high_dpi_mode(), "system")

    def test_get_window_dpi_scale_uses_base_dpi_ratio(self):
        with mock.patch(
            "eyes_protector.platform_utils.get_window_dpi", return_value=144
        ):
            self.assertEqual(platform_utils.get_window_dpi_scale(hwnd=123), 1.5)

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

    def test_get_platform_busy_reason_screen_lock_returns_idle(self):
        # QUNS_NOT_PRESENT (1) = lock screen
        with mock.patch(
            "eyes_protector.platform_utils._query_user_notification_state",
            return_value=1,
        ):
            self.assertEqual(
                platform_utils.get_platform_busy_reason(), BUSY_REASON_IDLE
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

    def test_foreground_window_covers_monitor_ignores_shell_and_desktop_classes(self):
        with mock.patch("ctypes.windll.user32.GetForegroundWindow", return_value=12345):
            with mock.patch("ctypes.windll.user32.IsIconic", return_value=False):
                with mock.patch("ctypes.windll.user32.IsWindowVisible", return_value=True):
                    # Test GetShellWindow match
                    with mock.patch("ctypes.windll.user32.GetShellWindow", return_value=12345):
                        self.assertFalse(platform_utils._foreground_window_covers_monitor())

                    # Test Progman / WorkerW class match
                    with mock.patch("ctypes.windll.user32.GetShellWindow", return_value=99999):
                        def mock_get_class_name(hwnd, buf, size):
                            buf.value = "Progman"
                            return len("Progman")

                        with mock.patch(
                            "ctypes.windll.user32.GetClassNameW",
                            side_effect=mock_get_class_name,
                        ):
                            self.assertFalse(platform_utils._foreground_window_covers_monitor())

    def test_multi_monitor_helpers_fallback_safely(self):
        # When user32 calls raise or fail, fallback sizes should be returned
        with mock.patch("ctypes.windll.user32.GetSystemMetrics", side_effect=RuntimeError):
            rect = platform_utils.get_virtual_screen_rect(fallback_size=(2560, 1440))
            self.assertEqual(rect, (0, 0, 2560, 1440))

        with mock.patch("ctypes.windll.user32.GetCursorPos", return_value=False):
            with mock.patch("ctypes.windll.user32.MonitorFromWindow", return_value=0):
                work_area = platform_utils.get_monitor_work_area(fallback_size=(1920, 1080))
                self.assertEqual(work_area, (0, 0, 1920, 1080))

                active_mon = platform_utils.get_active_monitor_rect(fallback_size=(1920, 1080))
                self.assertEqual(active_mon, (0, 0, 1920, 1080))

    def test_get_idle_time_handles_exception(self):
        with mock.patch(
            "ctypes.windll.user32.GetLastInputInfo", side_effect=Exception("win32 error")
        ):
            self.assertEqual(platform_utils.get_idle_time(), 0.0)

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
        import os
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
                    args, ["taskkill", "/F", "/FI", f"PID ne {os.getpid()}", "/IM", "EyesProtector.exe", "/T"]
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

    def test_check_single_instance_already_running_user_says_yes_close_success(self):
        root = mock.Mock()
        mutex = object()
        with mock.patch(
            "eyes_protector.platform_utils.create_single_instance_mutex",
            return_value=(mutex, platform_utils.ERROR_ALREADY_EXISTS),
        ):
            with mock.patch(
                "eyes_protector.platform_utils.messagebox.askyesno",
                return_value=True,
            ) as askyesno_mock:
                with mock.patch(
                    "eyes_protector.platform_utils.force_close_existing_instance",
                    return_value=True,
                ) as force_close_mock:
                    with mock.patch(
                        "eyes_protector.platform_utils.messagebox.showinfo"
                    ) as showinfo_mock:
                        with self.assertRaises(SystemExit) as exit_info:
                            platform_utils.check_single_instance(root)

        self.assertEqual(exit_info.exception.code, 0)
        root.withdraw.assert_called_once()
        root.attributes.assert_called_once_with("-topmost", True)
        askyesno_mock.assert_called_once()
        force_close_mock.assert_called_once()
        showinfo_mock.assert_not_called()

    def test_check_single_instance_already_running_user_says_yes_close_fail(self):
        root = mock.Mock()
        mutex = object()
        with mock.patch(
            "eyes_protector.platform_utils.create_single_instance_mutex",
            return_value=(mutex, platform_utils.ERROR_ALREADY_EXISTS),
        ):
            with mock.patch(
                "eyes_protector.platform_utils.messagebox.askyesno",
                return_value=True,
            ) as askyesno_mock:
                with mock.patch(
                    "eyes_protector.platform_utils.force_close_existing_instance",
                    return_value=False,
                ) as force_close_mock:
                    with mock.patch(
                        "eyes_protector.platform_utils.messagebox.showinfo"
                    ) as showinfo_mock:
                        with self.assertRaises(SystemExit) as exit_info:
                            platform_utils.check_single_instance(root)

        self.assertEqual(exit_info.exception.code, 0)
        root.withdraw.assert_called_once()
        root.attributes.assert_called_once_with("-topmost", True)
        askyesno_mock.assert_called_once()
        force_close_mock.assert_called_once()
        showinfo_mock.assert_called_once()

    def test_check_single_instance_already_running_user_says_no(self):
        root = mock.Mock()
        mutex = object()
        with mock.patch(
            "eyes_protector.platform_utils.create_single_instance_mutex",
            return_value=(mutex, platform_utils.ERROR_ALREADY_EXISTS),
        ):
            with mock.patch(
                "eyes_protector.platform_utils.messagebox.askyesno",
                return_value=False,
            ) as askyesno_mock:
                with mock.patch(
                    "eyes_protector.platform_utils.force_close_existing_instance"
                ) as force_close_mock:
                    with mock.patch(
                        "eyes_protector.platform_utils.messagebox.showinfo"
                    ) as showinfo_mock:
                        with self.assertRaises(SystemExit) as exit_info:
                            platform_utils.check_single_instance(root)

        self.assertEqual(exit_info.exception.code, 0)
        root.withdraw.assert_called_once()
        root.attributes.assert_called_once_with("-topmost", True)
        askyesno_mock.assert_called_once()
        force_close_mock.assert_not_called()
        showinfo_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
