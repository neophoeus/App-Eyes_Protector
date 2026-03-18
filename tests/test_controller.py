import unittest
from unittest import mock

from eyes_protector.config import AppConfig
from eyes_protector.controller import EyesProtectorController
from eyes_protector.core import STATE_DIALOG_VISIBLE, STATE_RUNNING


TEST_CONFIG = AppConfig(
    break_interval=10,
    snooze_interval=5,
    break_duration=5,
    poll_interval=1,
    idle_threshold=20,
)


class FakeRoot:
    def __init__(self):
        self.after_calls = []
        self.after_cancel_calls = []
        self._job_index = 0
        self.withdraw_called = False

    def withdraw(self):
        self.withdraw_called = True

    def after(self, delay, callback):
        job_id = f"job-{self._job_index}"
        self._job_index += 1
        self.after_calls.append((delay, callback, job_id))
        return job_id

    def after_cancel(self, job_id):
        self.after_cancel_calls.append(job_id)


class FakeWindow:
    pass


class FakeDialog:
    def __init__(self, controller):
        self.controller = controller
        self.window = FakeWindow()
        self.show_calls = 0

    def show(self):
        self.show_calls += 1


class FakeFloating:
    def __init__(self, controller):
        self.controller = controller
        self.window = FakeWindow()
        self.show_calls = 0
        self.hide_calls = 0
        self.update_pause_ui_calls = 0

    def show(self):
        self.show_calls += 1

    def hide(self):
        self.hide_calls += 1

    def update_pause_ui(self):
        self.update_pause_ui_calls += 1


class FakeFullscreen:
    def __init__(self, controller):
        self.controller = controller
        self.window = FakeWindow()
        self.show_calls = 0
        self.hide_calls = 0

    def show(self):
        self.show_calls += 1

    def hide(self):
        self.hide_calls += 1


class ControllerTests(unittest.TestCase):
    def _build_controller(self):
        root = FakeRoot()
        dialog_patch = mock.patch(
            "eyes_protector.controller.CenterReminderDialog", FakeDialog
        )
        floating_patch = mock.patch(
            "eyes_protector.controller.FloatingWidget", FakeFloating
        )
        fullscreen_patch = mock.patch(
            "eyes_protector.controller.FullScreenBreak", FakeFullscreen
        )
        patches = [dialog_patch, floating_patch, fullscreen_patch]
        for patcher in patches:
            patcher.start()
            self.addCleanup(patcher.stop)
        return root, EyesProtectorController(root, TEST_CONFIG)

    def test_toggle_pause_stops_and_resumes_tick_schedule(self):
        root, controller = self._build_controller()

        initial_job = controller._tick_job
        self.assertEqual(root.after_calls[0][0], 100)

        controller.toggle_pause()

        self.assertIsNone(controller._tick_job)
        self.assertEqual(root.after_cancel_calls, [initial_job])
        self.assertTrue(controller.runtime.paused)

        controller.toggle_pause()

        self.assertFalse(controller.runtime.paused)
        self.assertEqual(root.after_calls[-1][0], TEST_CONFIG.poll_interval * 1000)
        self.assertIsNotNone(controller._tick_job)

    def test_run_timer_shows_dialog_without_rescheduling_background_tick(self):
        root, controller = self._build_controller()
        controller.runtime = controller.runtime.__class__(
            time_elapsed=TEST_CONFIG.break_interval - 1,
            target_interval=controller.runtime.target_interval,
            state=controller.runtime.state,
            paused=controller.runtime.paused,
            floating_visible=controller.runtime.floating_visible,
            running=controller.runtime.running,
        )

        with mock.patch(
            "eyes_protector.controller.is_fullscreen_or_busy", return_value=False
        ):
            with mock.patch("eyes_protector.controller.get_idle_time", return_value=0):
                controller.run_timer()

        self.assertEqual(controller.runtime.state, STATE_DIALOG_VISIBLE)
        self.assertEqual(controller.dialog.show_calls, 1)
        self.assertIsNone(controller._tick_job)
        self.assertEqual(len(root.after_calls), 1)

    def test_break_flow_cancels_tick_and_finish_break_reschedules(self):
        root, controller = self._build_controller()

        initial_job = controller._tick_job
        controller.start_full_break()

        self.assertEqual(root.after_cancel_calls, [initial_job])
        self.assertIsNone(controller._tick_job)
        self.assertEqual(controller.fullscreen.show_calls, 1)

        controller.finish_break()

        self.assertEqual(root.after_calls[-1][0], TEST_CONFIG.poll_interval * 1000)
        self.assertIsNotNone(controller._tick_job)

    def test_snooze_from_dialog_state_reschedules_tick(self):
        root, controller = self._build_controller()
        controller._tick_job = None
        controller.runtime = controller.runtime.__class__(
            time_elapsed=controller.runtime.time_elapsed,
            target_interval=controller.runtime.target_interval,
            state=STATE_DIALOG_VISIBLE,
            paused=controller.runtime.paused,
            floating_visible=False,
            running=controller.runtime.running,
        )

        controller.snooze()

        self.assertEqual(controller.runtime.state, STATE_RUNNING)
        self.assertEqual(root.after_calls[-1][0], TEST_CONFIG.poll_interval * 1000)
        self.assertIsNotNone(controller._tick_job)

    def test_quit_app_cancels_tick_and_closes_windows(self):
        root, controller = self._build_controller()
        initial_job = controller._tick_job

        with mock.patch(
            "eyes_protector.controller.safe_destroy_window"
        ) as destroy_mock:
            controller.quit_app()

        self.assertFalse(controller.runtime.running)
        self.assertEqual(root.after_cancel_calls, [initial_job])
        self.assertEqual(controller.fullscreen.hide_calls, 1)
        self.assertEqual(destroy_mock.call_count, 4)


if __name__ == "__main__":
    unittest.main()
