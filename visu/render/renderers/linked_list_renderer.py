
from __future__ import annotations

from ...interpreter import Snapshot, Structure
from ..animator import Pose
from ..primitives import draw_arrow, draw_text, draw_text_centered, rounded_rect, set_source
from .base import NaturalLayout, StructureRenderer


class LinkedListRenderer(StructureRenderer):
    kind = "list"

    BOX_W = 68.0
    BOX_H = 44.0
    GAP = 32.0
    NULL_CAP = 40.0
    LABEL_ABOVE = 22.0

    def layout(self, structure: Structure) -> NaturalLayout:
        items = structure.linear_items()
        if not items:
            return NaturalLayout()

        n = len(items)
        total_w = n * self.BOX_W + (n - 1) * self.GAP + self.NULL_CAP
        total_h = self.BOX_H + self.LABEL_ABOVE

        cy = (self.LABEL_ABOVE - 0) / 2
        start_x = -total_w / 2 + self.BOX_W / 2
        poses: dict[str, Pose] = {}
        for i, item in enumerate(items):
            cx = start_x + i * (self.BOX_W + self.GAP)
            poses[self.key(structure, item.id)] = Pose(x=cx, y=cy)
        return NaturalLayout(poses=poses, width=total_w, height=total_h)

    def draw(self, cr, structure, snapshot: Snapshot, poses, scale: float):
        items = structure.linear_items()
        if not items:
            return

        t = self.theme
        hls = set(snapshot.highlights.get(structure.name, []))
        bw = self.BOX_W * scale
        bh = self.BOX_H * scale

        first_pose = poses.get(self.key(structure, items[0].id))
        if first_pose is not None:
            draw_text(
                cr, "head",
                first_pose.x - bw * 0.28,
                first_pose.y - bh / 2 - 6 * scale,
                t.font_sans, max(9.0, (t.index_size + 1) * scale), t.muted,
            )

        for a, b in zip(items, items[1:]):
            pa = poses.get(self.key(structure, a.id))
            pb = poses.get(self.key(structure, b.id))
            if pa is None or pb is None:
                continue
            draw_arrow(
                cr,
                pa.x + bw / 2 + 2 * scale, pa.y,
                pb.x - bw / 2 - 2 * scale, pb.y,
                t.muted,
                head=max(3.0, 6.0 * scale),
                width=max(0.8, 1.2 * scale),
            )

        for i, item in enumerate(items):
            pose = poses.get(self.key(structure, item.id))
            if pose is None:
                continue
            self._draw_node(cr, pose, bw, bh, str(self._fmt(item.value)), item.id in hls, scale)

        last_pose = poses.get(self.key(structure, items[-1].id))
        if last_pose is not None:
            x1 = last_pose.x + bw / 2 + 2 * scale
            x2 = x1 + 28 * scale
            draw_arrow(
                cr, x1, last_pose.y, x2, last_pose.y, t.muted,
                head=max(3.0, 5.0 * scale), width=max(0.8, 1.0 * scale),
            )
            draw_text_centered(
                cr, "∅", x2 + 8 * scale, last_pose.y,
                t.font_sans, max(10.0, t.value_size * scale), t.muted,
            )

    def _draw_node(self, cr, pose: Pose, w: float, h: float, text: str, highlighted: bool, scale: float):
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

        set_source(cr, (*t.muted[:3], 0.45 * pose.alpha))
        cr.set_line_width(max(0.7, 1.0 * scale))
        cr.move_to(x + w * 0.68, y + 4 * scale)
        cr.line_to(x + w * 0.68, y + h - 4 * scale)
        cr.stroke()

        fg = t.fg if not highlighted else (0.08, 0.06, 0.04)
        draw_text_centered(
            cr, text, pose.x - w * 0.16, pose.y,
            t.font_sans, max(9.0, t.value_size * scale),
            (*fg[:3], pose.alpha),
        )

        cr.new_sub_path()
        cr.arc(pose.x + w * 0.18, pose.y, max(1.5, 2.0 * scale), 0, 6.283185)
        set_source(cr, (*t.muted[:3], pose.alpha))
        cr.fill()

    @staticmethod
    def _fmt(v):
        if isinstance(v, float) and v.is_integer():
            return str(int(v))
        return str(v)
