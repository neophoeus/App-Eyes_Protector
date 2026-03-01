import tkinter as tk
from tkinter import messagebox
import time
import threading
import ctypes
import winsound
import sys
import os
import math
import random
if "--test" in sys.argv:
    BREAK_INTERVAL = 10
    SNOOZE_INTERVAL = 5
    BREAK_DURATION = 5
else:
    BREAK_INTERVAL = 20 * 60
    SNOOZE_INTERVAL = 5 * 60
    BREAK_DURATION = 20
POLL_INTERVAL = 1
def is_fullscreen_or_busy():
    state = ctypes.c_int()
    try:
        hr = ctypes.windll.shell32.SHQueryUserNotificationState(ctypes.byref(state))
        if hr == 0:
            if state.value in (1, 2, 3, 4, 7):
                return True
    except Exception:
        pass
    return False
class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("dwTime", ctypes.c_uint)
    ]
def get_idle_time():
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
        tick = ctypes.windll.kernel32.GetTickCount()
        elapsed = (tick - lii.dwTime) & 0xFFFFFFFF
        return elapsed / 1000.0
    return 0.0
class Leaf:
    def __init__(self, canvas, sw, sh):
        self.canvas = canvas
        self.sw = sw
        self.sh = sh
        self.size = random.uniform(sh * 0.03, sh * 0.08)
        self.x = random.uniform(0, sw)
        self.y = random.uniform(-self.size*3, sh)
        self.fall_speed = random.uniform(0.5, 2.5)
        self.sway_speed = random.uniform(0.01, 0.03)
        self.sway_range = random.uniform(40, 150)
        self.spin_speed = random.uniform(0.01, 0.05)
        self.time_offset = random.uniform(0, 100)
        self.angle_offset = random.uniform(0, math.pi * 2)
        colors = ["#a8e6cf", "#dcedc1", "#88d8b0", "#c1dfc4", "#a3e4d7", "#abebc6"]
        self.color = random.choice(colors)
        self.id = self.canvas.create_polygon(0, 0, 0, 0, 0, 0, fill=self.color, outline="")
    def _get_leaf_points(self, cx, cy, angle, scale, squeeze):
        points = []
        resolution = 6
        for i in range(resolution):
            t = (i / resolution) * math.pi * 2
            px = math.sin(t) * (scale * 0.3)
            py = math.cos(t) * scale
            px *= math.cos(squeeze)
            rx = px * math.cos(angle) - py * math.sin(angle)
            ry = px * math.sin(angle) + py * math.cos(angle)
            points.append(cx + rx)
            points.append(cy + ry)
        return points
    def update(self, t):
        self.y += self.fall_speed
        cx = self.x + math.sin((t + self.time_offset) * self.sway_speed) * self.sway_range
        cy = self.y
        if cy > self.sh + self.size:
            self.y = -self.size * 3
            self.x = random.uniform(0, self.sw)
            self.time_offset = random.uniform(0, 100)
        lean_angle = math.cos((t + self.time_offset) * self.sway_speed) * 0.5
        current_angle = self.angle_offset + lean_angle
        squeeze = (t + self.time_offset) * self.spin_speed
        points = self._get_leaf_points(cx, cy, current_angle, self.size, squeeze)
        self.canvas.coords(self.id, *points)
class CenterReminderDialog:
    def __init__(self, controller):
        self.controller = controller
        self.window = tk.Toplevel()
        self.window.withdraw()
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(bg="#ffffff") # 明亮白底卡片
        title_font = ("Microsoft JhengHei", 18, "bold")
        sub_font = ("Microsoft JhengHei", 12)
        btn_font = ("Microsoft JhengHei", 11, "bold")
        frame = tk.Frame(self.window, bg="#ffffff", highlightbackground="#e0e0e0", highlightthickness=1)
        frame.pack(fill=tk.BOTH, expand=True)
        lbl_title = tk.Label(frame, text="護眼時間到了", font=title_font, fg="#2c3e50", bg="#ffffff")
        lbl_title.pack(pady=(35, 10))
        lbl_msg = tk.Label(frame, text="您已經連續盯著螢幕一段時間了。\n給眼睛幾秒鐘，跟我一起深呼吸吧！",
                           font=sub_font, fg="#7f8c8d", bg="#ffffff", justify=tk.CENTER)
        lbl_msg.pack(padx=30, pady=(0, 30))
        btn_frame = tk.Frame(frame, bg="#ffffff")
        btn_frame.pack(fill=tk.X, padx=40, pady=(0, 35))
        btn_rest = tk.Button(btn_frame, text="開始放鬆 (20秒)  ⏎", font=btn_font, bg="#27ae60", fg="white",
                             relief=tk.FLAT, cursor="hand2", command=self.on_rest, activebackground="#2ecc71", pady=10)
        btn_rest.pack(side=tk.TOP, expand=True, fill=tk.X, pady=(0, 15))
        btn_snooze = tk.Button(btn_frame, text="稍後提醒 (5分鐘)  Esc", font=("Microsoft JhengHei", 10), bg="#ffffff", fg="#95a5a6",
                               relief=tk.FLAT, cursor="hand2", command=self.on_snooze, activebackground="#f5f6fa", activeforeground="#7f8c8d", pady=5)
        btn_snooze.pack(side=tk.TOP, expand=True, fill=tk.X)
        self.window.bind("<Return>", lambda e: self.on_rest())
        self.window.bind("<Escape>", lambda e: self.on_snooze())
    def show(self):
        w, h = 420, 320
        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.window.geometry(f"{w}x{h}+{x}+{y}")
        self.window.deiconify()
        self.window.focus_force()
        winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
    def hide(self):
        self.window.withdraw()
    def on_rest(self):
        self.hide()
        self.controller.start_full_break()
    def on_snooze(self):
        self.hide()
        self.controller.snooze()
class FullScreenBreak:
    def __init__(self, controller):
        self.controller = controller
        self.window = tk.Toplevel()
        self.window.withdraw()
        self.window.attributes("-topmost", True)
        self.window.attributes("-fullscreen", True)
        self.bg_color = "#e8f5e9"
        self.window.configure(bg=self.bg_color)
        self.canvas = tk.Canvas(self.window, bg=self.bg_color, highlightthickness=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        title_font = ("Microsoft JhengHei", 36)
        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        self.txt_shadow = self.canvas.create_text(
            sw//2 + 2, sh//2 + 2,
            text="", font=title_font, fill="#c8e6c9", justify=tk.CENTER
        )
        self.txt_main = self.canvas.create_text(
            sw//2, sh//2,
            text="", font=title_font, fill="#2c3e50", justify=tk.CENTER
        )
        self.close_id = self.canvas.create_text(
            sw - 50, 40, text="✕", font=("Segoe UI", 22), fill="#b0bec5"
        )
        self.canvas.tag_bind(self.close_id, "<ButtonRelease-1>", lambda e: self.finish_early())
        self.canvas.tag_bind(self.close_id, "<Enter>", lambda e: self.canvas.itemconfig(self.close_id, fill="#2c3e50"))
        self.canvas.tag_bind(self.close_id, "<Leave>", lambda e: self.canvas.itemconfig(self.close_id, fill="#b0bec5"))
        self.leaves = []
        self.animating = False
        self.start_time = 0
    def init_geometry(self):
        self.canvas.delete("all")
        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        title_font = ("Microsoft JhengHei", 36)
        self.txt_shadow = self.canvas.create_text(
            sw//2 + 2, sh//2 + 2, text="", font=title_font, fill="#c8e6c9", justify=tk.CENTER
        )
        self.txt_main = self.canvas.create_text(
            sw//2, sh//2, text="", font=title_font, fill="#2c3e50", justify=tk.CENTER
        )
        self.close_id = self.canvas.create_text(
            sw - 50, 40, text="✕", font=("Segoe UI", 22), fill="#b0bec5"
        )
        self.canvas.tag_bind(self.close_id, "<ButtonRelease-1>", lambda e: self.finish_early())
        self.canvas.tag_bind(self.close_id, "<Enter>", lambda e: self.canvas.itemconfig(self.close_id, fill="#2c3e50"))
        self.canvas.tag_bind(self.close_id, "<Leave>", lambda e: self.canvas.itemconfig(self.close_id, fill="#b0bec5"))
        self.leaves = [Leaf(self.canvas, sw, sh) for _ in range(15)]
        self.canvas.tag_raise(self.txt_shadow)
        self.canvas.tag_raise(self.txt_main)
        self.canvas.tag_raise(self.close_id)
    def _update_text(self, text):
        self.canvas.itemconfig(self.txt_shadow, text=text)
        self.canvas.itemconfig(self.txt_main, text=text)
    def _animation_loop(self):
        if not self.animating:
            return
        current_time = time.time() - self.start_time
        for leaf in self.leaves:
            leaf.update(current_time * 15)
        self.window.after(66, self._animation_loop)
    def show(self):
        self.window.update_idletasks()
        self.init_geometry()
        self.animating = True
        self.start_time = time.time()
        self.window.deiconify()
        self.window.focus_force()
        self.window.attributes("-topmost", True)
        self._update_text("🌿 20-20-20 護眼時刻\n\n看向 20 呎遠的地方，放鬆你的雙眼...")
        self._animation_loop()
        self._countdown_step(BREAK_DURATION)
    def hide(self):
        self.animating = False
        self.window.withdraw()
    def _countdown_step(self, remaining):
        if remaining > 0:
            self._update_text(f"🌿 20-20-20 護眼時刻\n\n看向 20 呎遠的地方，放鬆你的雙眼...\n\n剩 餘 {remaining} 秒")
            self.window.after(1000, self._countdown_step, remaining - 1)
        else:
            self._update_text("\n\n✨ 眼睛充電完成！\n回到工作站吧！\n\n")
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
            self.window.after(2000, self.finish)
    def finish_early(self):
        self.animating = False
        self._update_text("\n\n⏩ 休息中斷，回到工作站！\n\n")
        winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
        self.window.after(1000, self.finish)
    def finish(self):
        self.hide()
        self.controller.finish_break()
class FloatingWidget:
    def __init__(self, controller):
        self.controller = controller
        self.window = tk.Toplevel()
        self.window.attributes("-topmost", True)
        self.window.overrideredirect(True)
        self.window.attributes("-transparentcolor", "#000000")
        self.window.attributes("-alpha", 0.6)
        self.bg_color_normal = "#e8f5e9"
        self.bg_color_hover = "#ffffff"
        self.canvas = tk.Canvas(self.window, bg="#000000", highlightthickness=0, width=130, height=44)
        self.canvas.pack()
        self.r = 16
        self.normal_coords = (2, 2, 42, 42)
        self.hover_coords = (2, 2, 128, 42)
        points = self._get_round_rect_points(*self.normal_coords, self.r)
        self.bg_id = self.canvas.create_polygon(points, smooth=True, fill=self.bg_color_normal, outline="#a5d6a7", width=2)
        self.txt_icon = self.canvas.create_text(22, 22, text="👁️", font=("Segoe UI Emoji", 14), fill="#2c3e50")
        self.txt_label = self.canvas.create_text(65, 22, text="", font=("Microsoft JhengHei", 10, "bold"), fill="#27ae60")
        self.btn_close = self.canvas.create_text(110, 22, text="✕", font=("Microsoft JhengHei", 11, "bold"), fill="#e74c3c", state="hidden")
        self.canvas.bind("<ButtonPress-1>", self.start_move)
        self.canvas.bind("<B1-Motion>", self.do_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_click)
        self.canvas.bind("<Enter>", self.on_hover)
        self.canvas.bind("<Leave>", self.on_leave)
        self.window.update_idletasks()
        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        w, h = 130, 44
        x = sw - w - 40
        y = sh - h - 80
        self.window.geometry(f"{w}x{h}+{x}+{y}")
        self._x = 0
        self._y = 0
        self._dragged = False
    def _get_round_rect_points(self, x1, y1, x2, y2, r):
        return [
            x1+r, y1,  x1+r, y1,  x2-r, y1,  x2-r, y1,
            x2, y1,    x2, y1+r,  x2, y1+r,  x2, y2-r,  x2, y2-r,
            x2, y2,    x2-r, y2,  x2-r, y2,  x1+r, y2,  x1+r, y2,
            x1, y2,    x1, y2-r,  x1, y2-r,  x1, y1+r,  x1, y1+r,
            x1, y1
        ]
    def start_move(self, event):
        self._x = event.x
        self._y = event.y
        self._dragged = False
    def do_move(self, event):
        self._dragged = True
        deltax = event.x - self._x
        deltay = event.y - self._y
        x = self.window.winfo_x() + deltax
        y = self.window.winfo_y() + deltay
        self.window.geometry(f"+{x}+{y}")
    def on_click(self, event):
        if not self._dragged and event.x > 90:
            if self.canvas.itemcget(self.btn_close, "state") == "normal":
                self.controller.quit_app()
    def on_hover(self, e):
        self.window.attributes("-alpha", 0.95)
        new_points = self._get_round_rect_points(*self.hover_coords, self.r)
        self.canvas.coords(self.bg_id, *new_points)
        self.canvas.itemconfig(self.bg_id, fill=self.bg_color_hover, outline="#81c784")
        self.canvas.itemconfig(self.txt_label, text="保護中")
        self.canvas.itemconfig(self.btn_close, state="normal")
        self.window.config(cursor="hand2")
    def on_leave(self, e):
        x, y = self.window.winfo_pointerxy()
        wx = self.window.winfo_rootx()
        wy = self.window.winfo_rooty()
        ww = self.window.winfo_width()
        wh = self.window.winfo_height()
        if not (wx <= x <= wx + ww and wy <= y <= wy + wh):
            self.window.attributes("-alpha", 0.6)
            old_points = self._get_round_rect_points(*self.normal_coords, self.r)
            self.canvas.coords(self.bg_id, *old_points)
            self.canvas.itemconfig(self.bg_id, fill=self.bg_color_normal, outline="#a5d6a7")
            self.canvas.itemconfig(self.txt_label, text="")
            self.canvas.itemconfig(self.btn_close, state="hidden")
            self.window.config(cursor="arrow")
    def hide(self):
        if self.window.state() != "withdrawn":
            self.window.withdraw()
    def show(self):
        if self.window.state() == "withdrawn":
            self.window.deiconify()
class EyesProtectorController:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()
        self.dialog = CenterReminderDialog(self)
        self.fullscreen = FullScreenBreak(self)
        self.floating = FloatingWidget(self)
        self.root.after(100, self.floating.show)
        self.time_elapsed = 0
        self.target_interval = BREAK_INTERVAL
        self.state = "RUNNING"
        self.running = True
        self.timer_thread = threading.Thread(target=self.run_timer, daemon=True)
        self.timer_thread.start()
    def run_timer(self):
        while self.running:
            time.sleep(POLL_INTERVAL)
            if self.state != "RUNNING":
                continue
            idle_sec = get_idle_time()
            idle_threshold = 20 if "--test" in sys.argv else 300
            if is_fullscreen_or_busy() or idle_sec >= idle_threshold:
                self.time_elapsed = 0
                self.root.after(0, self.floating.hide)
                continue
            else:
                self.root.after(0, self.floating.show)
            self.time_elapsed += POLL_INTERVAL
            if self.time_elapsed >= self.target_interval:
                self.state = "DIALOG_VISIBLE"
                self.root.after(0, self.floating.hide)
                self.root.after(0, self.dialog.show)
    def snooze(self):
        self.time_elapsed = 0
        self.target_interval = SNOOZE_INTERVAL
        self.state = "RUNNING"
    def start_full_break(self):
        self.state = "BREAKING"
        self.root.after(0, self.floating.hide)
        self.root.after(0, self.fullscreen.show)
    def finish_break(self):
        self.time_elapsed = 0
        self.target_interval = BREAK_INTERVAL
        self.state = "RUNNING"
    def quit_app(self):
        self.running = False
        try:
            self.floating.window.destroy()
        except: pass
        try:
            self.dialog.window.destroy()
        except: pass
        try:
            self.fullscreen.window.destroy()
        except: pass
        self.root.destroy()
        sys.exit(0)
def check_single_instance(root):
    ERROR_ALREADY_EXISTS = 183
    mutex_name = "Global\\AppEyesProtectorMutex_1_0"
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
    if ctypes.windll.kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
        root.withdraw()
        root.attributes("-topmost", True)
        if messagebox.askyesno(
            "App-Eyes Protector",
            "護眼助理目前正在背景為您倒數計時中。\n\n您想要完全「強制關閉」這個軟體嗎？\n(按下「是」將會結束常駐保護)",
            parent=root
        ):
            os.system('taskkill /F /IM EyesProtector.exe /T >nul 2>&1')
            os.system('taskkill /F /IM main.exe /T >nul 2>&1') # 防呆
        sys.exit(0)
    root.mutex = mutex
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    check_single_instance(root)
    app = EyesProtectorController(root)
    root.mainloop()
