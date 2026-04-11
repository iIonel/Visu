from __future__ import annotations

from ...interpreter import Snapshot, Structure
from ..animator import Pose
from ..primitives import draw_text, draw_text_centered, rounded_rect, set_source
from .base import NaturalLayout, StructureRenderer


class MapRenderer(StructureRenderer):
    kind = "map"

    KEY_W = 110.0
    VAL_W = 150.0
    ROW_H = 38.0
    ROW_GAP = 6.0
    CELL_GAP = 6.0

    def layout(self, structure: Structure) -> NaturalLayout:
        entries = structure.map_entries()
        if not entries:
            return NaturalLayout()

        n = len(entries)
        total_w = self.KEY_W + self.CELL_GAP + self.VAL_W
        total_h = n * self.ROW_H + (n - 1) * self.ROW_GAP

        start_y = -total_h / 2 + self.ROW_H / 2
        poses: dict[str, Pose] = {}
        for i, entry in enumerate(entries):
            cy = start_y + i * (self.ROW_H + self.ROW_GAP)
            poses[self.key(structure, entry.id)] = Pose(x=0.0, y=cy)
        return NaturalLayout(poses=poses, width=total_w, height=total_h)

    def draw(self, cr, structure, snapshot: Snapshot, poses, scale: float):
        entries = structure.map_entries()
        if not entries:
            return

        hls = set(snapshot.highlights.get(structure.name, []))
        key_w = self.KEY_W * scale
        val_w = self.VAL_W * scale
        row_h = self.ROW_H * scale
        cell_gap = self.CELL_GAP * scale

        for entry in entries:
            pose = poses.get(self.key(structure, entry.id))
            if pose is None:
                continue
            highlighted = entry.id in hls
            self._draw_cell(
                cr, pose.x - key_w / 2 - cell_gap / 2,
                pose.y, key_w, row_h,
                str(self._fmt(entry.key)), pose, highlighted, scale,
                is_key=True,
            )
            self._draw_cell(
                cr, pose.x + val_w / 2 + cell_gap / 2,
                pose.y, val_w, row_h,
                str(self._fmt(entry.value)), pose, highlighted, scale,
                is_key=False,
            )
            self._draw_arrow(cr, pose.x, pose.y, cell_gap, scale)

    def _draw_cell(self, cr, cx, cy, w, h, text, pose, highlighted, scale, is_key):
        t = self.theme
        x = cx - w / 2
        y = cy - h / 2
        rounded_rect(cr, x, y, w, h, t.corner * scale)

        if highlighted:
            set_source(cr, (*t.highlight[:3], pose.alpha))
            cr.fill_preserve()
            set_source(cr, (*t.highlight[:3], pose.alpha))
            fg = (0.08, 0.06, 0.04)
        else:
            if is_key:
                set_source(cr, (*t.muted[:3], 0.18 * pose.alpha))
            else:
                set_source(cr, (*t.accent_fill[:3], t.accent_fill[3] * pose.alpha))
            cr.fill_preserve()
            set_source(cr, (*t.accent[:3], pose.alpha))
            fg = t.fg

        cr.set_line_width(max(0.8, t.stroke * scale))
        cr.stroke()
        draw_text_centered(
            cr, text, cx, cy,
            t.font_sans, max(9.0, t.value_size * scale),
            (*fg[:3], pose.alpha),
        )

    def _draw_arrow(self, cr, cx, cy, gap, scale):
        t = self.theme
        draw_text(
            cr, "→",
            cx - 5 * scale, cy + 5 * scale,
            t.font_sans, max(10.0, 14.0 * scale),
            (*t.muted[:3], 0.8),
        )

    @staticmethod
    def _fmt(v):
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, float) and v.is_integer():
            return str(int(v))
        if isinstance(v, list):
            return "[" + ", ".join(MapRenderer._fmt(x) for x in v) + "]"
        if v is None:
            return "null"
        return str(v)
