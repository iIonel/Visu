from __future__ import annotations

import math

from ...interpreter import Snapshot, Structure
from ..animator import Pose
from ..primitives import draw_text_centered, rounded_rect, set_source
from .base import NaturalLayout, StructureRenderer


class SetRenderer(StructureRenderer):
    kind = "set"

    CHIP_W = 60.0
    CHIP_H = 44.0
    GAP_X = 12.0
    GAP_Y = 14.0
    MAX_PER_ROW = 6

    def layout(self, structure: Structure) -> NaturalLayout:
        items = structure.linear_items()
        if not items:
            return NaturalLayout()

        n = len(items)
        per_row = min(self.MAX_PER_ROW, n)
        rows = math.ceil(n / per_row)
        total_w = per_row * self.CHIP_W + (per_row - 1) * self.GAP_X
        total_h = rows * self.CHIP_H + (rows - 1) * self.GAP_Y

        start_x = -total_w / 2 + self.CHIP_W / 2
        start_y = -total_h / 2 + self.CHIP_H / 2

        poses: dict[str, Pose] = {}
        for i, item in enumerate(items):
            row = i // per_row
            col = i % per_row

            nodes_in_row = min(per_row, n - row * per_row)
            row_width = nodes_in_row * self.CHIP_W + (nodes_in_row - 1) * self.GAP_X
            row_start_x = -row_width / 2 + self.CHIP_W / 2

            cx = row_start_x + col * (self.CHIP_W + self.GAP_X)
            cy = start_y + row * (self.CHIP_H + self.GAP_Y)
            poses[self.key(structure, item.id)] = Pose(x=cx, y=cy)

        return NaturalLayout(poses=poses, width=total_w, height=total_h)

    def draw(self, cr, structure, snapshot: Snapshot, poses, scale: float):
        items = structure.linear_items()
        if not items:
            return

        hls = set(snapshot.highlights.get(structure.name, []))
        w = self.CHIP_W * scale
        h = self.CHIP_H * scale

        for item in items:
            pose = poses.get(self.key(structure, item.id))
            if pose is None:
                continue
            self._draw_chip(cr, pose, w, h, str(self._fmt(item.value)), item.id in hls, scale)

    def _draw_chip(self, cr, pose: Pose, w: float, h: float, text: str, highlighted: bool, scale: float):
        t = self.theme
        x = pose.x - w / 2
        y = pose.y - h / 2
        radius = min(w, h) / 2 * 0.85
        rounded_rect(cr, x, y, w, h, radius)
        if highlighted:
            set_source(cr, (*t.highlight[:3], pose.alpha))
            cr.fill_preserve()
            set_source(cr, (*t.highlight[:3], pose.alpha))
        else:
            set_source(cr, (*t.accent_fill[:3], t.accent_fill[3] * pose.alpha))
            cr.fill_preserve()
            set_source(cr, (*t.accent[:3], pose.alpha))
        cr.set_line_width(max(0.8, t.stroke * scale))
        cr.stroke()
        fg = t.fg if not highlighted else (0.08, 0.06, 0.04)
        draw_text_centered(
            cr, text, pose.x, pose.y,
            t.font_sans, max(9.0, t.value_size * scale),
            (*fg[:3], pose.alpha),
        )

    @staticmethod
    def _fmt(v):
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, float) and v.is_integer():
            return str(int(v))
        if isinstance(v, list):
            return "{" + ", ".join(SetRenderer._fmt(x) for x in v) + "}"
        return str(v)
