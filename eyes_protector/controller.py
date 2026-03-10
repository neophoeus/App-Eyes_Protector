from .core import (
    apply_finish_break,
    apply_quit,
    apply_snooze,
    apply_start_break,
    apply_tick,
    create_runtime_state,
    toggle_pause,
)
from .platform_utils import get_idle_time, is_fullscreen_or_busy, safe_destroy_window
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
        self._set_floating_visibility(self.runtime.floating_visible)
        self._schedule_tick(100)

    @property
    def paused(self):
        return self.runtime.paused

    @property
    def state(self):
        return self.runtime.state

    def _schedule_tick(self, delay_ms=None):
        if not self.runtime.running or self._tick_job is not None:
            return
        delay = self.config.poll_interval * 1000 if delay_ms is None else delay_ms
        self._tick_job = self.root.after(delay, self.run_timer)

    def _set_floating_visibility(self, visible):
        if visible:
            self.floating.show()
        else:
            self.floating.hide()

    def toggle_pause(self):
        self.runtime = toggle_pause(self.runtime)
        self.floating.update_pause_ui()

    def run_timer(self):
        self._tick_job = None
        if not self.runtime.running:
            return
        is_busy = is_fullscreen_or_busy() or get_idle_time() >= self.config.idle_threshold
        tick_result = apply_tick(self.runtime, self.config, is_busy)
        previous_visibility = self.runtime.floating_visible
        self.runtime = tick_result.runtime
        if previous_visibility != self.runtime.floating_visible:
            self._set_floating_visibility(self.runtime.floating_visible)
        if tick_result.should_show_dialog:
            self.dialog.show()
        self._schedule_tick()

    def snooze(self):
        previous_visibility = self.runtime.floating_visible
        self.runtime = apply_snooze(self.runtime, self.config)
        if previous_visibility != self.runtime.floating_visible:
            self._set_floating_visibility(self.runtime.floating_visible)

    def start_full_break(self):
        previous_visibility = self.runtime.floating_visible
        self.runtime = apply_start_break(self.runtime)
        if previous_visibility != self.runtime.floating_visible:
            self._set_floating_visibility(self.runtime.floating_visible)
        self.fullscreen.show()

    def finish_break(self):
        previous_visibility = self.runtime.floating_visible
        self.runtime = apply_finish_break(self.runtime, self.config)
        if previous_visibility != self.runtime.floating_visible:
            self._set_floating_visibility(self.runtime.floating_visible)

    def quit_app(self):
        self.runtime = apply_quit(self.runtime)
        if self._tick_job is not None:
            try:
                self.root.after_cancel(self._tick_job)
            except Exception:
                pass
            self._tick_job = None
        self.fullscreen.hide()
        safe_destroy_window(self.floating.window)
        safe_destroy_window(self.dialog.window)
        safe_destroy_window(self.fullscreen.window)
        safe_destroy_window(self.root)
