import unittest
from unittest import mock
import tkinter as tk

from eyes_protector.ui import FloatingWidget
from eyes_protector.ui_metrics import build_floating_widget_metrics


class FloatingWidgetTests(unittest.TestCase):
    @mock.patch("eyes_protector.ui.get_window_dpi_scale")
    @mock.patch("tkinter.Toplevel")
    @mock.patch("tkinter.Canvas")
    def test_click_open_eye_starts_break(
        self, mock_canvas_cls, mock_toplevel_cls, mock_get_dpi
    ):
        # Setup mock DPI scale
        mock_get_dpi.return_value = 1.0

        # Setup mock controller (not paused, meaning eye is open)
        controller = mock.MagicMock()
        controller.paused = False

        # Instantiate FloatingWidget
        widget = FloatingWidget(controller)

        # Ensure metrics are built with 1.0 scale for exact coordinate checks
        metrics = build_floating_widget_metrics(1.0)
        widget.metrics = metrics

        # Simulate click release event on the eye icon region (icon_box coordinates are around 4 to 40)
        event = mock.MagicMock()
        event.x = 20
        event.y = 20

        widget._dragged = False
        widget.on_click(event)

        # The controller should immediately start a full break
        controller.start_full_break.assert_called_once()

    @mock.patch("eyes_protector.ui.get_window_dpi_scale")
    @mock.patch("tkinter.Toplevel")
    @mock.patch("tkinter.Canvas")
    def test_click_closed_eye_does_not_start_break(
        self, mock_canvas_cls, mock_toplevel_cls, mock_get_dpi
    ):
        # Setup mock DPI scale
        mock_get_dpi.return_value = 1.0

        # Setup mock controller (paused, meaning eye is closed)
        controller = mock.MagicMock()
        controller.paused = True

        # Instantiate FloatingWidget
        widget = FloatingWidget(controller)

        metrics = build_floating_widget_metrics(1.0)
        widget.metrics = metrics

        # Simulate click release event on the eye icon region
        event = mock.MagicMock()
        event.x = 20
        event.y = 20

        widget._dragged = False
        widget.on_click(event)

        # The controller should NOT start a full break since the eye is closed
        controller.start_full_break.assert_not_called()

    @mock.patch("eyes_protector.ui.get_window_dpi_scale")
    @mock.patch("tkinter.Toplevel")
    @mock.patch("tkinter.Canvas")
    def test_click_outside_eye_does_not_start_break(
        self, mock_canvas_cls, mock_toplevel_cls, mock_get_dpi
    ):
        # Setup mock DPI scale
        mock_get_dpi.return_value = 1.0

        # Setup mock controller (not paused)
        controller = mock.MagicMock()
        controller.paused = False

        # Instantiate FloatingWidget
        widget = FloatingWidget(controller)

        metrics = build_floating_widget_metrics(1.0)
        widget.metrics = metrics

        # Simulate click release event outside the eye icon region
        event = mock.MagicMock()
        event.x = 100
        event.y = 20

        widget._dragged = False
        widget.on_click(event)

        # The controller should NOT start a full break
        controller.start_full_break.assert_not_called()


if __name__ == "__main__":
    unittest.main()
