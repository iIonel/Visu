
from __future__ import annotations

from ...interpreter import Snapshot, Structure
from ..animator import Pose
from ..primitives import draw_text_centered, rounded_rect, set_source
from .base import NaturalLayout, StructureRenderer


class ArrayRenderer(StructureRenderer):
    kind = "array"

    INDEX_GAP = 16.0

    def layout(self, structure: Structure) -> NaturalLayout:
        items = structure.linear_items()
        if not items:
            return NaturalLayout()

        t = self.theme
        n = len(items)
        bw = t.box_w
        bh = t.box_h
        gap = t.box_gap
        total_w = n * bw + (n - 1) * gap
        total_h = bh + self.INDEX_GAP

        start_x = -total_w / 2 + bw / 2
        poses: dict[str, Pose] = {}
        for i, item in enumerate(items):
            cx = start_x + i * (bw + gap)
            poses[self.key(structure, item.id)] = Pose(x=cx, y=-self.INDEX_GAP / 2)
        return NaturalLayout(poses=poses, width=total_w, height=total_h)

    def draw(self, cr, structure, snapshot: Snapshot, poses, scale: float):
        items = structure.linear_items()
        if not items:
            return

        t = self.theme
        hls = set(snapshot.highlights.get(structure.name, []))
        bw = t.box_w * scale
        bh = t.box_h * scale

        for i, item in enumerate(items):
            pose = poses.get(self.key(structure, item.id))
            if pose is None:
                continue
            self._draw_box(cr, pose, bw, bh, str(self._fmt(item.value)), item.id in hls, scale)
            self._draw_index(cr, pose, bh, i, scale)

    def _draw_box(self, cr, pose: Pose, w: float, h: float, text: str, highlighted: bool, scale: float):
        t = self.theme
        x = pose.x - w / 2
        y = pose.y - h / 2

        rounded_rect(cr, x, y, w, h, t.corner * scale)
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

    def _draw_index(self, cr, pose: Pose, box_h: float, index: int, scale: float):
        t = self.theme
        draw_text_centered(
            cr,
            str(index),
            pose.x,
            pose.y + box_h / 2 + 10 * scale,
            t.font_mono,
            max(8.0, t.index_size * scale),
            (*t.muted[:3], 0.8 * pose.alpha),
        )

    @staticmethod
    def _fmt(v):
        if isinstance(v, float) and v.is_integer():
            return str(int(v))
        return str(v)
