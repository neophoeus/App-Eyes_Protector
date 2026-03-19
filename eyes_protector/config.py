from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    break_interval: int
    snooze_interval: int
    break_duration: int
    poll_interval: int
    idle_threshold: int
    fullscreen_transition_ticks: int


def load_config(argv):
    if "--test" in argv:
        return AppConfig(
            break_interval=10,
            snooze_interval=5,
            break_duration=5,
            poll_interval=1,
            idle_threshold=20,
            fullscreen_transition_ticks=1,
        )
    return AppConfig(
        break_interval=20 * 60,
        snooze_interval=5 * 60,
        break_duration=20,
        poll_interval=1,
        idle_threshold=300,
        fullscreen_transition_ticks=2,
    )
