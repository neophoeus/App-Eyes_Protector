import tkinter as tk
import time
import math

from .platform_utils import (
    get_window_dpi_scale,
    safe_play_sound,
    set_window_click_through,
    remove_window_click_through,
)
from .ui_metrics import (
    build_floating_widget_metrics,
    build_fullscreen_layout,
    center_window_position,
    get_round_rect_points,
    scale_px,
    make_box,
)
from .i18n import t

# Forest Dark Mode Theme Colors
COLOR_SCREEN_BG = "#0d130f"
COLOR_CARD_BG = "#16201a"
COLOR_CARD_BORDER = "#28382e"
COLOR_TEXT_PRIMARY = "#e6f4ea"
COLOR_MINT_ACCENT = "#5cdb95"
COLOR_AMBER_WARNING = "#f39c12"
COLOR_RED_CLOSE = "#e74c3c"
COLOR_CLOSE_HOVER = "#243b2f"

COLOR_FLOATING_BG_NORMAL = "#16201a"
COLOR_FLOATING_BG_HOVER = "#1e2b23"
COLOR_FLOATING_BORDER_NORMAL = "#28382e"
COLOR_FLOATING_BORDER_HOVER = "#5cdb95"



def _expand_box(box, delta):
    return (box[0] - delta, box[1] - delta, box[2] + delta, box[3] + delta)


def _relative_point(box, x_ratio, y_ratio):
    x1, y1, x2, y2 = box
    width = x2 - x1
    height = y2 - y1
    return (x1 + (width * x_ratio), y1 + (height * y_ratio))


def _measure_text_width(text, font_family, font_size, is_bold, scale):
    try:
        from tkinter import font as tkfont
        f = tkfont.Font(family=font_family, size=font_size, weight="bold" if is_bold else "normal")
        return f.measure(text)
    except Exception:
        # Fallback estimation for tests where Tk context is not available
        base_size = abs(font_size) if font_size < 0 else int(font_size * 1.33)
        width = 0
        for char in text:
            if ord(char) > 127:
                width += base_size
            else:
                width += base_size * 0.55
        return scale_px(width, scale)


class FullScreenBreak:
    def __init__(self, controller):
        self.controller = controller
        self.window = tk.Toplevel(controller.root)
        self.window.attributes("-topmost", True)
        self.window.attributes("-fullscreen", True)
        self.bg_color = COLOR_SCREEN_BG
        self.close_hover_color = COLOR_CLOSE_HOVER
        self.window.configure(bg=self.bg_color)
        self.canvas = tk.Canvas(self.window, bg=self.bg_color, highlightthickness=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self._countdown_job = None
        self._finish_job = None
        self._session_id = 0
        self.scale = 1.0
        self.layout = None

        # Solid warning pill window at the top center
        self.warning_window = tk.Toplevel(controller.root)
        self.warning_window.attributes("-topmost", True)
        self.warning_window.overrideredirect(True)
        self.warning_window.attributes("-transparentcolor", "#000000")
        self.warning_window.configure(bg="#000000")
        self.warning_canvas = tk.Canvas(self.warning_window, bg="#000000", highlightthickness=0)
        self.warning_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # Pre-map the windows at startup to fully initialize root HWND wrapper structures,
        # then immediately withdraw them so they are hidden from the user.
        self.window.deiconify()
        self.warning_window.deiconify()
        self.window.update()
        self.warning_window.update()
        self.window.withdraw()
        self.warning_window.withdraw()

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

    def init_geometry(self, is_warning=False):
        self.canvas.delete("all")
        sw, sh = self._refresh_layout()
        layout = self.layout
        close_stroke_width = max(2, scale_px(2.5, self.scale))
        close_icon_inset = max(scale_px(11, self.scale), layout.close_radius // 2)
        close_x1 = layout.close_center_x - layout.close_radius
        close_y1 = layout.close_center_y - layout.close_radius
        close_x2 = layout.close_center_x + layout.close_radius
        close_y2 = layout.close_center_y + layout.close_radius
        
        self.window.configure(bg=self.bg_color)
        self.canvas.configure(bg=self.bg_color)
        self.canvas.create_rectangle(0, 0, sw, sh, fill=self.bg_color, outline="")
        
        if is_warning:
            # Minimalist countdown style in a solid 100% alpha window at the top center
            pill_w = scale_px(510, self.scale)
            pill_h = scale_px(40, self.scale)
            x = sw // 2 - pill_w // 2
            y = scale_px(40, self.scale)
            self.warning_window.geometry(f"{pill_w}x{pill_h}+{x}+{y}")
            
            self.warning_canvas.delete("all")
            self.warning_canvas.configure(width=pill_w, height=pill_h)
            
            # Warning pill background (thick bright green outline, green background)
            pill_points = get_round_rect_points(0, 0, pill_w, pill_h, pill_h // 2)
            self.warning_pill_id = self.warning_canvas.create_polygon(
                pill_points,
                fill="#113d23",
                outline=COLOR_MINT_ACCENT,
                width=max(2, scale_px(2.5, self.scale)),
                smooth=True,
            )
            
            self.warning_guide_text_id = self.warning_canvas.create_text(
                pill_w // 2,
                pill_h // 2,
                text="",
                font=("Microsoft JhengHei UI", -scale_px(17, self.scale), "bold"),
                fill="#ffffff",
                anchor="center",
                justify=tk.CENTER,
            )
            
            # Setup dummy/hidden elements on main canvas for compatibility/prevent errors
            self.active_arc_id = self.canvas.create_arc(
                0, 0, 0, 0, start=0, extent=0, style=tk.ARC, outline="", width=0, state="hidden"
            )
            self.txt_timer = self.canvas.create_text(
                0, 0, text="", state="hidden"
            )
            self.guide_text_id = self.canvas.create_text(
                0, 0, text="", state="hidden"
            )
            self.close_chip_bg_id = self.canvas.create_oval(
                0, 0, 0, 0, state="hidden"
            )
        else:
            # Redesigned solid background fullscreen layout (no central card)
            
            # Static background circle track
            self.canvas.create_oval(
                layout.ring_x1,
                layout.ring_y1,
                layout.ring_x2,
                layout.ring_y2,
                outline="#1d2e24",
                width=layout.ring_thickness,
            )
            
            # Active progress arc
            self.active_arc_id = self.canvas.create_arc(
                layout.ring_x1,
                layout.ring_y1,
                layout.ring_x2,
                layout.ring_y2,
                start=90,
                extent=360,
                style=tk.ARC,
                outline=COLOR_MINT_ACCENT,
                width=layout.ring_thickness,
            )
            
            # Countdown text
            self.txt_timer = self.canvas.create_text(
                layout.timer_x,
                layout.timer_y,
                text="",
                font=("Segoe UI", -layout.timer_font_size, "bold"),
                fill=COLOR_TEXT_PRIMARY,
                justify=tk.CENTER,
            )
            
            # Guide text
            guide_font_size = max(16, int(sh * 0.024))
            self.guide_text_id = self.canvas.create_text(
                layout.guide_x,
                layout.guide_y,
                text="",
                font=("Microsoft JhengHei UI", -guide_font_size, "bold"),
                fill=COLOR_MINT_ACCENT,
                anchor="n",
                justify=tk.CENTER,
                width=layout.guide_width,
            )
            
            # Close chip hover background
            self.close_chip_bg_id = self.canvas.create_oval(
                close_x1,
                close_y1,
                close_x2,
                close_y2,
                fill=self.close_hover_color,
                outline="",
                width=0,
                state="hidden",
                tags="close_chip",
            )
            
            # Close chip icon lines (X)
            self.canvas.create_line(
                close_x1 + close_icon_inset,
                close_y1 + close_icon_inset,
                close_x2 - close_icon_inset,
                close_y2 - close_icon_inset,
                fill=COLOR_RED_CLOSE,
                width=close_stroke_width,
                capstyle=tk.ROUND,
                tags=("close_chip", "close_chip_icon"),
            )
            self.canvas.create_line(
                close_x2 - close_icon_inset,
                close_y1 + close_icon_inset,
                close_x1 + close_icon_inset,
                close_y2 - close_icon_inset,
                fill=COLOR_RED_CLOSE,
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

    def show(self, is_warning=False):
        self._session_id += 1
        self._cancel_jobs()
        self.init_geometry(is_warning=is_warning)
        session_id = self._session_id
        if is_warning:
            self._last_warning_remaining = None
            self._last_warning_alpha = 0.0
            
            self.window.deiconify()
            self.warning_window.deiconify()
            self.window.update()  # Force drawing and window mapping
            self.warning_window.update()
            
            set_window_click_through(self.window)
            set_window_click_through(self.warning_window)
            
            self.window.attributes("-alpha", 0.0)
            self.warning_window.attributes("-alpha", 1.0)
            
            # Re-apply click-through after 50ms to ensure the OS wrapper window handles are fully linked
            self.window.after(50, lambda: set_window_click_through(self.window))
            self.warning_window.after(50, lambda: set_window_click_through(self.warning_window))
            
            # Record warning start time and kick off smooth 5Hz update job
            self._warning_start_time = time.time()
            self._warning_step(session_id)
        else:
            self.warning_window.withdraw()
            self.window.deiconify()
            self.window.update()  # Force drawing and window mapping
            remove_window_click_through(self.window)
            self.window.attributes("-alpha", 1.0)
            self.canvas.itemconfig("close_chip", state="normal")
            self.canvas.itemconfig(self.close_chip_bg_id, state="hidden")
            self.window.focus_force()
            self.window.attributes("-topmost", True)
            self._countdown_step(self.controller.config.break_duration, session_id)

    def hide(self):
        self._session_id += 1
        self._cancel_jobs()
        self.window.withdraw()
        self.warning_window.withdraw()

    def _apply_break_copy(self, state_name):
        self.canvas.itemconfig(self.guide_text_id, text=t(state_name))

    def _warning_step(self, session_id):
        if session_id != self._session_id:
            return
        total_dur = self.controller.config.warning_duration
        elapsed = time.time() - self._warning_start_time
        
        if elapsed < total_dur:
            # Smoothly transition alpha from 0.0 to 0.50
            current_alpha = 0.0 + 0.50 * (elapsed / total_dur)
            # Only update window alpha if it differs significantly (>= 0.02) or it's the first frame
            if self._last_warning_alpha is None or abs(current_alpha - self._last_warning_alpha) >= 0.02:
                self.window.attributes("-alpha", current_alpha)
                self._last_warning_alpha = current_alpha
            
            # Clockwise filling active arc
            extent = -360 * (elapsed / total_dur)
            self.canvas.itemconfig(self.active_arc_id, extent=extent, outline=COLOR_AMBER_WARNING)
            
            # Display ceiling rounded integer remaining seconds, only update text when it actually changes
            remaining = int(math.ceil(total_dur - elapsed))
            if remaining != self._last_warning_remaining:
                warning_text = t("warning_text", remaining=remaining)
                
                # Dynamic width adaptation for the warning pill banner
                text_width = _measure_text_width(warning_text, "Microsoft JhengHei UI", -scale_px(17, self.scale), True, self.scale)
                
                sw = self.window.winfo_screenwidth()
                pill_h = scale_px(40, self.scale)
                min_pill_w = scale_px(510, self.scale)
                pill_w = max(min_pill_w, text_width + scale_px(40, self.scale))
                
                x = sw // 2 - pill_w // 2
                y = scale_px(40, self.scale)
                self.warning_window.geometry(f"{pill_w}x{pill_h}+{x}+{y}")
                self.warning_canvas.configure(width=pill_w)
                
                pill_points = get_round_rect_points(0, 0, pill_w, pill_h, pill_h // 2)
                self.warning_canvas.coords(self.warning_pill_id, *pill_points)
                self.warning_canvas.coords(self.warning_guide_text_id, pill_w // 2, pill_h // 2)
                
                self.warning_canvas.itemconfig(self.warning_guide_text_id, text=warning_text, fill="#ffffff")
                self.canvas.itemconfig(self.txt_timer, text=f"{remaining:02d}", fill=COLOR_AMBER_WARNING)
                self._last_warning_remaining = remaining
            
            # Re-schedule after 200ms (5Hz) for buttery-smooth transition with low overhead
            self._countdown_job = self.window.after(
                200, self._warning_step, session_id
            )
            return
        self._countdown_job = None
        self.controller.start_full_break()

    def _countdown_step(self, remaining, session_id):
        if session_id != self._session_id:
            return
        if remaining > 0:
            total_dur = self.controller.config.break_duration
            extent = -360 * (remaining / total_dur)
            self.canvas.itemconfig(self.active_arc_id, extent=extent, outline=COLOR_MINT_ACCENT)
            
            self._apply_break_copy("countdown")
            self.canvas.itemconfig(self.txt_timer, text=f"{remaining:02d}", fill=COLOR_TEXT_PRIMARY)
            self.canvas.itemconfig(self.guide_text_id, fill=COLOR_MINT_ACCENT)
            self._countdown_job = self.window.after(
                1000, self._countdown_step, remaining - 1, session_id
            )
            return
        self._countdown_job = None
        self._apply_break_copy("complete")
        self.canvas.itemconfig(self.txt_timer, text="00", fill=COLOR_MINT_ACCENT)
        self.canvas.itemconfig(self.active_arc_id, extent=0)
        safe_play_sound("SystemAsterisk")
        self._finish_job = self.window.after(2000, self.finish)

    def finish_early(self):
        if self.window.state() == "withdrawn":
            return
        self._cancel_jobs()
        self._apply_break_copy("skipped")
        self.canvas.itemconfig(self.txt_timer, text="")
        self.canvas.itemconfig(self.active_arc_id, extent=0)
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
        self.window.attributes("-alpha", 0.75)
        self.bg_color_normal = COLOR_FLOATING_BG_NORMAL
        self.bg_color_hover = COLOR_FLOATING_BG_HOVER
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
            outline=COLOR_FLOATING_BORDER_NORMAL,
            width=self.metrics.outline_width,
        )
        self.txt_label = self.canvas.create_text(
            self.metrics.label_x,
            self.metrics.center_y,
            text="",
            anchor="w",
            font=("Microsoft JhengHei UI", 10, "bold"),
            fill=COLOR_MINT_ACCENT,
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
        w_collapsed = scale_px(44, self.scale)
        h = self.metrics.height
        x = sw - w_collapsed - self.metrics.margin_right
        y = sh - h - self.metrics.margin_bottom
        self.window.geometry(f"{w_collapsed}x{h}+{x}+{y}")
        self._x = 0
        self._y = 0
        self._dragged = False
        self._collapse_job = None
        self._expanded = False
        self._pause_hovered = False
        self._close_hovered = False
        self._pressed_control = None
        self.update_pause_ui()

    def _update_dynamic_layout(self):
        paused = getattr(self.controller, "paused", False)
        text = t("paused") if paused else t("protecting")
        
        text_width = _measure_text_width(text, "Microsoft JhengHei UI", 10, True, self.scale)
        
        scale = self.scale
        min_pause_x1 = scale_px(114, scale)
        pause_x1 = max(min_pause_x1, self.metrics.label_x + text_width + scale_px(8, scale))
        
        control_size = scale_px(32, scale)
        pause_x2 = pause_x1 + control_size
        pause_center_x = (pause_x1 + pause_x2) // 2
        
        close_x1 = pause_x2 + scale_px(8, scale)
        close_x2 = close_x1 + control_size
        close_center_x = (close_x1 + close_x2) // 2
        
        w_expanded = close_x2 + scale_px(9, scale)
        
        from dataclasses import replace
        
        expanded_rect = (
            scale_px(2, scale),
            scale_px(2, scale),
            w_expanded - scale_px(2, scale),
            self.metrics.height - scale_px(2, scale),
        )
        
        self.metrics = replace(
            self.metrics,
            window_width=w_expanded,
            expanded_rect=expanded_rect,
            pause_box=make_box(pause_center_x, self.metrics.center_y, control_size),
            close_box=make_box(close_center_x, self.metrics.center_y, control_size),
        )
        self.hover_coords = expanded_rect
        
        if self._expanded:
            self.canvas.configure(width=w_expanded)
            right_x = self.window.winfo_x() + self.window.winfo_width()
            h = self.metrics.height
            new_x = right_x - w_expanded
            y = self.window.winfo_y()
            self.window.geometry(f"{w_expanded}x{h}+{new_x}+{y}")
            
            new_points = get_round_rect_points(*expanded_rect, self.metrics.radius)
            self.canvas.coords(self.bg_id, *new_points)
            self.canvas.coords(self.btn_pause, *self.metrics.pause_box)
            self.canvas.coords(self.btn_close, *self.metrics.close_box)

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
        if self._dragged or self._pressed_control is not None:
            return
        old_points = get_round_rect_points(*self.normal_coords, self.metrics.radius)
        self.window.attributes("-alpha", 0.75)
        self.canvas.coords(self.bg_id, *old_points)
        self.canvas.itemconfig(self.bg_id, fill=self.bg_color_normal, outline=COLOR_FLOATING_BORDER_NORMAL)
        if self._expanded:
            # Resize window to collapsed width and slide right
            right_x = self.window.winfo_x() + self.window.winfo_width()
            w_collapsed = scale_px(44, self.scale)
            h = self.metrics.height
            new_x = right_x - w_collapsed
            y = self.window.winfo_y()
            self.window.geometry(f"{w_collapsed}x{h}+{new_x}+{y}")
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
                fill=COLOR_MINT_ACCENT,
                width=stroke,
                tags="icon_parts",
            )
            self.canvas.create_line(
                *lower,
                smooth=True,
                fill=COLOR_MINT_ACCENT,
                width=stroke,
                tags="icon_parts",
            )
            pupil_top_left = _relative_point(box, 0.38, 0.40)
            pupil_bottom_right = _relative_point(box, 0.62, 0.66)
            self.canvas.create_oval(
                *pupil_top_left,
                *pupil_bottom_right,
                fill=COLOR_MINT_ACCENT,
                outline="",
                tags="icon_parts",
            )
            highlight_top_left = _relative_point(box, 0.47, 0.45)
            highlight_bottom_right = _relative_point(box, 0.56, 0.54)
            self.canvas.create_oval(
                *highlight_top_left,
                *highlight_bottom_right,
                fill=COLOR_SCREEN_BG,
                outline="",
                tags="icon_parts",
            )
            self.canvas.create_line(
                *_relative_point(box, 0.25, 0.46),
                *_relative_point(box, 0.17, 0.36),
                fill=COLOR_MINT_ACCENT,
                width=stroke,
                capstyle=tk.ROUND,
                tags="icon_parts",
            )
            self.canvas.create_line(
                *_relative_point(box, 0.35, 0.40),
                *_relative_point(box, 0.29, 0.28),
                fill=COLOR_MINT_ACCENT,
                width=stroke,
                capstyle=tk.ROUND,
                tags="icon_parts",
            )
            self.canvas.create_line(
                *_relative_point(box, 0.50, 0.37),
                *_relative_point(box, 0.50, 0.23),
                fill=COLOR_MINT_ACCENT,
                width=stroke,
                capstyle=tk.ROUND,
                tags="icon_parts",
            )
            self.canvas.create_line(
                *_relative_point(box, 0.65, 0.40),
                *_relative_point(box, 0.71, 0.28),
                fill=COLOR_MINT_ACCENT,
                width=stroke,
                capstyle=tk.ROUND,
                tags="icon_parts",
            )
            self.canvas.create_line(
                *_relative_point(box, 0.75, 0.46),
                *_relative_point(box, 0.83, 0.36),
                fill=COLOR_MINT_ACCENT,
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
                fill=COLOR_AMBER_WARNING,
                width=stroke,
                tags="icon_parts",
            )
            self.canvas.create_line(
                *_relative_point(box, 0.25, 0.48),
                *_relative_point(box, 0.17, 0.56),
                fill=COLOR_AMBER_WARNING,
                width=stroke,
                capstyle=tk.ROUND,
                tags="icon_parts",
            )
            self.canvas.create_line(
                *_relative_point(box, 0.35, 0.54),
                *_relative_point(box, 0.29, 0.66),
                fill=COLOR_AMBER_WARNING,
                width=stroke,
                capstyle=tk.ROUND,
                tags="icon_parts",
            )
            self.canvas.create_line(
                *_relative_point(box, 0.50, 0.56),
                *_relative_point(box, 0.50, 0.70),
                fill=COLOR_AMBER_WARNING,
                width=stroke,
                capstyle=tk.ROUND,
                tags="icon_parts",
            )
            self.canvas.create_line(
                *_relative_point(box, 0.65, 0.54),
                *_relative_point(box, 0.71, 0.66),
                fill=COLOR_AMBER_WARNING,
                width=stroke,
                capstyle=tk.ROUND,
                tags="icon_parts",
            )
            self.canvas.create_line(
                *_relative_point(box, 0.75, 0.48),
                *_relative_point(box, 0.83, 0.56),
                fill=COLOR_AMBER_WARNING,
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
        accent = COLOR_MINT_ACCENT if paused else COLOR_AMBER_WARNING
        fill_color = "#1e2e24" if self._pause_hovered else COLOR_CARD_BG
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
        fill_color = "#2e1e1e" if self._close_hovered else COLOR_CARD_BG
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
            fill=COLOR_RED_CLOSE,
            width=stroke,
            capstyle=tk.ROUND,
            tags="close_control",
        )
        self.canvas.create_line(
            *_relative_point(box, 0.65, 0.35),
            *_relative_point(box, 0.35, 0.65),
            fill=COLOR_RED_CLOSE,
            width=stroke,
            capstyle=tk.ROUND,
            tags="close_control",
        )

    def update_pause_ui(self):
        self._update_dynamic_layout()
        if getattr(self.controller, "paused", False):
            self._draw_eye("closed")
            if self._expanded:
                self.canvas.itemconfig(self.txt_label, text=t("paused"), fill=COLOR_AMBER_WARNING)
            self._draw_pause_control()
            self._draw_close_control()
            self._raise_control_hitboxes()
            return
        self._draw_eye("open")
        if self._expanded:
            self.canvas.itemconfig(self.txt_label, text=t("protecting"), fill=COLOR_MINT_ACCENT)
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

        # Boundary check to prevent moving window off screen
        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        w = self.window.winfo_width()
        h = self.window.winfo_height()
        x = max(0, min(x, sw - w))
        y = max(0, min(y, sh - h))

        self.window.geometry(f"+{x}+{y}")

    def on_click(self, event):
        self._pressed_control = None
        if self._dragged:
            self._dragged = False
            # Check and update DPI if it changed after drag release
            self._check_and_update_dpi()
            return
        # Check if the click is on the eye icon
        ix1, iy1, ix2, iy2 = self.metrics.icon_box
        if ix1 <= event.x <= ix2 and iy1 <= event.y <= iy2:
            if not self.controller.paused:
                self.controller.start_full_break()
                return
        if not self._expanded:
            return
        self._dragged = False

    def on_hover(self, _event):
        self._cancel_collapse()
        if self._dragged or self._pressed_control is not None:
            return
        self.window.attributes("-alpha", 0.95)
        self.update_pause_ui()
        new_points = get_round_rect_points(*self.hover_coords, self.metrics.radius)
        self.canvas.coords(self.bg_id, *new_points)
        self.canvas.itemconfig(self.bg_id, fill=self.bg_color_hover, outline=COLOR_FLOATING_BORDER_HOVER)
        if not self._expanded:
            # Resize window to expanded width and slide left
            right_x = self.window.winfo_x() + self.window.winfo_width()
            w_expanded = self.metrics.window_width
            h = self.metrics.height
            new_x = right_x - w_expanded
            y = self.window.winfo_y()
            self.window.geometry(f"{w_expanded}x{h}+{new_x}+{y}")
            self.canvas.configure(width=w_expanded)
            self._expanded = True
            self.update_pause_ui()
        self.canvas.itemconfig(self.btn_pause, state="normal")
        self.canvas.itemconfig(self.btn_close, state="normal")
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
        if self._expanded:
            # Revert window layout to collapsed state on hide
            old_points = get_round_rect_points(*self.normal_coords, self.metrics.radius)
            self.canvas.coords(self.bg_id, *old_points)
            self.canvas.itemconfig(self.bg_id, fill=self.bg_color_normal, outline=COLOR_FLOATING_BORDER_NORMAL)
            w_collapsed = scale_px(44, self.scale)
            h = self.metrics.height
            right_x = self.window.winfo_x() + self.window.winfo_width()
            new_x = right_x - w_collapsed
            y = self.window.winfo_y()
            self.window.geometry(f"{w_collapsed}x{h}+{new_x}+{y}")
            self._expanded = False
            self.canvas.itemconfig(self.btn_pause, state="hidden")
            self.canvas.itemconfig(self.btn_close, state="hidden")
            self.canvas.delete("pause_control")
            self.canvas.delete("close_control")
        if self.window.state() != "withdrawn":
            self.window.withdraw()

    def show(self):
        if self.window.state() == "withdrawn":
            self.window.deiconify()

    def _check_and_update_dpi(self):
        new_scale = get_window_dpi_scale(self.window)
        if new_scale != self.scale:
            self.scale = new_scale
            self.metrics = build_floating_widget_metrics(self.scale)
            self.normal_coords = self.metrics.collapsed_rect
            self.hover_coords = self.metrics.expanded_rect

            # Reconfigure canvas dimension
            self.canvas.configure(
                width=self.metrics.window_width,
                height=self.metrics.height
            )

            # Re-coords background polygon
            points = get_round_rect_points(
                *(self.hover_coords if self._expanded else self.normal_coords),
                self.metrics.radius
            )
            self.canvas.coords(self.bg_id, *points)
            self.canvas.itemconfig(self.bg_id, width=self.metrics.outline_width)

            # Re-coords label and reset scaled font size
            self.canvas.coords(self.txt_label, self.metrics.label_x, self.metrics.center_y)
            self.canvas.itemconfig(
                self.txt_label,
                font=("Microsoft JhengHei UI", 10, "bold")
            )

            # Re-coords buttons hitbox
            self.canvas.coords(self.btn_pause, *self.metrics.pause_box)
            self.canvas.coords(self.btn_close, *self.metrics.close_box)

            # Repaint controls
            self.update_pause_ui()

            # Adjust window geometry
            w = self.metrics.window_width if self._expanded else scale_px(44, self.scale)
            h = self.metrics.height
            x = self.window.winfo_x()
            y = self.window.winfo_y()
            self.window.geometry(f"{w}x{h}+{x}+{y}")
