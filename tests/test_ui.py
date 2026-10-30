import unittest
from unittest import mock
import tkinter as tk

from eyes_protector.ui import (
    FloatingWidget,
    FullScreenBreak,
    _format_geometry_offset,
    format_remaining_mmss,
)
from eyes_protector.ui_metrics import build_floating_widget_metrics


class UiFormatTests(unittest.TestCase):
    def test_format_remaining_mmss(self):
        self.assertEqual(format_remaining_mmss(1200), "20:00")
        self.assertEqual(format_remaining_mmss(1199), "19:59")
        self.assertEqual(format_remaining_mmss(65), "01:05")
        self.assertEqual(format_remaining_mmss(5), "00:05")
        self.assertEqual(format_remaining_mmss(0), "00:00")
        self.assertEqual(format_remaining_mmss(-10), "00:00")

    def test_format_geometry_offset_negative_multi_monitor_coords(self):
        self.assertEqual(_format_geometry_offset(100, 200), "+100+200")
        self.assertEqual(_format_geometry_offset(-500, -200), "+-500+-200")
        self.assertEqual(_format_geometry_offset(-1920, 0), "+-1920+0")


class FloatingWidgetTests(unittest.TestCase):
    @mock.patch("eyes_protector.ui.get_window_dpi_scale")
    @mock.patch("tkinter.Toplevel")
    @mock.patch("tkinter.Canvas")
    def test_click_open_eye_starts_break(
        self, mock_canvas_cls, mock_toplevel_cls, mock_get_dpi
    ):
        mock_get_dpi.return_value = 1.0
        controller = mock.MagicMock()
        controller.paused = False

        widget = FloatingWidget(controller)
        metrics = build_floating_widget_metrics(1.0)
        widget.metrics = metrics

        event = mock.MagicMock()
        event.x = 20
        event.y = 20

        widget._dragged = False
        widget.on_click(event)

        controller.start_full_break.assert_called_once()

    @mock.patch("eyes_protector.ui.get_window_dpi_scale")
    @mock.patch("tkinter.Toplevel")
    @mock.patch("tkinter.Canvas")
    def test_click_closed_eye_does_not_start_break(
        self, mock_canvas_cls, mock_toplevel_cls, mock_get_dpi
    ):
        mock_get_dpi.return_value = 1.0
        controller = mock.MagicMock()
        controller.paused = True

        widget = FloatingWidget(controller)
        metrics = build_floating_widget_metrics(1.0)
        widget.metrics = metrics

        event = mock.MagicMock()
        event.x = 20
        event.y = 20

        widget._dragged = False
        widget.on_click(event)

        controller.start_full_break.assert_not_called()

    @mock.patch("eyes_protector.ui.get_window_dpi_scale")
    @mock.patch("tkinter.Toplevel")
    @mock.patch("tkinter.Canvas")
    def test_click_outside_eye_does_not_start_break(
        self, mock_canvas_cls, mock_toplevel_cls, mock_get_dpi
    ):
        mock_get_dpi.return_value = 1.0
        controller = mock.MagicMock()
        controller.paused = False

        widget = FloatingWidget(controller)
        metrics = build_floating_widget_metrics(1.0)
        widget.metrics = metrics

        event = mock.MagicMock()
        event.x = 100
        event.y = 20

        widget._dragged = False
        widget.on_click(event)

        controller.start_full_break.assert_not_called()

    @mock.patch("eyes_protector.ui.get_window_dpi_scale")
    @mock.patch("tkinter.Toplevel")
    @mock.patch("tkinter.Canvas")
    def test_update_dynamic_layout_resizes_widget_correctly(
        self, mock_canvas_cls, mock_toplevel_cls, mock_get_dpi
    ):
        mock_get_dpi.return_value = 1.0
        controller = mock.MagicMock()
        controller.paused = False
        controller.remaining_seconds = 1200

        widget = FloatingWidget(controller)
        widget._expanded = True

        widget.update_pause_ui()
        width_normal = widget.metrics.window_width

        with mock.patch("eyes_protector.ui.t", return_value="This is a very very long mock text for testing widget auto expansion"):
            widget.update_pause_ui()
            width_long = widget.metrics.window_width

        self.assertGreater(width_long, width_normal)

    @mock.patch("eyes_protector.ui.get_window_dpi_scale")
    @mock.patch("tkinter.Toplevel")
    @mock.patch("tkinter.Canvas")
    def test_right_click_triggers_snooze_during_warning(
        self, mock_canvas_cls, mock_toplevel_cls, mock_get_dpi
    ):
        mock_get_dpi.return_value = 1.0
        controller = mock.MagicMock()
        controller.state = "WARNING"

        widget = FloatingWidget(controller)
        widget.on_right_click()
        controller.snooze.assert_called_once()

        controller.reset_mock()
        controller.state = "RUNNING"
        widget.on_right_click()
        controller.snooze.assert_not_called()

    @mock.patch("eyes_protector.ui.get_window_dpi_scale")
    @mock.patch("tkinter.Toplevel")
    @mock.patch("tkinter.Canvas")
    def test_status_text_shows_mmss_when_running_and_hides_when_paused(
        self, mock_canvas_cls, mock_toplevel_cls, mock_get_dpi
    ):
        mock_get_dpi.return_value = 1.0
        controller = mock.MagicMock()
        controller.paused = False
        controller.remaining_seconds = 754  # 12:34

        widget = FloatingWidget(controller)
        self.assertTrue(widget._get_status_text().endswith("12:34"))

        controller.paused = True
        self.assertNotIn("12:34", widget._get_status_text())

    @mock.patch("eyes_protector.ui.get_virtual_screen_rect")
    @mock.patch("eyes_protector.ui.get_monitor_work_area")
    @mock.patch("eyes_protector.ui.get_window_dpi_scale")
    @mock.patch("tkinter.Toplevel")
    @mock.patch("tkinter.Canvas")
    def test_left_edge_hover_expands_rightward_and_drag_supports_negative_monitors(
        self,
        mock_canvas_cls,
        mock_toplevel_cls,
        mock_get_dpi,
        mock_work_area,
        mock_virtual_rect,
    ):
        mock_get_dpi.return_value = 1.0
        mock_work_area.return_value = (-1920, 0, 0, 1080)
        mock_virtual_rect.return_value = (-1920, -200, 1920, 1080)

        controller = mock.MagicMock()
        controller.paused = False
        controller.remaining_seconds = 600

        widget = FloatingWidget(controller)
        widget.window.winfo_x.return_value = -1910
        widget.window.winfo_y.return_value = 500
        widget.window.winfo_width.return_value = 44
        widget.window.winfo_height.return_value = 44
        widget.window.winfo_screenwidth.return_value = 1920
        widget.window.winfo_screenheight.return_value = 1080

        widget.on_hover(None)
        self.assertEqual(widget._expand_direction, "right")
        self.assertTrue(widget.is_expanded)
        last_geom = widget.window.geometry.call_args[0][0]
        self.assertTrue(last_geom.endswith("+-1910+500"))

        # Test negative virtual screen drag clamping
        widget._x = 10
        widget._y = 10
        drag_event = mock.MagicMock()
        drag_event.x = -500
        drag_event.y = -1000
        widget.do_move(drag_event)
        widget.window.geometry.assert_called_with("+-1920+-200")


class FullScreenBreakTests(unittest.TestCase):
    @mock.patch("eyes_protector.ui.get_window_dpi_scale")
    @mock.patch("tkinter.Toplevel")
    @mock.patch("tkinter.Canvas")
    def test_delayed_click_through_is_cancelled_on_hide(
        self, mock_canvas_cls, mock_toplevel_cls, mock_get_dpi
    ):
        mock_get_dpi.return_value = 1.0
        controller = mock.MagicMock()
        controller.config.warning_duration = 10

        fs = FullScreenBreak(controller)
        # show as warning
        with mock.patch("eyes_protector.ui.set_window_click_through"):
            fs.show(is_warning=True)
            self.assertTrue(len(fs._warning_delay_jobs) > 0)

            # hide should cancel delayed click-through jobs
            fs.hide()
            self.assertEqual(len(fs._warning_delay_jobs), 0)
            self.assertFalse(fs._is_warning_active)

    @mock.patch("eyes_protector.ui.get_window_dpi_scale")
    @mock.patch("tkinter.Toplevel")
    @mock.patch("tkinter.Canvas")
    def test_finish_early_during_break_triggers_snooze(
        self, mock_canvas_cls, mock_toplevel_cls, mock_get_dpi
    ):
        mock_get_dpi.return_value = 1.0
        controller = mock.MagicMock()
        controller.config.break_duration = 20
        controller.config.sound_enabled = False

        fs = FullScreenBreak(controller)
        fs.window.state = mock.MagicMock(return_value="normal")
        fs._break_completed = False

        with mock.patch("eyes_protector.ui.remove_window_click_through"):
            fs.show(is_warning=False)

        fs.finish_early()
        self.assertTrue(fs._is_finishing)
        # Directly invoke finish_snooze
        fs.finish_snooze()
        controller.snooze.assert_called_once()
        controller.finish_break.assert_not_called()

    @mock.patch("eyes_protector.ui.get_window_dpi_scale")
    @mock.patch("tkinter.Toplevel")
    @mock.patch("tkinter.Canvas")
    def test_finish_early_after_completed_countdown_triggers_finish_break(
        self, mock_canvas_cls, mock_toplevel_cls, mock_get_dpi
    ):
        mock_get_dpi.return_value = 1.0
        controller = mock.MagicMock()
        controller.config.break_duration = 20
        controller.config.sound_enabled = False

        fs = FullScreenBreak(controller)
        fs.window.state = mock.MagicMock(return_value="normal")
        fs._break_completed = True

        fs.finish_early()
        controller.finish_break.assert_called_once()
        controller.snooze.assert_not_called()

    @mock.patch("eyes_protector.ui.set_window_click_through")
    @mock.patch("eyes_protector.ui.get_active_monitor_rect")
    @mock.patch("eyes_protector.ui.get_window_dpi_scale")
    @mock.patch("tkinter.Toplevel")
    @mock.patch("tkinter.Canvas")
    def test_fullscreen_targets_active_monitor_and_guards_stale_session(
        self,
        mock_canvas_cls,
        mock_toplevel_cls,
        mock_get_dpi,
        mock_active_mon,
        mock_set_click_through,
    ):
        mock_get_dpi.return_value = 1.0
        mock_active_mon.return_value = (-1920, 0, 0, 1080)
        controller = mock.MagicMock()
        controller.config.warning_duration = 10

        fs = FullScreenBreak(controller)
        call_order = []
        fs.window.geometry.side_effect = lambda g: call_order.append(("geometry", g))
        fs.window.update_idletasks.side_effect = lambda: call_order.append(("update_idletasks", None))
        fs.window.attributes.side_effect = lambda *args: call_order.append(("attributes", args))
        mock_set_click_through.side_effect = lambda w: call_order.append(("click_through", w))

        sw, sh = fs._refresh_layout()
        self.assertEqual((sw, sh), (1920, 1080))
        self.assertEqual(
            call_order,
            [
                ("attributes", ("-fullscreen", False)),
                ("geometry", "1920x1080+-1920+0"),
                ("update_idletasks", None),
                ("attributes", ("-fullscreen", True)),
            ],
        )

        # Verify -alpha is configured BEFORE set_window_click_through on show(is_warning=True)
        call_order.clear()
        fs.show(is_warning=True)
        alpha_idx = call_order.index(("attributes", ("-alpha", 0.0)))
        ct_idx = call_order.index(("click_through", fs.window))
        self.assertLess(alpha_idx, ct_idx)

        # Stale session_id must not re-apply click-through
        active_session = fs._session_id
        mock_set_click_through.reset_mock()

        fs._reapply_warning_click_through(active_session - 1)
        mock_set_click_through.assert_not_called()

        # Escape / finish_early during active warning snoozes immediately without 1s freeze
        fs.window.state = mock.MagicMock(return_value="normal")
        fs.finish_early()
        controller.snooze.assert_called_once()
        self.assertFalse(fs._is_finishing)

        # After hide(), even previous active_session is invalidated
        fs._reapply_warning_click_through(active_session)
        mock_set_click_through.assert_not_called()


if __name__ == "__main__":
    unittest.main()
