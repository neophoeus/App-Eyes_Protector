import sys
import tkinter as tk

from .config import get_default_config_path, load_config
from .controller import EyesProtectorController
from .i18n import set_language
from .platform_utils import check_single_instance, enable_high_dpi_mode


def main(argv=None):
    if argv is None:
        argv = sys.argv
    if any(flag in argv for flag in ("--help", "-h")):
        print("App-Eyes Protector - A lightweight immersive eye protection assistant for Windows.\n")
        print("Usage:")
        print("  main.py [options]\n")
        print("Options:")
        print("  -h, --help              Show this help message and exit.")
        print("  --test                  Run with test profile (accelerated timers for testing).")
        print("  --interval SECONDS      Work break interval in seconds (default: 1200).")
        print("  --break-seconds SECONDS Break duration in seconds (default: 20).")
        print("  --warning-seconds SEC   Warning duration in seconds (default: 10).")
        print("  --snooze-minutes MIN    Snooze interval in minutes (default: 5).")
        print("  --mute                  Disable all audio sounds.")
        print("  --lang CODE             Set UI language (zh-TW, zh-CN, ja, ko, en).")
        print("  --config PATH           Path to custom JSON configuration file.")
        sys.exit(0)
    enable_high_dpi_mode()
    root = tk.Tk()
    root.withdraw()
    cfg = load_config(argv, config_path=get_default_config_path())
    if cfg.language:
        set_language(cfg.language)
    check_single_instance(root)
    root.app_controller = EyesProtectorController(root, cfg)
    root.mainloop()


if __name__ == "__main__":
    main()
