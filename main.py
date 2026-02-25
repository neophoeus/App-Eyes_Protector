import tkinter as tk
import time
import threading
import ctypes
import winsound
import sys
import math
import random

# ================= 設定區 =================
if "--test" in sys.argv:
    BREAK_INTERVAL = 10  # 測試用：每 10 秒提醒
    SNOOZE_INTERVAL = 5  # 測試用：稍後提醒 5 秒
    BREAK_DURATION = 5   # 測試用：休息 5 秒
else:
    BREAK_INTERVAL = 20 * 60  # 每 20 分鐘提醒一次
    SNOOZE_INTERVAL = 5 * 60  # 稍後提醒延遲 5 分鐘
    BREAK_DURATION = 20       # 實際休息 20 秒

POLL_INTERVAL = 1  # 每 1 秒檢查一次狀態

# ================= 系統偵測 =================
def is_fullscreen_or_busy():
    state = ctypes.c_int()
    try:
        hr = ctypes.windll.shell32.SHQueryUserNotificationState(ctypes.byref(state))
        if hr == 0:
            if state.value in (2, 3, 4, 7):
                return True
    except Exception:
        pass
    return False

# ================= 幾何背景動畫設定 (飄落綠葉) =================
class Leaf:
    """幾何飄落樹葉"""
    def __init__(self, canvas, sw, sh):
        self.canvas = canvas
        self.sw = sw
        self.sh = sh
        
        # 尺寸與基底位置
        self.size = random.uniform(sh * 0.03, sh * 0.08) # 葉子大小
        self.x = random.uniform(0, sw)
        self.y = random.uniform(-self.size*3, sh)
        
        # 運動參數 (模擬微風與重力)
        self.fall_speed = random.uniform(0.5, 2.5) # 垂直下降速度(極緩慢)
        self.sway_speed = random.uniform(0.01, 0.03) # 左右搖晃的頻率
        self.sway_range = random.uniform(40, 150) # 左右搖晃的幅度
        self.spin_speed = random.uniform(0.01, 0.05) # 葉片旋轉/翻轉的速度
        
        # 初始向位偏移
        self.time_offset = random.uniform(0, 100)
        self.angle_offset = random.uniform(0, math.pi * 2)
        
        # 明亮、充滿生命力的淺綠/黃綠/薄荷配色庫
        colors = ["#a8e6cf", "#dcedc1", "#88d8b0", "#c1dfc4", "#a3e4d7", "#abebc6"]
        self.color = random.choice(colors)
        
        # 建立多邊形 (移除 stipple 點陣屬性，讓樹葉變成完全平滑、清晰的實心色彩)
        self.id = self.canvas.create_polygon(0, 0, 0, 0, 0, 0, fill=self.color, outline="")
        
    def _get_leaf_points(self, cx, cy, angle, scale, squeeze):
        """
        利用極座標方程式繪製兩端尖銳的葉子形狀
        r = a * sin(2*theta) 的變形，或是利用兩段貝茲圓弧近似
        我們這裡用更簡單可靠的橢圓擠壓變形法
        """
        points = []
        resolution = 12 # 取 12 個頂點畫出平滑的葉子(足夠了，太多會降 FPS)
        
        # 建立一個菱形/橢圓混和的基礎形狀 (葉片)
        for i in range(resolution):
            t = (i / resolution) * math.pi * 2
            # 基礎的瘦長橢圓 (葉身)
            px = math.sin(t) * (scale * 0.3)  # 寬度
            py = math.cos(t) * scale          # 長度
            
            # 將兩端捏尖 (利用 cos 讓中間胖，兩端細)
            # px *= (1 - 0.5 * math.cos(t))
            
            # 模擬 3D 翻轉 (隨著自轉壓縮 X 軸)
            px *= math.cos(squeeze)
            
            # 旋轉矩陣 (葉子本身的傾斜角度)
            rx = px * math.cos(angle) - py * math.sin(angle)
            ry = px * math.sin(angle) + py * math.cos(angle)
            
            # 加上畫布的絕對位置
            points.append(cx + rx)
            points.append(cy + ry)
            
        return points
        
    def update(self, t):
        # 1. 物理運動：垂直下降
        self.y += self.fall_speed
        
        # 2. 物理飄逸：橫向正弦波微風搖曳
        cx = self.x + math.sin((t + self.time_offset) * self.sway_speed) * self.sway_range
        cy = self.y
        
        # 若掉出畫面下方，則重新從頂部生成
        if cy > self.sh + self.size:
            self.y = -self.size * 3
            self.x = random.uniform(0, self.sw)
            self.time_offset = random.uniform(0, 100) # 重置搖擺參數避免重複
            
        # 3. 葉片姿態：旋轉與翻轉 (Squeeze)
        # 葉片迎風的傾斜角 (隨風搖擺的方向而改變)
        lean_angle = math.cos((t + self.time_offset) * self.sway_speed) * 0.5
        current_angle = self.angle_offset + lean_angle
        # 模擬 3D 在空中翻滾的壓縮感
        squeeze = (t + self.time_offset) * self.spin_speed
        
        # 4. 計算幾何樹葉多邊形頂點
        points = self._get_leaf_points(cx, cy, current_angle, self.size, squeeze)
        
        # 5. 更新畫布物件座標
        self.canvas.coords(self.id, *points)

# ================= 視窗類別 =================

class CenterReminderDialog:
    """畫面正中央的明亮提醒卡片"""
    def __init__(self, controller):
        self.controller = controller
        self.window = tk.Toplevel()
        self.window.withdraw()
        self.window.overrideredirect(True) # 無邊框
        self.window.attributes("-topmost", True)
        self.window.configure(bg="#ffffff") # 明亮白底卡片
        
        title_font = ("Microsoft JhengHei", 18, "bold")
        sub_font = ("Microsoft JhengHei", 12)
        btn_font = ("Microsoft JhengHei", 11, "bold")
        
        # 外框 (淺灰邊界，營造精緻感)
        frame = tk.Frame(self.window, bg="#ffffff", highlightbackground="#e0e0e0", highlightthickness=1)
        frame.pack(fill=tk.BOTH, expand=True)

        lbl_title = tk.Label(frame, text="護眼時間到了", font=title_font, fg="#2c3e50", bg="#ffffff")
        lbl_title.pack(pady=(35, 10))
        
        lbl_msg = tk.Label(frame, text="您已經連續盯著螢幕一段時間了。\n給眼睛幾秒鐘，跟我一起深呼吸吧！", 
                           font=sub_font, fg="#7f8c8d", bg="#ffffff", justify=tk.CENTER)
        lbl_msg.pack(padx=30, pady=(0, 30))

        btn_frame = tk.Frame(frame, bg="#ffffff")
        btn_frame.pack(fill=tk.X, padx=40, pady=(0, 35))

        # 主按鈕：寬大、顯眼綠色
        btn_rest = tk.Button(btn_frame, text="開始放鬆 (20秒)", font=btn_font, bg="#27ae60", fg="white", 
                             relief=tk.FLAT, cursor="hand2", command=self.on_rest, activebackground="#2ecc71", pady=10)
        btn_rest.pack(side=tk.TOP, expand=True, fill=tk.X, pady=(0, 15))

        # 副按鈕：淺灰色文字，低調不搶眼
        btn_snooze = tk.Button(btn_frame, text="稍後提醒 (5分鐘)", font=("Microsoft JhengHei", 10), bg="#ffffff", fg="#95a5a6", 
                               relief=tk.FLAT, cursor="hand2", command=self.on_snooze, activebackground="#f5f6fa", activeforeground="#7f8c8d", pady=5)
        btn_snooze.pack(side=tk.TOP, expand=True, fill=tk.X)

    def show(self):
        w, h = 420, 320
        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        # 置中使用公式 (螢幕寬度-視窗寬度)/2
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
    """全螢幕明亮動態放鬆視窗"""
    def __init__(self, controller):
        self.controller = controller
        self.window = tk.Toplevel()
        self.window.withdraw()
        self.window.attributes("-topmost", True)
        self.window.attributes("-fullscreen", True)
        self.bg_color = "#e8f5e9" # 淺薄荷綠至白色的清新底色感
        self.window.configure(bg=self.bg_color) 
        
        # 建立動畫畫布
        self.canvas = tk.Canvas(self.window, bg=self.bg_color, highlightthickness=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # 取消白色生硬方塊背景，改用 Canvas 直接繪製帶有圓角的無框半透明底層
        # 或者更優雅的做法：乾脆去掉背景框，直接讓文字陰影或粗體浮在背景上。
        # 這裡我們採取不使用 Frame 方塊，直接用 Canvas widget 來呈現大氣的文字。
        title_font = ("Microsoft JhengHei", 36)
        
        # 對文字作微小的一點陰影可以確保可讀性，但移除後面死板的色塊
        self.txt_shadow = self.canvas.create_text(
            self.window.winfo_screenwidth()//2 + 2,
            self.window.winfo_screenheight()//2 + 2,
            text="", font=title_font, fill="#c8e6c9", justify=tk.CENTER
        )
        self.txt_main = self.canvas.create_text(
            self.window.winfo_screenwidth()//2,
            self.window.winfo_screenheight()//2,
            text="", font=title_font, fill="#2c3e50", justify=tk.CENTER
        )
        
        # 加入極簡的打叉按鈕 
        btn_font = ("Segoe UI", 24) 
        self.btn_quit = tk.Button(self.window, text="✕", font=btn_font, bg=self.bg_color, fg="#b0bec5", 
                             relief=tk.FLAT, cursor="hand2", command=self.controller.quit_app,
                             activebackground="#c8e6c9", activeforeground="#2c3e50")
        self.btn_quit.place(relx=1.0, rely=0.0, anchor="ne", x=-30, y=30)
        
        # 綁定 Hover 事件
        self.btn_quit.bind("<Enter>", self.on_quit_hover)
        self.btn_quit.bind("<Leave>", self.on_quit_leave)
        
        self.leaves = []
        self.animating = False
        self.start_time = 0

    def on_quit_hover(self, e):
        self.btn_quit.config(fg="#2c3e50")

    def on_quit_leave(self, e):
        self.btn_quit.config(fg="#b0bec5")

    def init_geometry(self):
        self.canvas.delete("all")
        # 重新建立文字物件（因為 delete all 會清空）
        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        
        title_font = ("Microsoft JhengHei", 36)
        self.txt_shadow = self.canvas.create_text(
            sw//2 + 2, sh//2 + 2, text="", font=title_font, fill="#c8e6c9", justify=tk.CENTER
        )
        self.txt_main = self.canvas.create_text(
            sw//2, sh//2, text="", font=title_font, fill="#2c3e50", justify=tk.CENTER
        )
        
        # 增加飄落樹葉的數量以營造茂盛紛飛感 (約30片)
        self.leaves = [Leaf(self.canvas, sw, sh) for _ in range(30)]
        
        # 確保文字永遠在最上層 (畫布物件)
        self.canvas.tag_raise(self.txt_shadow)
        self.canvas.tag_raise(self.txt_main)
        
    def _update_text(self, text):
        self.canvas.itemconfig(self.txt_shadow, text=text)
        self.canvas.itemconfig(self.txt_main, text=text)
        
    def _animation_loop(self):
        if not self.animating:
            return
        
        current_time = time.time() - self.start_time
        for leaf in self.leaves:
            # 乘以較小的常數讓時間流動感非常溫和
            leaf.update(current_time * 15) 
            
        self.window.after(33, self._animation_loop)

    def show(self):
        self.window.update_idletasks() # 確保取得螢幕正確大小
        self.init_geometry()
        self.animating = True
        self.start_time = time.time()
        
        self.window.deiconify()
        self.window.focus_force()
        self.window.attributes("-topmost", True)
        
        self._update_text("放空思緒，讓心跳跟著微風慢下來...")
        
        # 啟動動畫與倒數
        self._animation_loop()
        self._countdown_step(BREAK_DURATION)

    def hide(self):
        self.animating = False
        self.window.withdraw()

    def _countdown_step(self, remaining):
        if remaining > 0:
            self._update_text(f"放空思緒，讓心跳跟著微風慢下來...\n\n剩 餘 {remaining} 秒")
            self.window.after(1000, self._countdown_step, remaining - 1)
        else:
            self._update_text("\n\n充電完成，回到工作站！\n\n")
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
            self.window.after(2000, self.finish)

    def finish(self):
        self.hide()
        self.controller.finish_break()


# ================= 主控制器 =================
class EyesProtectorController:
    def __init__(self, root):
        self.root = root
        self.root.withdraw() # 隱藏主根視窗
        
        self.dialog = CenterReminderDialog(self)
        self.fullscreen = FullScreenBreak(self)
        
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
                
            if is_fullscreen_or_busy():
                self.time_elapsed = 0
                continue
                
            self.time_elapsed += POLL_INTERVAL
            if self.time_elapsed >= self.target_interval:
                self.state = "DIALOG_VISIBLE"
                self.root.after(0, self.dialog.show)

    def snooze(self):
        self.time_elapsed = 0
        self.target_interval = SNOOZE_INTERVAL
        self.state = "RUNNING"

    def start_full_break(self):
        self.state = "BREAKING"
        self.root.after(0, self.fullscreen.show)

    def finish_break(self):
        self.time_elapsed = 0
        self.target_interval = BREAK_INTERVAL
        self.state = "RUNNING"
        
    def quit_app(self):
        self.running = False
        self.dialog.window.destroy()
        self.fullscreen.window.destroy()
        self.root.destroy()
        sys.exit(0)


if __name__ == "__main__":
    root = tk.Tk()
    app = EyesProtectorController(root)
    root.mainloop()
