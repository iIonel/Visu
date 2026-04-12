from __future__ import annotations

import math

from ...interpreter import Snapshot, Structure
from ..animator import Pose
from ..primitives import draw_text_centered, rounded_rect, set_source
from .base import NaturalLayout, StructureRenderer


class GraphRenderer(StructureRenderer):
    kind = "graph"

    NODE_RADIUS = 26.0
    MIN_CIRCLE_R = 110.0
    EXTRA_MARGIN = 32.0
    LABEL_ABOVE = 26.0
    SELF_LOOP_R = 18.0
    PARALLEL_OFFSET = 34.0
    SINGLE_CURVE = 18.0

    def layout(self, structure: Structure) -> NaturalLayout:
        nodes = structure.graph_nodes()
        if not nodes:
            return NaturalLayout()

        n = len(nodes)
        if n == 1:
            circle_r = 0.0
        else:
            min_chord = 2 * self.NODE_RADIUS + 36.0
            ideal = min_chord / (2 * math.sin(math.pi / max(2, n)))
            circle_r = max(self.MIN_CIRCLE_R, ideal)

        total_radius = circle_r + self.NODE_RADIUS + self.EXTRA_MARGIN
        width = 2 * total_radius
        height = 2 * total_radius + self.LABEL_ABOVE

        y_offset = self.LABEL_ABOVE / 2
        poses: dict[str, Pose] = {}
        for i, node in enumerate(nodes):
            if n == 1:
                cx, cy = 0.0, y_offset
            else:
                angle = -math.pi / 2 + 2 * math.pi * i / n
                cx = circle_r * math.cos(angle)
                cy = circle_r * math.sin(angle) + y_offset
            poses[self.key(structure, node.id)] = Pose(x=cx, y=cy)
        return NaturalLayout(poses=poses, width=width, height=height)

    def draw(self, cr, structure, snapshot: Snapshot, poses, scale: float):
        nodes = structure.graph_nodes()
        if not nodes:
            return

        hls = set(snapshot.highlights.get(structure.name, []))
        radius = self.NODE_RADIUS * scale

        key_to_info: dict = {}
        for node in nodes:
            pose = poses.get(self.key(structure, node.id))
            if pose is not None:
                key_to_info[node.key] = (node, pose)

        if not key_to_info:
            return

        center_x = sum(p.x for _, p in key_to_info.values()) / len(key_to_info)
        center_y = sum(p.y for _, p in key_to_info.values()) / len(key_to_info)

        edges_by_pair: dict[tuple, list] = {}
        self_loops: list = []
        for edge in structure.graph_edges():
            if edge.src == edge.dst:
                self_loops.append(edge)
                continue
            pair_key = self._unordered_pair(edge.src, edge.dst)
            edges_by_pair.setdefault(pair_key, []).append(edge)

        for pair_edges in edges_by_pair.values():
            total = len(pair_edges)
            for index, edge in enumerate(pair_edges):
                self._draw_edge(
                    cr, structure, edge, key_to_info, hls, radius, scale,
                    index, total, center_x, center_y,
                )

        for edge in self_loops:
            info = key_to_info.get(edge.src)
            if info is None:
                continue
            self._draw_self_loop(cr, edge, info[1], radius, scale, hls, structure.directed)

        for node in nodes:
            pose = poses.get(self.key(structure, node.id))
            if pose is None:
                continue
            self._draw_node(cr, node, pose, radius, node.id in hls, scale)

    def _unordered_pair(self, a, b) -> tuple:
        ra, rb = repr(a), repr(b)
        return (a, b) if ra < rb else (b, a)

    def _compute_curve(self, edge, total, index, scale,
                       src_pose, dst_pose, nx, ny, center_x, center_y) -> float:
        base_parallel = self.PARALLEL_OFFSET * scale
        base_single = self.SINGLE_CURVE * scale

        if total >= 2:
            if total == 2:
                return base_parallel
            spread = 0.75 * base_parallel * (index - (total - 1) / 2)
            return base_parallel + spread

        mid_x = (src_pose.x + dst_pose.x) / 2
        mid_y = (src_pose.y + dst_pose.y) / 2
        out_x = mid_x - center_x
        out_y = mid_y - center_y
        out_len = math.hypot(out_x, out_y)

        if out_len < 1e-3:
            sign = 1.0 if repr(edge.src) < repr(edge.dst) else -1.0
            return base_single * sign * 1.4

        dot = (out_x * nx + out_y * ny) / out_len
        if abs(dot) < 0.15:
            sign = 1.0 if repr(edge.src) < repr(edge.dst) else -1.0
            return base_single * sign * 1.4

        return base_single if dot > 0 else -base_single

    def _draw_edge(self, cr, structure, edge, key_to_info, hls, radius, scale,
                   index, total, center_x, center_y):
        if edge.src not in key_to_info or edge.dst not in key_to_info:
            return
        src_node, src_pose = key_to_info[edge.src]
        dst_node, dst_pose = key_to_info[edge.dst]

        t = self.theme
        highlighted = edge.id in hls or (
            src_node.id in hls and dst_node.id in hls
        )
        color = t.highlight if highlighted else t.muted
        alpha = 0.95 if highlighted else 0.65
        width = max(1.3, (2.4 if highlighted else 1.7) * scale)

        dx = dst_pose.x - src_pose.x
        dy = dst_pose.y - src_pose.y
        length = math.hypot(dx, dy)
        if length < 1e-6:
            return
        ux, uy = dx / length, dy / length
        nx, ny = -uy, ux

        start_x = src_pose.x + ux * radius
        start_y = src_pose.y + uy * radius
        end_x = dst_pose.x - ux * radius
        end_y = dst_pose.y - uy * radius

        curve = self._compute_curve(
            edge, total, index, scale,
            src_pose, dst_pose, nx, ny, center_x, center_y,
        )

        if abs(curve) < 0.5:
            set_source(cr, (*color[:3], alpha))
            cr.set_line_width(width)
            cr.move_to(start_x, start_y)
            cr.line_to(end_x, end_y)
            cr.stroke()

            if structure.directed:
                angle = math.atan2(end_y - start_y, end_x - start_x)
                self._draw_arrow_head(cr, end_x, end_y, angle, scale, color, alpha)

            label_x = (start_x + end_x) / 2
            label_y = (start_y + end_y) / 2
        else:
            ctrl_x = (start_x + end_x) / 2 + nx * curve
            ctrl_y = (start_y + end_y) / 2 + ny * curve

            c1x = start_x + (ctrl_x - start_x) * 2 / 3
            c1y = start_y + (ctrl_y - start_y) * 2 / 3
            c2x = end_x + (ctrl_x - end_x) * 2 / 3
            c2y = end_y + (ctrl_y - end_y) * 2 / 3

            set_source(cr, (*color[:3], alpha))
            cr.set_line_width(width)
            cr.move_to(start_x, start_y)
            cr.curve_to(c1x, c1y, c2x, c2y, end_x, end_y)
            cr.stroke()

            if structure.directed:
                angle = math.atan2(end_y - ctrl_y, end_x - ctrl_x)
                self._draw_arrow_head(cr, end_x, end_y, angle, scale, color, alpha)

            label_x = 0.25 * start_x + 0.5 * ctrl_x + 0.25 * end_x
            label_y = 0.25 * start_y + 0.5 * ctrl_y + 0.25 * end_y

        if edge.weight is not None:
            self._draw_weight(cr, label_x, label_y, edge.weight, scale, highlighted)

    def _draw_self_loop(self, cr, edge, pose, node_radius, scale, hls, directed):
        t = self.theme
        highlighted = edge.id in hls
        color = t.highlight if highlighted else t.muted
        alpha = 0.95 if highlighted else 0.65
        width = max(1.3, (2.4 if highlighted else 1.7) * scale)
        loop_r = self.SELF_LOOP_R * scale

        attach = math.pi / 5
        a1_x = pose.x - node_radius * math.sin(attach)
        a1_y = pose.y - node_radius * math.cos(attach)
        a2_x = pose.x + node_radius * math.sin(attach)
        a2_y = pose.y - node_radius * math.cos(attach)

        ctrl1_x = pose.x - loop_r * 1.8
        ctrl1_y = pose.y - node_radius - loop_r * 2.6
        ctrl2_x = pose.x + loop_r * 1.8
        ctrl2_y = pose.y - node_radius - loop_r * 2.6

        set_source(cr, (*color[:3], alpha))
        cr.set_line_width(width)
        cr.move_to(a1_x, a1_y)
        cr.curve_to(ctrl1_x, ctrl1_y, ctrl2_x, ctrl2_y, a2_x, a2_y)
        cr.stroke()

        if directed:
            angle = math.atan2(a2_y - ctrl2_y, a2_x - ctrl2_x)
            self._draw_arrow_head(cr, a2_x, a2_y, angle, scale, color, alpha)

        if edge.weight is not None:
            label_y = pose.y - node_radius - loop_r * 1.9
            self._draw_weight(cr, pose.x, label_y, edge.weight, scale, highlighted)

    def _draw_arrow_head(self, cr, x, y, angle, scale, color, alpha):
        head = max(5.5, 9.0 * scale)
        half = math.pi / 7
        ax = x - head * math.cos(angle - half)
        ay = y - head * math.sin(angle - half)
        bx = x - head * math.cos(angle + half)
        by = y - head * math.sin(angle + half)
        set_source(cr, (*color[:3], alpha))
        cr.move_to(x, y)
        cr.line_to(ax, ay)
        cr.line_to(bx, by)
        cr.close_path()
        cr.fill()

    def _draw_weight(self, cr, x, y, weight, scale, highlighted):
        t = self.theme
        label = str(self._fmt(weight))
        font_size = max(9.5, 11.0 * scale)
        cr.select_font_face(t.font_mono)
        cr.set_font_size(font_size)
        ext = cr.text_extents(label)

        pad_x = 6 * scale
        pad_y = 3 * scale
        bg_w = ext.width + 2 * pad_x
        bg_h = ext.height + 2 * pad_y
        bx = x - bg_w / 2
        by = y - bg_h / 2
        corner = min(bg_w, bg_h) / 2

        rounded_rect(cr, bx, by, bg_w, bg_h, corner)
        set_source(cr, (*t.bg[:3], 0.92))
        cr.fill_preserve()
        border = t.highlight if highlighted else t.muted
        set_source(cr, (*border[:3], 0.6))
        cr.set_line_width(max(0.6, 0.9 * scale))
        cr.stroke()

        color = t.highlight if highlighted else t.fg
        draw_text_centered(cr, label, x, y, t.font_mono, font_size, color)

    def _draw_node(self, cr, node, pose, radius, highlighted, scale):
        t = self.theme
        cr.new_sub_path()
        cr.arc(pose.x, pose.y, radius, 0, 2 * math.pi)
        if highlighted:
            set_source(cr, (*t.highlight[:3], pose.alpha))
            cr.fill_preserve()
            set_source(cr, (*t.highlight[:3], pose.alpha))
        else:
            set_source(cr, (*t.bg[:3], pose.alpha))
            cr.fill_preserve()
            set_source(cr, (*t.accent_fill[:3], t.accent_fill[3] * pose.alpha))
            cr.fill_preserve()
            set_source(cr, (*t.accent[:3], pose.alpha))
        cr.set_line_width(max(1.0, t.stroke * scale))
        cr.stroke()

        fg = t.fg if not highlighted else (0.08, 0.06, 0.04)
        key_text = str(self._fmt(node.key))
        draw_text_centered(
            cr, key_text, pose.x, pose.y,
            t.font_sans, max(10.0, (t.value_size + 1) * scale),
            (*fg[:3], pose.alpha),
        )

        if node.value is not None:
            sub = str(self._fmt(node.value))
            if len(sub) > 18:
                sub = sub[:16] + "…"
            draw_text_centered(
                cr, sub,
                pose.x, pose.y + radius + 12 * scale,
                t.font_mono, max(9.0, 10.0 * scale),
                (*t.muted[:3], 0.9 * pose.alpha),
            )
