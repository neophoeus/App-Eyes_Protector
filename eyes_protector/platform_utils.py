import ctypes
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox
import winsound


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]


class MONITORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("rcMonitor", RECT),
        ("rcWork", RECT),
        ("dwFlags", ctypes.c_uint),
    ]


MONITOR_DEFAULTTONEAREST = 2
ERROR_ALREADY_EXISTS = 183
FULLSCREEN_MARGIN_PX = 2


def _query_user_notification_state():
    state = ctypes.c_int()
    try:
        hr = ctypes.windll.shell32.SHQueryUserNotificationState(ctypes.byref(state))
        if hr == 0:
            return state.value
    except Exception:
        pass
    return None


def _foreground_window_covers_monitor():
    try:
        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return False
        if user32.IsIconic(hwnd) or not user32.IsWindowVisible(hwnd):
            return False

        rect = RECT()
        if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            return False
        if rect.right <= rect.left or rect.bottom <= rect.top:
            return False

        monitor = user32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)
        if not monitor:
            return False

        monitor_info = MONITORINFO()
        monitor_info.cbSize = ctypes.sizeof(MONITORINFO)
        if not user32.GetMonitorInfoW(monitor, ctypes.byref(monitor_info)):
            return False

        screen_rect = monitor_info.rcMonitor
        return (
            rect.left <= screen_rect.left + FULLSCREEN_MARGIN_PX
            and rect.top <= screen_rect.top + FULLSCREEN_MARGIN_PX
            and rect.right >= screen_rect.right - FULLSCREEN_MARGIN_PX
            and rect.bottom >= screen_rect.bottom - FULLSCREEN_MARGIN_PX
        )
    except Exception:
        return False


def create_single_instance_mutex(mutex_name):
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
    error_code = ctypes.windll.kernel32.GetLastError()
    return mutex, error_code


def is_fullscreen_or_busy():
    state = _query_user_notification_state()
    return state in (3, 4) or _foreground_window_covers_monitor()


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


def get_closable_instance_image_name():
    if not getattr(sys, "frozen", False):
        return None

    image_name = sys.executable.rsplit("\\", 1)[-1].strip()
    if not image_name:
        return None

    normalized_name = image_name.lower()
    if normalized_name in {"python.exe", "pythonw.exe", "py.exe", "pyw.exe"}:
        return None
    return image_name


def force_close_existing_instance():
    image_name = get_closable_instance_image_name()
    if image_name is None:
        return False

    creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    result = subprocess.run(
        ["taskkill", "/F", "/IM", image_name, "/T"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creation_flags,
    )
    return result.returncode == 0


def check_single_instance(root):
    mutex_name = "Global\\AppEyesProtectorMutex_1_0"
    mutex, error_code = create_single_instance_mutex(mutex_name)
    if not mutex:
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showerror(
            "App-Eyes Protector",
            "無法建立單實例鎖定，程式將結束。\n請稍後再試，或重新啟動 Windows 後再執行。",
            parent=root,
        )
        raise SystemExit(1)
    if error_code == ERROR_ALREADY_EXISTS:
        root.withdraw()
        root.attributes("-topmost", True)
        if messagebox.askyesno(
            "App-Eyes Protector",
            "護眼助理目前正在背景為您倒數計時中。\n\n您想要完全「強制關閉」這個軟體嗎？\n(按下「是」將會結束常駐保護)",
            parent=root,
        ):
            if not force_close_existing_instance():
                messagebox.showinfo(
                    "App-Eyes Protector",
                    "目前只能在打包執行檔模式下自動關閉既有實例。\n請手動結束舊的護眼程式後再重新啟動。",
                    parent=root,
                )
        raise SystemExit(0)
    root.mutex = mutex
