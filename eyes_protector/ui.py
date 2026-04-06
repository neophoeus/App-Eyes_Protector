import tkinter as tk

from .platform_utils import get_window_dpi_scale, safe_play_sound
from .ui_metrics import (
    build_floating_widget_metrics,
    build_fullscreen_layout,
    build_reminder_dialog_metrics,
    center_window_position,
    get_round_rect_points,
    scale_px,
)


FULLSCREEN_COPY = {
    "countdown": "每20分鐘，花20秒鐘，看20呎外",
    "complete": "休息完成，慢慢回到工作",
    "skipped": "已返回工作，稍後會再提醒。",
}


def _expand_box(box, delta):
    return (box[0] - delta, box[1] - delta, box[2] + delta, box[3] + delta)


def _relative_point(box, x_ratio, y_ratio):
    x1, y1, x2, y2 = box
    width = x2 - x1
    height = y2 - y1
    return (x1 + (width * x_ratio), y1 + (height * y_ratio))


class CenterReminderDialog:
    def __init__(self, controller):
        self.controller = controller
        self.window = tk.Toplevel(controller.root)
        self.window.withdraw()
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(bg="#ffffff")
        self.scale = get_window_dpi_scale(self.window)
        self.metrics = build_reminder_dialog_metrics(self.scale)
        title_font = ("Microsoft JhengHei UI", 18, "bold")
        sub_font = ("Microsoft JhengHei UI", 12)
        btn_font = ("Microsoft JhengHei UI", 11, "bold")
        frame = tk.Frame(
            self.window,
            bg="#ffffff",
            highlightbackground="#e0e0e0",
            highlightthickness=self.metrics.border_width,
        )
        frame.pack(fill=tk.BOTH, expand=True)
        lbl_title = tk.Label(
            frame, text="護眼時間到了", font=title_font, fg="#2c3e50", bg="#ffffff"
        )
        lbl_title.pack(pady=(self.metrics.title_top_pad, self.metrics.title_bottom_pad))
        lbl_msg = tk.Label(
            frame,
            text="您已經連續盯著螢幕一段時間了。\n給眼睛幾秒鐘，跟我一起深呼吸吧！",
            font=sub_font,
            fg="#7f8c8d",
            bg="#ffffff",
            justify=tk.CENTER,
        )
        lbl_msg.pack(
            padx=self.metrics.message_pad_x,
            pady=(0, self.metrics.message_bottom_pad),
        )
        btn_frame = tk.Frame(frame, bg="#ffffff")
        btn_frame.pack(
            fill=tk.X,
            padx=self.metrics.button_pad_x,
            pady=(0, self.metrics.button_bottom_pad),
        )
        btn_rest = tk.Button(
            btn_frame,
            text="開始放鬆 (20秒)  Enter",
            font=btn_font,
            bg="#27ae60",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.on_rest,
            activebackground="#2ecc71",
            pady=self.metrics.primary_button_pad_y,
        )
        btn_rest.pack(
            side=tk.TOP,
            expand=True,
            fill=tk.X,
            pady=(0, self.metrics.primary_button_spacing),
        )
        btn_snooze = tk.Button(
            btn_frame,
            text="稍後提醒 (5分鐘)  Esc",
            font=("Microsoft JhengHei UI", 10),
            bg="#ffffff",
            fg="#95a5a6",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.on_snooze,
            activebackground="#f5f6fa",
            activeforeground="#7f8c8d",
            pady=self.metrics.secondary_button_pad_y,
        )
        btn_snooze.pack(side=tk.TOP, expand=True, fill=tk.X)
        self.window.bind("<Return>", lambda e: self.on_rest())
        self.window.bind("<Escape>", lambda e: self.on_snooze())

    def show(self):
        self.scale = get_window_dpi_scale(self.window)
        self.metrics = build_reminder_dialog_metrics(self.scale)
        w, h = self.metrics.width, self.metrics.height
        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        x, y = center_window_position(sw, sh, w, h)
        self.window.geometry(f"{w}x{h}+{x}+{y}")
        self.window.deiconify()
        self.window.focus_force()
        safe_play_sound("SystemAsterisk")

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
        self.window = tk.Toplevel(controller.root)
        self.window.withdraw()
        self.window.attributes("-topmost", True)
        self.window.attributes("-fullscreen", True)
        self.bg_color = "#6f8661"
        self.guide_color = "#dbe7b2"
        self.close_hover_color = "#8ea283"
        self.window.configure(bg=self.bg_color)
        self.canvas = tk.Canvas(self.window, bg=self.bg_color, highlightthickness=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self._countdown_job = None
        self._finish_job = None
        self._session_id = 0
        self.scale = 1.0
        self.layout = None

    def _refresh_layout(self):
        self.scale = get_window_dpi_scale(self.window)
        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        self.layout = build_fullscreen_layout(sw, sh, self.scale)
        return sw, sh

    def _set_close_chip_hover(self, hovered):
        self.canvas.itemconfig(
            self.close_chip_bg_id,
            state="normal" if hovered else "hidden",
            fill=self.close_hover_color,
            outline="",
        )
        self.canvas.itemconfig("close_chip_icon", fill="#ffffff")

    def init_geometry(self):
        self.canvas.delete("all")
        sw, sh = self._refresh_layout()
        layout = self.layout
        timer_font_size = max(96, scale_px(168, self.scale))
        guide_font_size = max(18, scale_px(18, self.scale))
        guide_gap = max(scale_px(56, self.scale), timer_font_size // 3)
        close_stroke_width = max(2, scale_px(2.5, self.scale))
        close_icon_inset = max(scale_px(11, self.scale), layout.close_radius // 2)
        close_x1 = layout.close_center_x - layout.close_radius
        close_y1 = layout.close_center_y - layout.close_radius
        close_x2 = layout.close_center_x + layout.close_radius
        close_y2 = layout.close_center_y + layout.close_radius
        self.window.configure(bg=self.bg_color)
        self.canvas.configure(bg=self.bg_color)
        self.canvas.create_rectangle(0, 0, sw, sh, fill=self.bg_color, outline="")
        timer_probe_id = self.canvas.create_text(
            layout.timer_x,
            layout.timer_y,
            text="00",
            font=("Segoe UI", timer_font_size, "bold"),
            fill=self.bg_color,
            justify=tk.CENTER,
        )
        timer_bbox = self.canvas.bbox(timer_probe_id)
        self.canvas.delete(timer_probe_id)
        guide_y = layout.guide_y
        if timer_bbox is not None:
            guide_y = timer_bbox[3] + guide_gap
        self.txt_timer = self.canvas.create_text(
            layout.timer_x,
            layout.timer_y,
            text="",
            font=("Segoe UI", timer_font_size, "bold"),
            fill="#ffffff",
            justify=tk.CENTER,
        )
        self.guide_text_id = self.canvas.create_text(
            layout.guide_x,
            guide_y,
            text="",
            font=("Microsoft JhengHei UI", guide_font_size, "bold"),
            fill=self.guide_color,
            anchor="n",
            justify=tk.CENTER,
            width=layout.guide_width,
        )
        self.close_chip_bg_id = self.canvas.create_oval(
            close_x1,
            close_y1,
            close_x2,
            close_y2,
            fill=self.guide_color,
            outline="",
            width=0,
            state="hidden",
            tags="close_chip",
        )
        self.canvas.create_line(
            close_x1 + close_icon_inset,
            close_y1 + close_icon_inset,
            close_x2 - close_icon_inset,
            close_y2 - close_icon_inset,
            fill="#ffffff",
            width=close_stroke_width,
            capstyle=tk.ROUND,
            tags=("close_chip", "close_chip_icon"),
        )
        self.canvas.create_line(
            close_x2 - close_icon_inset,
            close_y1 + close_icon_inset,
            close_x1 + close_icon_inset,
            close_y2 - close_icon_inset,
            fill="#ffffff",
            width=close_stroke_width,
            capstyle=tk.ROUND,
            tags=("close_chip", "close_chip_icon"),
        )
        self.canvas.tag_bind(
            "close_chip", "<ButtonRelease-1>", lambda e: self.finish_early()
        )
        self.canvas.tag_bind(
            "close_chip",
            "<Enter>",
            lambda e: self._set_close_chip_hover(True),
        )
        self.canvas.tag_bind(
            "close_chip",
            "<Leave>",
            lambda e: self._set_close_chip_hover(False),
        )
        self._apply_break_copy("countdown")
        self.canvas.tag_raise(self.txt_timer)
        self.canvas.tag_raise(self.guide_text_id)
        self.canvas.tag_raise(self.close_chip_bg_id)
        self.canvas.tag_raise("close_chip_icon")

    def _cancel_jobs(self):
        for job_name in ("_countdown_job", "_finish_job"):
            job_id = getattr(self, job_name)
            if job_id is None:
                continue
            try:
                self.window.after_cancel(job_id)
            except tk.TclError:
                pass
            setattr(self, job_name, None)

    def show(self):
        self._session_id += 1
        self._cancel_jobs()
        self.window.withdraw()
        self.window.update_idletasks()
        self.init_geometry()
        session_id = self._session_id
        self.window.deiconify()
        self.window.focus_force()
        self.window.attributes("-topmost", True)
        self._countdown_step(self.controller.config.break_duration, session_id)

    def hide(self):
        self._session_id += 1
        self._cancel_jobs()
        self.window.withdraw()

    def _apply_break_copy(self, state_name):
        self.canvas.itemconfig(self.guide_text_id, text=FULLSCREEN_COPY[state_name])

    def _countdown_step(self, remaining, session_id):
        if session_id != self._session_id:
            return
        if remaining > 0:
            self._apply_break_copy("countdown")
            self.canvas.itemconfig(self.txt_timer, text=f"{remaining:02d}")
            self._countdown_job = self.window.after(
                1000, self._countdown_step, remaining - 1, session_id
            )
            return
        self._countdown_job = None
        self._apply_break_copy("complete")
        self.canvas.itemconfig(self.txt_timer, text="00")
        safe_play_sound("SystemAsterisk")
        self._finish_job = self.window.after(2000, self.finish)

    def finish_early(self):
        if self.window.state() == "withdrawn":
            return
        self._cancel_jobs()
        self._apply_break_copy("skipped")
        self.canvas.itemconfig(self.txt_timer, text="")
        safe_play_sound("SystemAsterisk")
        self._finish_job = self.window.after(1000, self.finish)

    def finish(self):
        self.hide()
        self.controller.finish_break()


class FloatingWidget:
    def __init__(self, controller):
        self.controller = controller
        self.window = tk.Toplevel(controller.root)
        self.window.attributes("-topmost", True)
        self.window.overrideredirect(True)
        self.window.attributes("-transparentcolor", "#000000")
        self.window.attributes("-alpha", 0.6)
        self.bg_color_normal = "#e8f5e9"
        self.bg_color_hover = "#ffffff"
        self.scale = get_window_dpi_scale(self.window)
        self.metrics = build_floating_widget_metrics(self.scale)
        self.canvas = tk.Canvas(
            self.window,
            bg="#000000",
            highlightthickness=0,
            width=self.metrics.window_width,
            height=self.metrics.height,
        )
        self.canvas.pack()
        self.normal_coords = self.metrics.collapsed_rect
        self.hover_coords = self.metrics.expanded_rect
        points = get_round_rect_points(*self.normal_coords, self.metrics.radius)
        self.bg_id = self.canvas.create_polygon(
            points,
            smooth=True,
            fill=self.bg_color_normal,
            outline="#a5d6a7",
            width=self.metrics.outline_width,
        )
        self.txt_label = self.canvas.create_text(
            self.metrics.label_x,
            self.metrics.center_y,
            text="",
            anchor="w",
            font=("Microsoft JhengHei UI", 10, "bold"),
            fill="#27ae60",
        )
        self.btn_pause = self.canvas.create_rectangle(
            *self.metrics.pause_box,
            outline="",
            fill="",
            state="hidden",
            tags=("pause_hitbox",),
        )
        self.btn_close = self.canvas.create_rectangle(
            *self.metrics.close_box,
            outline="",
            fill="",
            state="hidden",
            tags=("close_hitbox",),
        )
        self.canvas.tag_bind(
            "pause_hitbox",
            "<Enter>",
            lambda e: self._set_control_hover("pause", True),
        )
        self.canvas.tag_bind(
            "pause_hitbox",
            "<Leave>",
            lambda e: self._set_control_hover("pause", False),
        )
        self.canvas.tag_bind(
            "close_hitbox",
            "<Enter>",
            lambda e: self._set_control_hover("close", True),
        )
        self.canvas.tag_bind(
            "close_hitbox",
            "<Leave>",
            lambda e: self._set_control_hover("close", False),
        )
        self.canvas.bind("<ButtonPress-1>", self.start_move)
        self.canvas.bind("<B1-Motion>", self.do_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_click)
        self.canvas.bind("<Enter>", self.on_hover)
        self.canvas.bind("<Leave>", self.on_leave)
        self.canvas.bind("<Motion>", self.on_motion)
        self.window.update_idletasks()
        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        w, h = self.metrics.window_width, self.metrics.height
        x = sw - w - self.metrics.margin_right
        y = sh - h - self.metrics.margin_bottom
        self.window.geometry(f"{w}x{h}+{x}+{y}")
        self._x = 0
        self._y = 0
        self._dragged = False
        self._collapse_job = None
        self._expanded = False
        self._pause_hovered = False
        self._close_hovered = False
        self._pressed_control = None
        self.update_pause_ui()

    def _control_from_hit_items(self, hit_items):
        for item_id in hit_items:
            tags = self.canvas.gettags(item_id)
            if (
                "pause_control" in tags
                or "pause_hitbox" in tags
                or item_id == self.btn_pause
            ):
                return "pause"
            if (
                "close_control" in tags
                or "close_hitbox" in tags
                or item_id == self.btn_close
            ):
                return "close"
        return None

    def _reset_pointer_state(self):
        self._pressed_control = None
        self._dragged = False

    def _raise_control_hitboxes(self):
        self.canvas.tag_raise(self.btn_pause)
        self.canvas.tag_raise(self.btn_close)

    def _cancel_collapse(self):
        if self._collapse_job is None:
            return
        try:
            self.window.after_cancel(self._collapse_job)
        except tk.TclError:
            pass
        self._collapse_job = None

    def _pointer_inside_widget(self):
        try:
            pointer_widget = self.window.winfo_containing(
                *self.window.winfo_pointerxy()
            )
        except tk.TclError:
            return False
        if pointer_widget is None:
            return False
        try:
            return pointer_widget.winfo_toplevel() == self.window
        except tk.TclError:
            return False

    def _collapse_if_pointer_left(self):
        self._collapse_job = None
        if self._pointer_inside_widget():
            return
        old_points = get_round_rect_points(*self.normal_coords, self.metrics.radius)
        self.window.attributes("-alpha", 0.6)
        self.canvas.coords(self.bg_id, *old_points)
        self.canvas.itemconfig(self.bg_id, fill=self.bg_color_normal, outline="#a5d6a7")
        self._expanded = False
        self._pause_hovered = False
        self._close_hovered = False
        self.canvas.itemconfig(self.txt_label, text="")
        self.canvas.itemconfig(self.btn_pause, state="hidden")
        self.canvas.itemconfig(self.btn_close, state="hidden")
        self.canvas.delete("pause_control")
        self.canvas.delete("close_control")
        self.update_pause_ui()
        self.window.config(cursor="arrow")

    def _draw_eye(self, state):
        self.canvas.delete("icon_parts")
        box = self.metrics.icon_box
        stroke = self.metrics.eye_stroke_width
        if state == "open":
            upper = [
                *_relative_point(box, 0.15, 0.55),
                *_relative_point(box, 0.50, 0.25),
                *_relative_point(box, 0.85, 0.55),
            ]
            lower = [
                *_relative_point(box, 0.15, 0.55),
                *_relative_point(box, 0.50, 0.85),
                *_relative_point(box, 0.85, 0.55),
            ]
            self.canvas.create_line(
                *upper,
                smooth=True,
                fill="#2c3e50",
                width=stroke,
                tags="icon_parts",
            )
            self.canvas.create_line(
                *lower,
                smooth=True,
                fill="#2c3e50",
                width=stroke,
                tags="icon_parts",
            )
            pupil_top_left = _relative_point(box, 0.38, 0.40)
            pupil_bottom_right = _relative_point(box, 0.62, 0.66)
            self.canvas.create_oval(
                *pupil_top_left,
                *pupil_bottom_right,
                fill="#2c3e50",
                outline="",
                tags="icon_parts",
            )
            highlight_top_left = _relative_point(box, 0.47, 0.45)
            highlight_bottom_right = _relative_point(box, 0.56, 0.54)
            self.canvas.create_oval(
                *highlight_top_left,
                *highlight_bottom_right,
                fill="#ffffff",
                outline="",
                tags="icon_parts",
            )
            self.canvas.create_line(
                *_relative_point(box, 0.25, 0.46),
                *_relative_point(box, 0.17, 0.36),
                fill="#2c3e50",
                width=stroke,
                capstyle=tk.ROUND,
                tags="icon_parts",
            )
            self.canvas.create_line(
                *_relative_point(box, 0.35, 0.40),
                *_relative_point(box, 0.29, 0.28),
                fill="#2c3e50",
                width=stroke,
                capstyle=tk.ROUND,
                tags="icon_parts",
            )
            self.canvas.create_line(
                *_relative_point(box, 0.50, 0.37),
                *_relative_point(box, 0.50, 0.23),
                fill="#2c3e50",
                width=stroke,
                capstyle=tk.ROUND,
                tags="icon_parts",
            )
            self.canvas.create_line(
                *_relative_point(box, 0.65, 0.40),
                *_relative_point(box, 0.71, 0.28),
                fill="#2c3e50",
                width=stroke,
                capstyle=tk.ROUND,
                tags="icon_parts",
            )
            self.canvas.create_line(
                *_relative_point(box, 0.75, 0.46),
                *_relative_point(box, 0.83, 0.36),
                fill="#2c3e50",
                width=stroke,
                capstyle=tk.ROUND,
                tags="icon_parts",
            )
        elif state == "closed":
            self.canvas.create_line(
                *_relative_point(box, 0.15, 0.42),
                *_relative_point(box, 0.50, 0.72),
                *_relative_point(box, 0.85, 0.42),
                smooth=True,
                fill="#f39c12",
                width=stroke,
                tags="icon_parts",
            )
            self.canvas.create_line(
                *_relative_point(box, 0.25, 0.48),
                *_relative_point(box, 0.17, 0.56),
                fill="#f39c12",
                width=stroke,
                capstyle=tk.ROUND,
                tags="icon_parts",
            )
            self.canvas.create_line(
                *_relative_point(box, 0.35, 0.54),
                *_relative_point(box, 0.29, 0.66),
                fill="#f39c12",
                width=stroke,
                capstyle=tk.ROUND,
                tags="icon_parts",
            )
            self.canvas.create_line(
                *_relative_point(box, 0.50, 0.56),
                *_relative_point(box, 0.50, 0.70),
                fill="#f39c12",
                width=stroke,
                capstyle=tk.ROUND,
                tags="icon_parts",
            )
            self.canvas.create_line(
                *_relative_point(box, 0.65, 0.54),
                *_relative_point(box, 0.71, 0.66),
                fill="#f39c12",
                width=stroke,
                capstyle=tk.ROUND,
                tags="icon_parts",
            )
            self.canvas.create_line(
                *_relative_point(box, 0.75, 0.48),
                *_relative_point(box, 0.83, 0.56),
                fill="#f39c12",
                width=stroke,
                capstyle=tk.ROUND,
                tags="icon_parts",
            )

    def _set_control_hover(self, control_name, hovered):
        if control_name == "pause":
            if self._pause_hovered == hovered:
                return
            self._pause_hovered = hovered
        else:
            if self._close_hovered == hovered:
                return
            self._close_hovered = hovered
        if self._expanded:
            self._draw_pause_control()
            self._draw_close_control()
            self._raise_control_hitboxes()

    def _draw_pause_control(self):
        self.canvas.delete("pause_control")
        if not self._expanded:
            return
        box = self.metrics.pause_box
        paused = getattr(self.controller, "paused", False)
        accent = "#2ecc71" if paused else "#f39c12"
        fill_color = "#f2fcf5" if self._pause_hovered else "#ffffff"
        self.canvas.create_oval(
            *box,
            fill=fill_color,
            outline="",
            width=0,
            tags="pause_control",
        )
        x1, y1, x2, y2 = box
        width = x2 - x1
        height = y2 - y1
        if paused:
            self.canvas.create_polygon(
                x1 + (width * 0.42),
                y1 + (height * 0.30),
                x1 + (width * 0.42),
                y1 + (height * 0.70),
                x1 + (width * 0.68),
                y1 + (height * 0.50),
                fill=accent,
                outline=accent,
                tags="pause_control",
            )
            return
        stroke = self.metrics.control_stroke_width
        self.canvas.create_line(
            x1 + (width * 0.38),
            y1 + (height * 0.30),
            x1 + (width * 0.38),
            y1 + (height * 0.70),
            fill=accent,
            width=stroke,
            capstyle=tk.ROUND,
            tags="pause_control",
        )
        self.canvas.create_line(
            x1 + (width * 0.62),
            y1 + (height * 0.30),
            x1 + (width * 0.62),
            y1 + (height * 0.70),
            fill=accent,
            width=stroke,
            capstyle=tk.ROUND,
            tags="pause_control",
        )

    def _draw_close_control(self):
        self.canvas.delete("close_control")
        if not self._expanded:
            return
        box = self.metrics.close_box
        fill_color = "#fff0f0" if self._close_hovered else "#ffffff"
        self.canvas.create_oval(
            *box,
            fill=fill_color,
            outline="",
            width=0,
            tags="close_control",
        )
        stroke = self.metrics.control_stroke_width
        self.canvas.create_line(
            *_relative_point(box, 0.35, 0.35),
            *_relative_point(box, 0.65, 0.65),
            fill="#e74c3c",
            width=stroke,
            capstyle=tk.ROUND,
            tags="close_control",
        )
        self.canvas.create_line(
            *_relative_point(box, 0.65, 0.35),
            *_relative_point(box, 0.35, 0.65),
            fill="#e74c3c",
            width=stroke,
            capstyle=tk.ROUND,
            tags="close_control",
        )

    def update_pause_ui(self):
        if getattr(self.controller, "paused", False):
            self._draw_eye("closed")
            if self._expanded:
                self.canvas.itemconfig(self.txt_label, text="已暫停", fill="#f39c12")
            self._draw_pause_control()
            self._draw_close_control()
            self._raise_control_hitboxes()
            return
        self._draw_eye("open")
        if self._expanded:
            self.canvas.itemconfig(self.txt_label, text="保護中", fill="#27ae60")
        self._draw_pause_control()
        self._draw_close_control()
        self._raise_control_hitboxes()

    def start_move(self, event):
        self._cancel_collapse()
        hit_items = set(
            self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        )
        control_name = self._control_from_hit_items(hit_items)
        if control_name == "pause":
            self._pressed_control = control_name
            self._dragged = False
            self.controller.toggle_pause()
            return "break"
        if control_name == "close":
            self._pressed_control = control_name
            self._dragged = False
            self.controller.quit_app()
            return "break"
        self._pressed_control = None
        self._x = event.x
        self._y = event.y
        self._dragged = False

    def do_move(self, event):
        if self._pressed_control is not None:
            return
        self._dragged = True
        deltax = event.x - self._x
        deltay = event.y - self._y
        x = self.window.winfo_x() + deltax
        y = self.window.winfo_y() + deltay
        self.window.geometry(f"+{x}+{y}")

    def on_click(self, event):
        self._pressed_control = None
        if self._dragged:
            self._dragged = False
            return
        if not self._expanded:
            return
        self._dragged = False

    def on_hover(self, _event):
        self._cancel_collapse()
        self.window.attributes("-alpha", 0.95)
        new_points = get_round_rect_points(*self.hover_coords, self.metrics.radius)
        self.canvas.coords(self.bg_id, *new_points)
        self.canvas.itemconfig(self.bg_id, fill=self.bg_color_hover, outline="#81c784")
        self._expanded = True
        self.canvas.itemconfig(self.btn_pause, state="normal")
        self.canvas.itemconfig(self.btn_close, state="normal")
        self.update_pause_ui()
        self._raise_control_hitboxes()
        self.window.config(cursor="hand2")

    def on_leave(self, _event):
        self._cancel_collapse()
        self._collapse_job = self.window.after(120, self._collapse_if_pointer_left)

    def on_motion(self, _event):
        self._cancel_collapse()

    def hide(self):
        self._cancel_collapse()
        self._pressed_control = None
        self._dragged = False
        if self.window.state() != "withdrawn":
            self.window.withdraw()

    def show(self):
        if self.window.state() == "withdrawn":
            self.window.deiconify()
