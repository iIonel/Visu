
from __future__ import annotations

from ...interpreter import Snapshot, Structure
from ..animator import Pose
from ..primitives import draw_text, draw_text_centered, rounded_rect, set_source
from .base import NaturalLayout, StructureRenderer


class StackRenderer(StructureRenderer):
    kind = "stack"

    BOX_W = 120.0
    BOX_H = 42.0
    GAP = 6.0
    BASE_EXTRA = 32.0
    BASE_HEIGHT = 6.0
    PAD = 10.0

    def layout(self, structure: Structure) -> NaturalLayout:
        items = structure.linear_items()
        if not items:
            return NaturalLayout(width=self.BOX_W + self.BASE_EXTRA, height=80.0)

        n = len(items)
        total_w = self.BOX_W + self.BASE_EXTRA
        total_h = 2 * self.PAD + self.BASE_HEIGHT + n * self.BOX_H + (n - 1) * self.GAP

        base_top_y = total_h / 2 - self.PAD - self.BASE_HEIGHT
        bottom_box_cy = base_top_y - self.BOX_H / 2

        poses: dict[str, Pose] = {}
        for i, item in enumerate(items):
            cy = bottom_box_cy - i * (self.BOX_H + self.GAP)
            poses[self.key(structure, item.id)] = Pose(x=0.0, y=cy)
        return NaturalLayout(poses=poses, width=total_w, height=total_h)

    def draw(self, cr, structure, snapshot: Snapshot, poses, scale: float):
        items = structure.linear_items()
        if not items:
            return

        hls = set(snapshot.highlights.get(structure.name, []))

        first_pose = poses.get(self.key(structure, items[0].id))
        if first_pose is not None:
            self._draw_base_plate(cr, first_pose, scale)

        box_w = self.BOX_W * scale
        box_h = self.BOX_H * scale

        for i, item in enumerate(items):
            pose = poses.get(self.key(structure, item.id))
            if pose is None:
                continue
            self._draw_box(cr, pose, box_w, box_h, str(self._fmt(item.value)), item.id in hls, scale)
            if i == len(items) - 1:
                self._draw_top_marker(cr, pose, box_w, scale)

    def _draw_base_plate(self, cr, first_pose: Pose, scale: float):
        t = self.theme
        plate_w = (self.BOX_W + self.BASE_EXTRA) * scale
        plate_h = self.BASE_HEIGHT * scale
        x = first_pose.x - plate_w / 2
        y = first_pose.y + (self.BOX_H * scale) / 2
        rounded_rect(cr, x, y, plate_w, plate_h, 3.0 * scale)
        set_source(cr, (*t.muted[:3], 0.55))
        cr.fill()

        cr.set_line_width(max(0.8, scale))
        set_source(cr, (*t.muted[:3], 0.25))
        cr.move_to(x - 8 * scale, y + plate_h + 1.2 * scale)
        cr.line_to(x + plate_w + 8 * scale, y + plate_h + 1.2 * scale)
        cr.stroke()

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

    def _draw_top_marker(self, cr, pose: Pose, box_w: float, scale: float):
        t = self.theme
        draw_text(
            cr, "← top",
            pose.x + box_w / 2 + 10 * scale,
            pose.y + 4 * scale,
            t.font_sans, max(9.0, (t.index_size + 1) * scale),
            t.muted,
        )

    @staticmethod
    def _fmt(v):
        if isinstance(v, float) and v.is_integer():
            return str(int(v))
        return str(v)
