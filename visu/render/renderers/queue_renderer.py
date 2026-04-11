
from __future__ import annotations

from ...interpreter import Snapshot, Structure
from ..animator import Pose
from ..primitives import draw_arrow, draw_text, draw_text_centered, rounded_rect, set_source
from .base import NaturalLayout, StructureRenderer


class QueueRenderer(StructureRenderer):
    kind = "queue"

    LABEL_ABOVE = 20.0
    ARROW_BELOW = 20.0

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
        total_h = bh + self.LABEL_ABOVE + self.ARROW_BELOW

        cy = (self.LABEL_ABOVE - self.ARROW_BELOW) / 2
        start_x = -total_w / 2 + bw / 2
        poses: dict[str, Pose] = {}
        for i, item in enumerate(items):
            cx = start_x + i * (bw + gap)
            poses[self.key(structure, item.id)] = Pose(x=cx, y=cy)
        return NaturalLayout(poses=poses, width=total_w, height=total_h)

    def draw(self, cr, structure, snapshot: Snapshot, poses, scale: float):
        items = structure.linear_items()
        if not items:
            return

        t = self.theme
        hls = set(snapshot.highlights.get(structure.name, []))
        bw = t.box_w * scale
        bh = t.box_h * scale

        first_pose = poses.get(self.key(structure, items[0].id))
        last_pose = poses.get(self.key(structure, items[-1].id))

        if first_pose is not None:
            draw_text(
                cr, "front",
                first_pose.x - bw * 0.4,
                first_pose.y - bh / 2 - 6 * scale,
                t.font_sans, max(9.0, (t.index_size + 1) * scale), t.muted,
            )
        if last_pose is not None and last_pose is not first_pose:
            draw_text(
                cr, "rear",
                last_pose.x - bw * 0.35,
                last_pose.y - bh / 2 - 6 * scale,
                t.font_sans, max(9.0, (t.index_size + 1) * scale), t.muted,
            )

        if first_pose is not None and last_pose is not None and last_pose.x - first_pose.x > 40 * scale:
            draw_arrow(
                cr,
                first_pose.x - bw / 2 - 4 * scale,
                first_pose.y + bh / 2 + 12 * scale,
                last_pose.x + bw / 2 + 4 * scale,
                last_pose.y + bh / 2 + 12 * scale,
                (*t.muted[:3], 0.5),
                head=max(3.0, 5.0 * scale),
                width=max(0.8, 1.0 * scale),
            )

        for i, item in enumerate(items):
            pose = poses.get(self.key(structure, item.id))
            if pose is None:
                continue
            self._draw_box(cr, pose, bw, bh, str(self._fmt(item.value)), item.id in hls, scale)

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

    @staticmethod
    def _fmt(v):
        if isinstance(v, float) and v.is_integer():
            return str(int(v))
        return str(v)
