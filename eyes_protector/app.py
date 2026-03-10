import sys
import tkinter as tk

from .config import load_config
from .controller import EyesProtectorController
from .platform_utils import check_single_instance


def main(argv=None):
    if argv is None:
        argv = sys.argv
    root = tk.Tk()
    root.withdraw()
    check_single_instance(root)
    root.app_controller = EyesProtectorController(root, load_config(argv))
    root.mainloop()


if __name__ == "__main__":
    main()
