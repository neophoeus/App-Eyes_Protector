import ctypes
import subprocess
import tkinter as tk
from tkinter import messagebox
import winsound


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]


def is_fullscreen_or_busy():
    state = ctypes.c_int()
    try:
        hr = ctypes.windll.shell32.SHQueryUserNotificationState(ctypes.byref(state))
        if hr == 0 and state.value in (3, 4):
            return True
    except Exception:
        pass
    return False


def get_idle_time():
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
        tick = ctypes.windll.kernel32.GetTickCount()
        elapsed = (tick - lii.dwTime) & 0xFFFFFFFF
        return elapsed / 1000.0
    return 0.0


def safe_play_sound(alias_name):
    try:
        winsound.PlaySound(alias_name, winsound.SND_ALIAS | winsound.SND_ASYNC)
    except RuntimeError:
        pass


def safe_destroy_window(window):
    if window is None:
        return
    try:
        if window.winfo_exists():
            window.destroy()
    except tk.TclError:
        pass


def force_close_existing_instance():
    creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    for image_name in ("EyesProtector.exe", "main.exe"):
        subprocess.run(
            ["taskkill", "/F", "/IM", image_name, "/T"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creation_flags,
        )


def check_single_instance(root):
    error_already_exists = 183
    mutex_name = "Global\\AppEyesProtectorMutex_1_0"
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
    if ctypes.windll.kernel32.GetLastError() == error_already_exists:
        root.withdraw()
        root.attributes("-topmost", True)
        if messagebox.askyesno(
            "App-Eyes Protector",
            "護眼助理目前正在背景為您倒數計時中。\n\n您想要完全「強制關閉」這個軟體嗎？\n(按下「是」將會結束常駐保護)",
            parent=root,
        ):
            force_close_existing_instance()
        raise SystemExit(0)
    root.mutex = mutex
