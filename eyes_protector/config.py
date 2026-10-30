import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    break_interval: int
    snooze_interval: int
    break_duration: int
    poll_interval: int
    idle_threshold: int
    fullscreen_transition_ticks: int
    warning_duration: int
    sound_enabled: bool = True
    language: str | None = None


DEFAULT_BREAK_INTERVAL = 20 * 60
DEFAULT_SNOOZE_INTERVAL = 5 * 60
DEFAULT_BREAK_DURATION = 20
DEFAULT_POLL_INTERVAL = 1
DEFAULT_IDLE_THRESHOLD = 300
DEFAULT_FULLSCREEN_TRANSITION_TICKS = 2
DEFAULT_WARNING_DURATION = 10
DEFAULT_SOUND_ENABLED = True
DEFAULT_LANGUAGE = None

SUPPORTED_LANGUAGES = frozenset({"zh-TW", "zh-CN", "ja", "ko", "en"})


def get_default_config_path() -> Path:
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / "AppEyesProtector" / "config.json"
    return Path.home() / ".config" / "AppEyesProtector" / "config.json"


def _clamp_int(val, min_v, max_v, default):
    # Guard against boolean which is a subclass of int in Python
    if not isinstance(val, int) or isinstance(val, bool):
        return default
    if val < min_v:
        return min_v
    if val > max_v:
        return max_v
    return val


def _parse_json_config(file_path: Path | str | None) -> dict:
    if not file_path:
        return {}
    try:
        path = Path(file_path)
        if not path.is_file():
            return {}
        content = path.read_text(encoding="utf-8")
        data = json.loads(content)
        if isinstance(data, dict):
            return data
    except (OSError, ValueError, UnicodeDecodeError):
        pass
    return {}


def load_config(argv, config_path: Path | str | None = None) -> AppConfig:
    if "--test" in argv:
        sound_enabled = "--mute" not in argv
        language = None
        for i, arg in enumerate(argv):
            if arg == "--lang" and i + 1 < len(argv):
                cand = argv[i + 1]
                if cand in SUPPORTED_LANGUAGES:
                    language = cand
        return AppConfig(
            break_interval=10,
            snooze_interval=5,
            break_duration=5,
            poll_interval=1,
            idle_threshold=20,
            fullscreen_transition_ticks=1,
            warning_duration=5,
            sound_enabled=sound_enabled,
            language=language,
        )

    # 1. Check if --config is specified in CLI arguments
    cli_config_path = None
    for i, arg in enumerate(argv):
        if arg == "--config" and i + 1 < len(argv):
            cli_config_path = argv[i + 1]
            break

    target_config_path = cli_config_path if cli_config_path is not None else config_path
    file_cfg = _parse_json_config(target_config_path)

    # Base values from defaults, overridden by valid JSON config
    break_interval = _clamp_int(
        file_cfg.get("break_interval", DEFAULT_BREAK_INTERVAL),
        5,
        14400,
        DEFAULT_BREAK_INTERVAL,
    )
    snooze_interval = _clamp_int(
        file_cfg.get("snooze_interval", DEFAULT_SNOOZE_INTERVAL),
        5,
        3600,
        DEFAULT_SNOOZE_INTERVAL,
    )
    break_duration = _clamp_int(
        file_cfg.get("break_duration", DEFAULT_BREAK_DURATION),
        3,
        600,
        DEFAULT_BREAK_DURATION,
    )
    poll_interval = _clamp_int(
        file_cfg.get("poll_interval", DEFAULT_POLL_INTERVAL),
        1,
        10,
        DEFAULT_POLL_INTERVAL,
    )
    idle_threshold = _clamp_int(
        file_cfg.get("idle_threshold", DEFAULT_IDLE_THRESHOLD),
        10,
        7200,
        DEFAULT_IDLE_THRESHOLD,
    )
    fullscreen_transition_ticks = _clamp_int(
        file_cfg.get("fullscreen_transition_ticks", DEFAULT_FULLSCREEN_TRANSITION_TICKS),
        1,
        10,
        DEFAULT_FULLSCREEN_TRANSITION_TICKS,
    )
    warning_duration = _clamp_int(
        file_cfg.get("warning_duration", DEFAULT_WARNING_DURATION),
        1,
        120,
        DEFAULT_WARNING_DURATION,
    )

    sound_val = file_cfg.get("sound_enabled", DEFAULT_SOUND_ENABLED)
    sound_enabled = bool(sound_val) if isinstance(sound_val, bool) else DEFAULT_SOUND_ENABLED

    lang_val = file_cfg.get("language", DEFAULT_LANGUAGE)
    language = lang_val if lang_val in SUPPORTED_LANGUAGES else None

    # 2. CLI flags override JSON config
    for i, arg in enumerate(argv):
        if arg == "--interval" and i + 1 < len(argv):
            try:
                break_interval = _clamp_int(int(argv[i + 1]), 5, 14400, break_interval)
            except ValueError:
                pass
        elif arg == "--break-seconds" and i + 1 < len(argv):
            try:
                break_duration = _clamp_int(int(argv[i + 1]), 3, 600, break_duration)
            except ValueError:
                pass
        elif arg == "--warning-seconds" and i + 1 < len(argv):
            try:
                warning_duration = _clamp_int(int(argv[i + 1]), 1, 120, warning_duration)
            except ValueError:
                pass
        elif arg == "--snooze-minutes" and i + 1 < len(argv):
            try:
                mins = float(argv[i + 1])
                snooze_interval = _clamp_int(int(mins * 60), 5, 3600, snooze_interval)
            except (ValueError, OverflowError):
                pass
        elif arg == "--snooze-seconds" and i + 1 < len(argv):
            try:
                snooze_interval = _clamp_int(int(argv[i + 1]), 5, 3600, snooze_interval)
            except ValueError:
                pass
        elif arg == "--mute":
            sound_enabled = False
        elif arg == "--lang" and i + 1 < len(argv):
            cand = argv[i + 1]
            if cand in SUPPORTED_LANGUAGES:
                language = cand

    return AppConfig(
        break_interval=break_interval,
        snooze_interval=snooze_interval,
        break_duration=break_duration,
        poll_interval=poll_interval,
        idle_threshold=idle_threshold,
        fullscreen_transition_ticks=fullscreen_transition_ticks,
        warning_duration=warning_duration,
        sound_enabled=sound_enabled,
        language=language,
    )
