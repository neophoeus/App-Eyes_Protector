from dataclasses import dataclass


def scale_px(value, scale):
    if value <= 0:
        return 0
    return max(1, int(round(value * scale)))


def center_window_position(screen_width, screen_height, window_width, window_height):
    return ((screen_width - window_width) // 2, (screen_height - window_height) // 2)


def make_box(center_x, center_y, size):
    half = size // 2
    return (
        center_x - half,
        center_y - half,
        center_x + half,
        center_y + half,
    )


def get_round_rect_points(x1, y1, x2, y2, radius):
    radius = min(radius, (x2 - x1) // 2, (y2 - y1) // 2)
    return [
        x1 + radius,
        y1,
        x1 + radius,
        y1,
        x2 - radius,
        y1,
        x2 - radius,
        y1,
        x2,
        y1,
        x2,
        y1 + radius,
        x2,
        y1 + radius,
        x2,
        y2 - radius,
        x2,
        y2 - radius,
        x2,
        y2,
        x2 - radius,
        y2,
        x2 - radius,
        y2,
        x1 + radius,
        y2,
        x1 + radius,
        y2,
        x1,
        y2,
        x1,
        y2 - radius,
        x1,
        y2 - radius,
        x1,
        y1 + radius,
        x1,
        y1 + radius,
        x1,
        y1,
    ]


@dataclass(frozen=True)
class ReminderDialogMetrics:
    width: int
    height: int
    border_width: int
    title_top_pad: int
    title_bottom_pad: int
    message_pad_x: int
    message_bottom_pad: int
    button_pad_x: int
    button_bottom_pad: int
    primary_button_pad_y: int
    primary_button_spacing: int
    secondary_button_pad_y: int


@dataclass(frozen=True)
class FloatingWidgetMetrics:
    window_width: int
    height: int
    radius: int
    outline_width: int
    collapsed_rect: tuple
    expanded_rect: tuple
    icon_box: tuple
    label_x: int
    center_y: int
    pause_box: tuple
    close_box: tuple
    margin_right: int
    margin_bottom: int
    control_outline_width: int
    control_stroke_width: int
    eye_stroke_width: int


@dataclass(frozen=True)
class FullScreenLayout:
    timer_x: int
    timer_y: int
    timer_font_size: int
    guide_x: int
    guide_y: int
    guide_width: int
    close_center_x: int
    close_center_y: int
    close_radius: int
    card_x1: int
    card_y1: int
    card_x2: int
    card_y2: int
    card_radius: int
    ring_x1: int
    ring_y1: int
    ring_x2: int
    ring_y2: int
    ring_thickness: int


def build_reminder_dialog_metrics(scale):
    return ReminderDialogMetrics(
        width=scale_px(420, scale),
        height=scale_px(320, scale),
        border_width=max(1, scale_px(1, scale)),
        title_top_pad=scale_px(35, scale),
        title_bottom_pad=scale_px(10, scale),
        message_pad_x=scale_px(30, scale),
        message_bottom_pad=scale_px(30, scale),
        button_pad_x=scale_px(40, scale),
        button_bottom_pad=scale_px(35, scale),
        primary_button_pad_y=scale_px(10, scale),
        primary_button_spacing=scale_px(15, scale),
        secondary_button_pad_y=scale_px(5, scale),
    )


def build_floating_widget_metrics(scale):
    center_y = scale_px(22, scale)
    pause_center_x = scale_px(130, scale)
    close_center_x = scale_px(170, scale)
    control_size = scale_px(32, scale)
    return FloatingWidgetMetrics(
        window_width=scale_px(195, scale),
        height=scale_px(44, scale),
        radius=scale_px(16, scale),
        outline_width=max(1, scale_px(1.5, scale)),
        collapsed_rect=(
            scale_px(2, scale),
            scale_px(2, scale),
            scale_px(42, scale),
            scale_px(42, scale),
        ),
        expanded_rect=(
            scale_px(2, scale),
            scale_px(2, scale),
            scale_px(193, scale),
            scale_px(42, scale),
        ),
        icon_box=(
            scale_px(4, scale),
            scale_px(4, scale),
            scale_px(40, scale),
            scale_px(40, scale),
        ),
        label_x=scale_px(52, scale),
        center_y=center_y,
        pause_box=make_box(pause_center_x, center_y, control_size),
        close_box=make_box(close_center_x, center_y, control_size),
        margin_right=scale_px(40, scale),
        margin_bottom=scale_px(80, scale),
        control_outline_width=max(1, scale_px(1, scale)),
        control_stroke_width=max(1, scale_px(1.5, scale)),
        eye_stroke_width=max(1, scale_px(1.5, scale)),
    )


def build_fullscreen_layout(screen_width, screen_height, scale):
    # Direct responsive width: 55% of screen width, clamped between 640px and 1920px
    card_width = int(screen_width * 0.55)
    card_width = max(640, min(1920, card_width))
    
    # 10:7 aspect ratio card height
    card_height = int(card_width * 0.70)
    card_radius = int(card_height * 0.08)
    
    card_x1 = (screen_width - card_width) // 2
    card_y1 = (screen_height - card_height) // 2
    card_x2 = card_x1 + card_width
    card_y2 = card_y1 + card_height
    
    # Proportional ring metrics
    ring_radius = int(card_height * 0.24)
    ring_thickness = max(scale_px(8, scale), int(ring_radius * 0.08))
    
    ring_center_x = screen_width // 2
    ring_center_y = card_y1 + int(card_height * 0.40)
    
    ring_x1 = ring_center_x - ring_radius
    ring_y1 = ring_center_y - ring_radius
    ring_x2 = ring_center_x + ring_radius
    ring_y2 = ring_center_y + ring_radius
    
    timer_x = ring_center_x
    timer_y = ring_center_y
    timer_font_size = int(ring_radius * 0.65)
    
    # Proportional guide text coordinates
    guide_x = screen_width // 2
    guide_y = card_y1 + int(card_height * 0.76)
    guide_width = card_width - scale_px(80, scale)
    
    close_radius = scale_px(26, scale)
    close_margin = scale_px(32, scale)
    close_center_x = screen_width - close_margin - close_radius
    close_center_y = close_margin + close_radius
    
    return FullScreenLayout(
        timer_x=timer_x,
        timer_y=timer_y,
        timer_font_size=timer_font_size,
        guide_x=guide_x,
        guide_y=guide_y,
        guide_width=guide_width,
        close_center_x=close_center_x,
        close_center_y=close_center_y,
        close_radius=close_radius,
        card_x1=card_x1,
        card_y1=card_y1,
        card_x2=card_x2,
        card_y2=card_y2,
        card_radius=card_radius,
        ring_x1=ring_x1,
        ring_y1=ring_y1,
        ring_x2=ring_x2,
        ring_y2=ring_y2,
        ring_thickness=ring_thickness,
    )
