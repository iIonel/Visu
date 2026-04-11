from __future__ import annotations

import gi

gi.require_version("Gdk", "4.0")
gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, Gtk


class EditorPanel(Gtk.Box):

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.set_hexpand(True)

        self._build_editor()
        self._build_output()

    def _build_editor(self):
        label = self._section_label("pseudocode")
        self.append(label)

        self.buffer = Gtk.TextBuffer()
        self.buffer.set_enable_undo(True)
        self._current_line_tag = self.buffer.create_tag(
            "current_line",
            paragraph_background_rgba=self._make_rgba(0.98, 0.62, 0.32, 0.22),
        )
        self.editor = Gtk.TextView(buffer=self.buffer)
        self.editor.set_monospace(True)
        self.editor.set_top_margin(10)
        self.editor.set_bottom_margin(10)
        self.editor.set_left_margin(14)
        self.editor.set_right_margin(14)
        self.editor.set_wrap_mode(Gtk.WrapMode.NONE)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_child(self.editor)
        scroll.set_vexpand(True)
        scroll.set_margin_start(14)
        scroll.set_margin_end(14)
        scroll.set_margin_top(4)
        scroll.add_css_class("visu-editor-card")
        self.append(scroll)

    def _build_output(self):
        label = self._section_label("output", top=14)
        self.append(label)

        self.output_buffer = Gtk.TextBuffer()
        self.output_view = Gtk.TextView(buffer=self.output_buffer)
        self.output_view.set_editable(False)
        self.output_view.set_monospace(True)
        self.output_view.set_top_margin(8)
        self.output_view.set_bottom_margin(8)
        self.output_view.set_left_margin(14)
        self.output_view.set_right_margin(14)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_child(self.output_view)
        scroll.set_size_request(-1, 150)
        scroll.set_margin_start(14)
        scroll.set_margin_end(14)
        scroll.set_margin_top(4)
        scroll.set_margin_bottom(14)
        scroll.add_css_class("visu-editor-card")
        self.append(scroll)

    def _section_label(self, text: str, top: int = 14) -> Gtk.Label:
        label = Gtk.Label(label=text)
        label.set_xalign(0)
        label.add_css_class("dim-label")
        label.add_css_class("visu-section-label")
        label.set_margin_top(top)
        label.set_margin_start(14)
        return label

    @staticmethod
    def _make_rgba(r: float, g: float, b: float, a: float) -> Gdk.RGBA:
        rgba = Gdk.RGBA()
        rgba.red = r
        rgba.green = g
        rgba.blue = b
        rgba.alpha = a
        return rgba

    def get_source(self) -> str:
        start = self.buffer.get_start_iter()
        end = self.buffer.get_end_iter()
        return self.buffer.get_text(start, end, True)

    def set_source(self, text: str):
        self.buffer.begin_irreversible_action()
        self.buffer.set_text(text)
        self.buffer.end_irreversible_action()

    def set_output(self, text: str):
        self.output_buffer.set_text(text or "")

    def highlight_line(self, line: int | None):
        self.clear_line_highlight()
        if line is None or line < 1:
            return
        line_index = line - 1
        if line_index >= self.buffer.get_line_count():
            return
        result = self.buffer.get_iter_at_line(line_index)
        if isinstance(result, tuple):
            ok, start = result
            if not ok:
                return
        else:
            start = result
        end = start.copy()
        if not end.ends_line():
            end.forward_to_line_end()
        self.buffer.apply_tag(self._current_line_tag, start, end)
        mark = self.buffer.create_mark(None, start, True)
        self.editor.scroll_to_mark(mark, 0.1, False, 0.0, 0.5)
        self.buffer.delete_mark(mark)

    def clear_line_highlight(self):
        start = self.buffer.get_start_iter()
        end = self.buffer.get_end_iter()
        self.buffer.remove_tag(self._current_line_tag, start, end)
