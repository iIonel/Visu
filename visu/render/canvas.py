from __future__ import annotations

import gi

gi.require_version("Gdk", "4.0")
gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, Gtk

from ..interpreter import Snapshot, Structure
from .animator import Animator, Pose
from .primitives import draw_text
from .renderers import RENDERERS
from .renderers.base import NaturalLayout, Region, StructureRenderer
from .theme import DARK_THEME, Theme


LABEL_RESERVE = 28.0
REGION_PADDING = 12.0
MIN_USER_ZOOM = 0.25
MAX_USER_ZOOM = 4.0
ZOOM_STEP = 1.15


class VisuCanvas(Gtk.DrawingArea):

    def __init__(self, theme: Theme = DARK_THEME):
        super().__init__()
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.set_draw_func(self._on_draw)

        self._theme = theme
        self._snapshot: Snapshot | None = None
        self._renderers: dict[str, StructureRenderer] = {
            kind: cls(theme) for kind, cls in RENDERERS.items()
        }
        self._animator = Animator()
        self._tick_id: int | None = None

        self._user_zoom = 1.0
        self._pan_x = 0.0
        self._pan_y = 0.0
        self._drag_start: tuple[float, float] | None = None

        self._current_scale_by_structure: dict[str, float] = {}

        self._install_gestures()
        self.connect("resize", lambda *_: self._on_size_change())

    @property
    def theme(self) -> Theme:
        return self._theme

    def set_theme(self, theme: Theme):
        self._theme = theme
        self._renderers = {kind: cls(theme) for kind, cls in RENDERERS.items()}
        self.queue_draw()

    def set_snapshot(self, snapshot: Snapshot | None):
        self._snapshot = snapshot
        if snapshot is None:
            self._animator.reset()
            self._current_scale_by_structure.clear()
            self.queue_draw()
            return
        self._recompute_targets()
        self._ensure_ticking()

    def reset(self):
        self._snapshot = None
        self._animator.reset()
        self._current_scale_by_structure.clear()
        self.queue_draw()

    def zoom_in(self):
        self._set_user_zoom(self._user_zoom * ZOOM_STEP)

    def zoom_out(self):
        self._set_user_zoom(self._user_zoom / ZOOM_STEP)

    def zoom_reset(self):
        self._user_zoom = 1.0
        self._pan_x = 0.0
        self._pan_y = 0.0
        self._recompute_targets(instant=True)
        self._ensure_ticking()

    def _set_user_zoom(self, value: float):
        self._user_zoom = max(MIN_USER_ZOOM, min(MAX_USER_ZOOM, value))
        self._recompute_targets(instant=True)
        self._ensure_ticking()

    def _recompute_targets(self, instant: bool = False):
        if self._snapshot is None:
            return
        targets, scales = self._compute_targets(self._snapshot)
        self._current_scale_by_structure = scales
        self._animator.commit(targets, instant=instant)

    def _compute_targets(
        self, snapshot: Snapshot
    ) -> tuple[dict[str, Pose], dict[str, float]]:
        targets: dict[str, Pose] = {}
        scales: dict[str, float] = {}

        for structure, region in self._regions_for(snapshot):
            renderer = self._renderers.get(structure.kind)
            if renderer is None:
                continue
            layout = renderer.layout(structure)
            if not layout.poses:
                scales[structure.name] = 1.0 * self._user_zoom
                continue

            fit_scale = self._compute_fit(layout, region)
            final_scale = fit_scale * self._user_zoom
            scales[structure.name] = final_scale

            content_center_x = region.cx + self._pan_x
            content_center_y = (
                region.y
                + LABEL_RESERVE
                + (region.h - LABEL_RESERVE) / 2
                + self._pan_y
            )

            for key, pose in layout.poses.items():
                dx = pose.x * final_scale + content_center_x
                dy = pose.y * final_scale + content_center_y
                targets[key] = Pose(x=dx, y=dy, alpha=pose.alpha, scale=final_scale)

        return targets, scales

    def _compute_fit(self, layout: NaturalLayout, region: Region) -> float:
        w = max(1.0, layout.width)
        h = max(1.0, layout.height)
        avail_w = max(1.0, region.w - 2 * REGION_PADDING)
        avail_h = max(1.0, region.h - LABEL_RESERVE - REGION_PADDING)
        fit = min(1.0, avail_w / w, avail_h / h)
        return max(0.05, fit)

    def _regions_for(self, snapshot: Snapshot) -> list[tuple[Structure, Region]]:
        structures = list(snapshot.structures.values())
        if not structures:
            return []

        pad = self._theme.outer_pad
        gap = self._theme.section_gap
        footer = self._theme.footer_height

        width = float(self.get_width() or 600)
        height = float(self.get_height() or 400)

        weights = [2.5 if s.kind == "graph" else (1.6 if s.kind == "map" else 1.0) for s in structures]
        total_weight = sum(weights) or 1.0
        usable_h = max(120.0, height - 2 * pad - footer - gap * (len(structures) - 1))

        regions: list[tuple[Structure, Region]] = []
        y = pad
        for structure, weight in zip(structures, weights):
            slot_h = max(110.0, usable_h * (weight / total_weight))
            regions.append(
                (
                    structure,
                    Region(x=pad, y=y, w=width - 2 * pad, h=slot_h),
                )
            )
            y += slot_h + gap
        return regions

    def _on_draw(self, _area, cr, width, height):
        t = self._theme
        cr.set_source_rgb(*t.bg)
        cr.paint()

        snapshot = self._snapshot
        if snapshot is None or not snapshot.structures:
            self._draw_placeholder(cr, width, height)
            if snapshot is not None:
                self._draw_footer(cr, width, height, snapshot)
            return

        for structure, region in self._regions_for(snapshot):
            renderer = self._renderers.get(structure.kind)
            if renderer is None:
                continue

            renderer.draw_label(cr, structure, region)
            display_poses = self._poses_for(structure, renderer)

            if not display_poses:
                renderer.draw_empty_placeholder(cr, region)
                continue

            scale = self._current_scale_by_structure.get(structure.name, 1.0)
            renderer.draw(cr, structure, snapshot, display_poses, scale)

        self._draw_footer(cr, width, height, snapshot)
        self._draw_zoom_indicator(cr, width, height)

    def _poses_for(
        self, structure: Structure, renderer: StructureRenderer
    ) -> dict[str, Pose]:
        poses: dict[str, Pose] = {}
        for element in structure.items:
            key = renderer.key(structure, element.id)
            pose = self._animator.pose_at(key)
            if pose is not None:
                poses[key] = pose
        return poses

    def _draw_placeholder(self, cr, width: float, height: float):
        t = self._theme
        msg = "Run pseudocode to visualize structures →"
        cr.select_font_face(t.font_sans)
        cr.set_font_size(14)
        ext = cr.text_extents(msg)
        cr.set_source_rgb(*t.muted)
        cr.move_to((width - ext.width) / 2, height / 2)
        cr.show_text(msg)

    def _draw_footer(self, cr, width: float, height: float, snapshot: Snapshot):
        t = self._theme
        footer_msg = snapshot.message if len(snapshot.message) <= 200 else snapshot.message[:199] + "…"
        draw_text(
            cr,
            f"line {snapshot.line}   {footer_msg}",
            18,
            height - 28,
            t.font_mono,
            t.footer_size,
            t.muted,
        )
        if snapshot.variables:
            vars_str = "  ".join(
                f"{k}={self._fmt(v)}" for k, v in snapshot.variables.items()
            )
            draw_text(cr, vars_str[:200], 18, height - 12, t.font_mono, t.footer_size, t.muted)

    def _draw_zoom_indicator(self, cr, width: float, height: float):
        if abs(self._user_zoom - 1.0) < 0.001 and self._pan_x == 0 and self._pan_y == 0:
            return
        t = self._theme
        text = f"zoom {self._user_zoom * 100:.0f}%"
        draw_text(
            cr, text, width - 88, 22, t.font_mono, t.footer_size, t.muted,
        )

    def _install_gestures(self):
        scroll = Gtk.EventControllerScroll.new(
            Gtk.EventControllerScrollFlags.VERTICAL
        )
        scroll.connect("scroll", self._on_scroll)
        self.add_controller(scroll)

        drag = Gtk.GestureDrag.new()
        drag.set_button(0)
        drag.connect("drag-begin", self._on_drag_begin)
        drag.connect("drag-update", self._on_drag_update)
        drag.connect("drag-end", self._on_drag_end)
        self.add_controller(drag)

        key = Gtk.EventControllerKey.new()
        key.connect("key-pressed", self._on_key_pressed)
        self.add_controller(key)
        self.set_focusable(True)

    def _on_scroll(self, _controller, _dx: float, dy: float) -> bool:
        if dy < 0:
            self.zoom_in()
        elif dy > 0:
            self.zoom_out()
        return True

    def _on_drag_begin(self, _gesture, _x: float, _y: float):
        self._drag_start = (self._pan_x, self._pan_y)

    def _on_drag_update(self, _gesture, offset_x: float, offset_y: float):
        if self._drag_start is None:
            return
        start_x, start_y = self._drag_start
        self._pan_x = start_x + offset_x
        self._pan_y = start_y + offset_y
        self._recompute_targets(instant=True)
        self.queue_draw()

    def _on_drag_end(self, *_):
        self._drag_start = None

    def _on_key_pressed(self, _controller, keyval, _keycode, _state) -> bool:
        if keyval in (Gdk.KEY_plus, Gdk.KEY_equal, Gdk.KEY_KP_Add):
            self.zoom_in()
            return True
        if keyval in (Gdk.KEY_minus, Gdk.KEY_KP_Subtract):
            self.zoom_out()
            return True
        if keyval in (Gdk.KEY_0, Gdk.KEY_KP_0):
            self.zoom_reset()
            return True
        return False

    def _on_size_change(self):
        if self._snapshot is not None:
            self._recompute_targets(instant=True)
            self.queue_draw()

    def _ensure_ticking(self):
        if self._tick_id is not None:
            return
        self._tick_id = self.add_tick_callback(self._on_tick)

    def _on_tick(self, widget, _frame_clock) -> bool:
        self.queue_draw()
        if not self._animator.is_running():
            if self._tick_id is not None:
                try:
                    widget.remove_tick_callback(self._tick_id)
                except Exception:
                    pass
                self._tick_id = None
            return False
        return True

    @staticmethod
    def _fmt(v):
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, float) and v.is_integer():
            return str(int(v))
        if isinstance(v, list):
            return "[" + ", ".join(VisuCanvas._fmt(x) for x in v) + "]"
        if v is None:
            return "null"
        return str(v)
