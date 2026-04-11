
from __future__ import annotations

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from ..render import VisuCanvas
from .timeline import Timeline


class CanvasPanel(Gtk.Box):

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.set_hexpand(True)
        self.set_vexpand(True)

        self.canvas = VisuCanvas()
        self.timeline = Timeline()

        self.append(self._build_zoom_bar())
        self.append(self._build_canvas_frame())
        self.append(self.timeline)

    def _build_zoom_bar(self) -> Gtk.Widget:
        bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        bar.set_margin_top(12)
        bar.set_margin_bottom(2)
        bar.set_margin_start(18)
        bar.set_margin_end(18)

        zoom_out = Gtk.Button.new_from_icon_name("zoom-out-symbolic")
        zoom_out.set_tooltip_text("Zoom out  (−)")
        zoom_out.add_css_class("flat")
        zoom_out.connect("clicked", lambda *_: self.canvas.zoom_out())
        bar.append(zoom_out)

        zoom_reset = Gtk.Button.new_from_icon_name("zoom-fit-best-symbolic")
        zoom_reset.set_tooltip_text("Reset zoom & pan  (0)")
        zoom_reset.add_css_class("flat")
        zoom_reset.connect("clicked", lambda *_: self.canvas.zoom_reset())
        bar.append(zoom_reset)

        zoom_in = Gtk.Button.new_from_icon_name("zoom-in-symbolic")
        zoom_in.set_tooltip_text("Zoom in  (+)")
        zoom_in.add_css_class("flat")
        zoom_in.connect("clicked", lambda *_: self.canvas.zoom_in())
        bar.append(zoom_in)

        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        bar.append(spacer)

        hint = Gtk.Label(label="scroll to zoom · drag to pan")
        hint.add_css_class("dim-label")
        hint.add_css_class("visu-section-label")
        bar.append(hint)

        return bar

    def _build_canvas_frame(self) -> Gtk.Widget:
        frame = Gtk.Frame()
        frame.set_child(self.canvas)
        frame.add_css_class("visu-canvas-frame")
        frame.set_margin_start(14)
        frame.set_margin_end(8)
        frame.set_margin_top(4)
        frame.set_margin_bottom(6)
        frame.set_vexpand(True)
        return frame
