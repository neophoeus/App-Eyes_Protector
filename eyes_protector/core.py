from dataclasses import dataclass, replace


STATE_RUNNING = "RUNNING"
STATE_DIALOG_VISIBLE = "DIALOG_VISIBLE"
STATE_BREAKING = "BREAKING"
BUSY_REASON_NONE = "NONE"
BUSY_REASON_IDLE = "IDLE"
BUSY_REASON_FULLSCREEN = "FULLSCREEN"


@dataclass(frozen=True)
class RuntimeState:
    time_elapsed: int
    target_interval: int
    state: str = STATE_RUNNING
    paused: bool = False
    floating_visible: bool = True
    running: bool = True


@dataclass(frozen=True)
class TickResult:
    runtime: RuntimeState
    should_show_dialog: bool = False


def create_runtime_state(config):
    return RuntimeState(time_elapsed=0, target_interval=config.break_interval)


def toggle_pause(runtime):
    paused = not runtime.paused
    time_elapsed = 0 if not paused else runtime.time_elapsed
    return replace(runtime, paused=paused, time_elapsed=time_elapsed)


def apply_tick(runtime, config, busy_reason=BUSY_REASON_NONE):
    if not runtime.running:
        return TickResult(runtime)
    if runtime.state != STATE_RUNNING:
        return TickResult(runtime)

    if busy_reason == BUSY_REASON_IDLE:
        return TickResult(replace(runtime, time_elapsed=0, floating_visible=False))

    if busy_reason == BUSY_REASON_FULLSCREEN:
        return TickResult(replace(runtime, floating_visible=False))

    updated = replace(runtime, floating_visible=True)
    if updated.paused:
        return TickResult(updated)

    elapsed = updated.time_elapsed + config.poll_interval
    if elapsed >= updated.target_interval:
        return TickResult(
            replace(
                updated,
                time_elapsed=elapsed,
                state=STATE_DIALOG_VISIBLE,
                floating_visible=False,
            ),
            should_show_dialog=True,
        )
    return TickResult(replace(updated, time_elapsed=elapsed))


def apply_snooze(runtime, config):
    return replace(
        runtime,
        time_elapsed=0,
        target_interval=config.snooze_interval,
        state=STATE_RUNNING,
        floating_visible=True,
    )


def apply_start_break(runtime):
    return replace(runtime, state=STATE_BREAKING, floating_visible=False)


def apply_finish_break(runtime, config):
    return replace(
        runtime,
        time_elapsed=0,
        target_interval=config.break_interval,
        state=STATE_RUNNING,
        floating_visible=True,
    )


def apply_quit(runtime):
    return replace(runtime, running=False)
