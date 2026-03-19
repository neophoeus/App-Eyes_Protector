import unittest

from eyes_protector.config import AppConfig
from eyes_protector.core import (
    BUSY_REASON_FULLSCREEN,
    BUSY_REASON_IDLE,
    BUSY_REASON_NONE,
    STATE_BREAKING,
    STATE_DIALOG_VISIBLE,
    STATE_RUNNING,
    apply_finish_break,
    apply_quit,
    apply_snooze,
    apply_start_break,
    apply_tick,
    create_runtime_state,
    toggle_pause,
)


TEST_CONFIG = AppConfig(
    break_interval=10,
    snooze_interval=5,
    break_duration=5,
    poll_interval=1,
    idle_threshold=20,
    fullscreen_transition_ticks=1,
)


class CoreStateTests(unittest.TestCase):
    def test_idle_tick_resets_elapsed_and_hides_widget(self):
        runtime = create_runtime_state(TEST_CONFIG)
        runtime = runtime.__class__(
            time_elapsed=7,
            target_interval=runtime.target_interval,
            state=runtime.state,
            paused=runtime.paused,
            floating_visible=True,
            running=runtime.running,
        )

        result = apply_tick(runtime, TEST_CONFIG, BUSY_REASON_IDLE)

        self.assertEqual(result.runtime.time_elapsed, 0)
        self.assertFalse(result.runtime.floating_visible)
        self.assertFalse(result.should_show_dialog)

    def test_fullscreen_tick_freezes_elapsed_and_hides_widget(self):
        runtime = create_runtime_state(TEST_CONFIG)
        runtime = runtime.__class__(
            time_elapsed=7,
            target_interval=runtime.target_interval,
            state=runtime.state,
            paused=runtime.paused,
            floating_visible=True,
            running=runtime.running,
        )

        result = apply_tick(runtime, TEST_CONFIG, BUSY_REASON_FULLSCREEN)

        self.assertEqual(result.runtime.time_elapsed, 7)
        self.assertFalse(result.runtime.floating_visible)
        self.assertFalse(result.should_show_dialog)

    def test_paused_tick_keeps_elapsed_unchanged(self):
        runtime = create_runtime_state(TEST_CONFIG)
        runtime = toggle_pause(runtime)
        runtime = runtime.__class__(
            time_elapsed=4,
            target_interval=runtime.target_interval,
            state=runtime.state,
            paused=runtime.paused,
            floating_visible=runtime.floating_visible,
            running=runtime.running,
        )

        result = apply_tick(runtime, TEST_CONFIG, BUSY_REASON_NONE)

        self.assertEqual(result.runtime.time_elapsed, 4)
        self.assertEqual(result.runtime.state, STATE_RUNNING)
        self.assertFalse(result.should_show_dialog)

    def test_tick_opens_dialog_when_interval_reached(self):
        runtime = create_runtime_state(TEST_CONFIG)
        runtime = runtime.__class__(
            time_elapsed=9,
            target_interval=runtime.target_interval,
            state=runtime.state,
            paused=runtime.paused,
            floating_visible=runtime.floating_visible,
            running=runtime.running,
        )

        result = apply_tick(runtime, TEST_CONFIG, BUSY_REASON_NONE)

        self.assertEqual(result.runtime.state, STATE_DIALOG_VISIBLE)
        self.assertFalse(result.runtime.floating_visible)
        self.assertTrue(result.should_show_dialog)

    def test_resume_from_pause_resets_elapsed(self):
        runtime = create_runtime_state(TEST_CONFIG)
        runtime = toggle_pause(runtime)
        runtime = runtime.__class__(
            time_elapsed=8,
            target_interval=runtime.target_interval,
            state=runtime.state,
            paused=runtime.paused,
            floating_visible=runtime.floating_visible,
            running=runtime.running,
        )

        resumed = toggle_pause(runtime)

        self.assertFalse(resumed.paused)
        self.assertEqual(resumed.time_elapsed, 0)

    def test_snooze_sets_shorter_target_and_returns_running(self):
        runtime = create_runtime_state(TEST_CONFIG)
        runtime = apply_start_break(runtime)

        snoozed = apply_snooze(runtime, TEST_CONFIG)

        self.assertEqual(snoozed.state, STATE_RUNNING)
        self.assertEqual(snoozed.target_interval, TEST_CONFIG.snooze_interval)
        self.assertTrue(snoozed.floating_visible)

    def test_start_and_finish_break_restore_main_interval(self):
        runtime = create_runtime_state(TEST_CONFIG)

        breaking = apply_start_break(runtime)
        restored = apply_finish_break(breaking, TEST_CONFIG)

        self.assertEqual(breaking.state, STATE_BREAKING)
        self.assertFalse(breaking.floating_visible)
        self.assertEqual(restored.state, STATE_RUNNING)
        self.assertEqual(restored.target_interval, TEST_CONFIG.break_interval)
        self.assertTrue(restored.floating_visible)

    def test_quit_marks_runtime_not_running(self):
        runtime = create_runtime_state(TEST_CONFIG)

        stopped = apply_quit(runtime)

        self.assertFalse(stopped.running)


if __name__ == "__main__":
    unittest.main()
