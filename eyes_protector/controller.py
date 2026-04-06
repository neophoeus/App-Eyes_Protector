from .core import (
    BUSY_REASON_FULLSCREEN,
    BUSY_REASON_IDLE,
    BUSY_REASON_NONE,
    STATE_RUNNING,
    apply_finish_break,
    apply_quit,
    apply_snooze,
    apply_start_break,
    apply_tick,
    create_runtime_state,
    toggle_pause,
)
from .platform_utils import get_idle_time, get_platform_busy_reason, safe_destroy_window
from .ui import CenterReminderDialog, FloatingWidget, FullScreenBreak


class EyesProtectorController:
    def __init__(self, root, config):
        self.root = root
        self.config = config
        self.root.withdraw()
        self.runtime = create_runtime_state(config)
        self.dialog = CenterReminderDialog(self)
        self.fullscreen = FullScreenBreak(self)
        self.floating = FloatingWidget(self)
        self._tick_job = None
        self._effective_busy_reason = BUSY_REASON_NONE
        self._fullscreen_busy_streak = 0
        self._fullscreen_clear_streak = 0
        self._quitting = False
        self._set_floating_visibility(self.runtime.floating_visible)
        self._sync_tick_schedule(100)

    @property
    def paused(self):
        return self.runtime.paused

    @property
    def state(self):
        return self.runtime.state

    def _should_schedule_tick(self):
        return (
            self.runtime.running
            and self.runtime.state == STATE_RUNNING
            and not self.runtime.paused
        )

    def _cancel_tick(self):
        if self._tick_job is None:
            return
        try:
            self.root.after_cancel(self._tick_job)
        except Exception:
            pass
        self._tick_job = None

    def _schedule_tick(self, delay_ms=None):
        if not self._should_schedule_tick() or self._tick_job is not None:
            return
        delay = self.config.poll_interval * 1000 if delay_ms is None else delay_ms
        self._tick_job = self.root.after(delay, self.run_timer)

    def _sync_tick_schedule(self, delay_ms=None):
        if self._should_schedule_tick():
            self._schedule_tick(delay_ms)
            return
        self._cancel_tick()

    def _set_floating_visibility(self, visible):
        if visible:
            self.floating.show()
        else:
            self.floating.hide()

    def _resolve_busy_reason(self, raw_busy_reason):
        if raw_busy_reason == BUSY_REASON_IDLE:
            self._effective_busy_reason = BUSY_REASON_IDLE
            self._fullscreen_busy_streak = 0
            self._fullscreen_clear_streak = 0
            return self._effective_busy_reason

        if raw_busy_reason == BUSY_REASON_FULLSCREEN:
            self._fullscreen_clear_streak = 0
            self._fullscreen_busy_streak += 1
            if (
                self._effective_busy_reason == BUSY_REASON_FULLSCREEN
                or self._fullscreen_busy_streak
                >= self.config.fullscreen_transition_ticks
            ):
                self._effective_busy_reason = BUSY_REASON_FULLSCREEN
            return self._effective_busy_reason

        self._fullscreen_busy_streak = 0
        if self._effective_busy_reason == BUSY_REASON_FULLSCREEN:
            self._fullscreen_clear_streak += 1
            if self._fullscreen_clear_streak < self.config.fullscreen_transition_ticks:
                return self._effective_busy_reason

        self._fullscreen_clear_streak = 0
        self._effective_busy_reason = BUSY_REASON_NONE
        return self._effective_busy_reason

    def _detect_busy_reason(self):
        idle_time = get_idle_time()
        if idle_time >= self.config.idle_threshold:
            return self._resolve_busy_reason(BUSY_REASON_IDLE)
        return self._resolve_busy_reason(get_platform_busy_reason())

    def toggle_pause(self):
        self.runtime = toggle_pause(self.runtime)
        self.floating.update_pause_ui()
        self._sync_tick_schedule()

    def run_timer(self):
        self._tick_job = None
        if not self.runtime.running:
            return
        busy_reason = self._detect_busy_reason()
        tick_result = apply_tick(self.runtime, self.config, busy_reason)
        previous_visibility = self.runtime.floating_visible
        self.runtime = tick_result.runtime
        if previous_visibility != self.runtime.floating_visible:
            self._set_floating_visibility(self.runtime.floating_visible)
        if tick_result.should_show_dialog:
            self.dialog.show()
        self._sync_tick_schedule()

    def snooze(self):
        previous_visibility = self.runtime.floating_visible
        self.runtime = apply_snooze(self.runtime, self.config)
        if previous_visibility != self.runtime.floating_visible:
            self._set_floating_visibility(self.runtime.floating_visible)
        self._sync_tick_schedule()

    def start_full_break(self):
        previous_runtime = self.runtime
        previous_visibility = self.runtime.floating_visible
        self.runtime = apply_start_break(self.runtime)
        if previous_visibility != self.runtime.floating_visible:
            self._set_floating_visibility(self.runtime.floating_visible)
        self._sync_tick_schedule()
        try:
            self.fullscreen.show()
        except Exception:
            self.runtime = previous_runtime
            self._set_floating_visibility(self.runtime.floating_visible)
            self._sync_tick_schedule()
            raise

    def finish_break(self):
        previous_visibility = self.runtime.floating_visible
        self.runtime = apply_finish_break(self.runtime, self.config)
        if previous_visibility != self.runtime.floating_visible:
            self._set_floating_visibility(self.runtime.floating_visible)
        self._sync_tick_schedule()

    def _destroy_windows(self):
        safe_destroy_window(self.floating.window)
        safe_destroy_window(self.dialog.window)
        safe_destroy_window(self.fullscreen.window)
        safe_destroy_window(self.root)

    def quit_app(self):
        if self._quitting:
            return
        self._quitting = True
        self.runtime = apply_quit(self.runtime)
        self._cancel_tick()
        self.fullscreen.hide()
        self.dialog.hide()
        self.floating.hide()
        after_idle = getattr(self.root, "after_idle", None)
        if after_idle is None:
            self._destroy_windows()
            return
        try:
            after_idle(self._destroy_windows)
        except Exception:
            self._destroy_windows()
