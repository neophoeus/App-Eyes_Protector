import sys
import tkinter as tk

from .config import load_config
from .controller import EyesProtectorController
from .platform_utils import check_single_instance, enable_high_dpi_mode


def main(argv=None):
    if argv is None:
        argv = sys.argv
    if any(flag in argv for flag in ("--help", "-h")):
        print("App-Eyes Protector - A lightweight immersive eye protection assistant for Windows.\n")
        print("Usage:")
        print("  main.py [options]\n")
        print("Options:")
        print("  -h, --help  Show this help message and exit.")
        print("  --test      Run with test profile (accelerated timers for testing).")
        sys.exit(0)
    enable_high_dpi_mode()
    root = tk.Tk()
    root.withdraw()
    check_single_instance(root)
    root.app_controller = EyesProtectorController(root, load_config(argv))
    root.mainloop()


if __name__ == "__main__":
    main()
