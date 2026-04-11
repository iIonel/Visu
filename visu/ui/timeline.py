from __future__ import annotations

from typing import Callable

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk


SPEED_LABELS = ["0.25×", "0.5×", "1×", "2×", "4×"]
SPEED_FACTORS = [0.25, 0.5, 1.0, 2.0, 4.0]
DEFAULT_SPEED_INDEX = 2


class Timeline(Gtk.Box):

    BASE_INTERVAL_MS = 500

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.add_css_class("visu-timeline")
        self.set_margin_start(18)
        self.set_margin_end(18)
        self.set_margin_top(6)
        self.set_margin_bottom(14)

        self._on_index_changed: Callable[[int], None] | None = None
        self._count = 0
        self._index = 0
        self._play_source: int | None = None
        self._suppress_scale = False
        self._speed_index = DEFAULT_SPEED_INDEX

        self._build_controls()
        self.set_snapshots(0)

    def _build_controls(self):
        self.prev_btn = Gtk.Button.new_from_icon_name("media-skip-backward-symbolic")
        self.prev_btn.set_tooltip_text("Previous step")
        self.prev_btn.connect("clicked", lambda *_: self.step(-1))
        self.append(self.prev_btn)

        self.play_btn = Gtk.Button.new_from_icon_name("media-playback-start-symbolic")
        self.play_btn.set_tooltip_text("Play / pause")
        self.play_btn.connect("clicked", lambda *_: self.toggle_play())
        self.append(self.play_btn)

        self.next_btn = Gtk.Button.new_from_icon_name("media-skip-forward-symbolic")
        self.next_btn.set_tooltip_text("Next step")
        self.next_btn.connect("clicked", lambda *_: self.step(1))
        self.append(self.next_btn)

        self.scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 1, 1)
        self.scale.set_draw_value(False)
        self.scale.set_hexpand(True)
        self.scale.connect("value-changed", self._on_scale_changed)
        self.append(self.scale)

        self.step_label = Gtk.Label(label="0 / 0")
        self.step_label.add_css_class("dim-label")
        self.step_label.set_width_chars(8)
        self.append(self.step_label)

        self.speed_dropdown = Gtk.DropDown.new_from_strings(SPEED_LABELS)
        self.speed_dropdown.set_selected(self._speed_index)
        self.speed_dropdown.set_tooltip_text("Playback speed")
        self.speed_dropdown.connect("notify::selected", self._on_speed_changed)
        self.append(self.speed_dropdown)

    def connect_change(self, callback: Callable[[int], None]):
        self._on_index_changed = callback

    def set_snapshots(self, count: int):
        self._count = count
        enabled = count > 0
        self.prev_btn.set_sensitive(enabled)
        self.next_btn.set_sensitive(enabled)
        self.play_btn.set_sensitive(enabled)
        self.scale.set_sensitive(enabled)

        upper = max(1, count - 1)
        adj = self.scale.get_adjustment()
        adj.set_lower(0)
        adj.set_upper(upper)
        self.pause()
        self._index = 0
        self._suppress_scale = True
        self.scale.set_value(0)
        self._suppress_scale = False
        self._update_label()

    def set_index(self, index: int):
        if self._count == 0:
            return
        index = max(0, min(self._count - 1, index))
        self._index = index
        self._suppress_scale = True
        self.scale.set_value(index)
        self._suppress_scale = False
        self._update_label()
        if self._on_index_changed:
            self._on_index_changed(index)

    def step(self, delta: int):
        self.set_index(self._index + delta)

    def _on_scale_changed(self, scale):
        if self._suppress_scale or self._count == 0:
            return
        new_index = int(scale.get_value())
        if new_index == self._index:
            return
        self._index = new_index
        self._update_label()
        if self._on_index_changed:
            self._on_index_changed(new_index)

    def _update_label(self):
        shown = 0 if self._count == 0 else self._index + 1
        self.step_label.set_text(f"{shown} / {self._count}")

    def _on_speed_changed(self, dropdown, _param):
        self._speed_index = dropdown.get_selected()
        if self._play_source is not None:
            GLib.source_remove(self._play_source)
            self._play_source = GLib.timeout_add(self._current_interval_ms(), self._on_tick)

    def _current_interval_ms(self) -> int:
        factor = SPEED_FACTORS[self._speed_index]
        return max(30, int(self.BASE_INTERVAL_MS / factor))

    def toggle_play(self):
        if self._play_source is not None:
            self.pause()
            return
        if self._count == 0:
            return
        if self._index >= self._count - 1:
            self.set_index(0)
        self.play_btn.set_icon_name("media-playback-pause-symbolic")
        self._play_source = GLib.timeout_add(self._current_interval_ms(), self._on_tick)

    def pause(self):
        if self._play_source is not None:
            GLib.source_remove(self._play_source)
            self._play_source = None
        self.play_btn.set_icon_name("media-playback-start-symbolic")

    def _on_tick(self) -> bool:
        if self._index >= self._count - 1:
            self.pause()
            return False
        self.set_index(self._index + 1)
        return True
