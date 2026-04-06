import unittest

from eyes_protector.ui_metrics import (
    build_floating_widget_metrics,
    build_fullscreen_layout,
    build_reminder_dialog_metrics,
    center_window_position,
    scale_px,
)


class UiMetricsTests(unittest.TestCase):
    def test_scale_px_rounds_and_preserves_zero(self):
        self.assertEqual(scale_px(0, 2.0), 0)
        self.assertEqual(scale_px(2, 1.5), 3)
        self.assertEqual(scale_px(10, 1.0), 10)

    def test_center_window_position_centers_dialog(self):
        self.assertEqual(center_window_position(1920, 1080, 420, 320), (750, 380))

    def test_reminder_dialog_metrics_match_base_geometry(self):
        metrics = build_reminder_dialog_metrics(1.0)
        self.assertEqual(metrics.width, 420)
        self.assertEqual(metrics.height, 320)
        self.assertEqual(metrics.title_top_pad, 35)
        self.assertEqual(metrics.button_pad_x, 40)

    def test_floating_widget_metrics_scale_collapsed_and_expanded_geometry(self):
        metrics = build_floating_widget_metrics(2.0)
        self.assertEqual(metrics.window_width, 390)
        self.assertEqual(metrics.height, 88)
        self.assertEqual(metrics.collapsed_rect, (4, 4, 84, 84))
        self.assertEqual(metrics.expanded_rect, (4, 4, 386, 84))
        self.assertEqual(metrics.pause_box, (228, 12, 292, 76))
        self.assertEqual(metrics.close_box, (308, 12, 372, 76))

    def test_fullscreen_layout_keeps_timer_guide_and_close_control_in_bounds(self):
        layout = build_fullscreen_layout(3840, 2160, 2.0)
        self.assertEqual(layout.timer_x, 1920)
        self.assertGreater(layout.timer_y, 0)
        self.assertEqual(layout.guide_x, layout.timer_x)
        self.assertGreater(layout.guide_y, layout.timer_y)
        self.assertLess(layout.guide_y, 2160)
        self.assertGreater(layout.guide_width, 0)
        self.assertGreaterEqual(layout.close_center_x - layout.close_radius, 0)
        self.assertGreaterEqual(layout.close_center_y - layout.close_radius, 0)
        self.assertLessEqual(layout.close_center_x + layout.close_radius, 3840)
        self.assertLessEqual(layout.close_center_y + layout.close_radius, 2160)


if __name__ == "__main__":
    unittest.main()
