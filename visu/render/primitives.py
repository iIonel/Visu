from __future__ import annotations

import math


def rounded_rect(cr, x: float, y: float, w: float, h: float, r: float):
    r = min(r, w / 2, h / 2)
    cr.new_sub_path()
    cr.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    cr.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    cr.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    cr.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    cr.close_path()


def set_source(cr, color):
    if len(color) == 3:
        cr.set_source_rgb(*color)
    else:
        cr.set_source_rgba(*color)


def text_extents(cr, text: str, font: str, size: float):
    cr.select_font_face(font)
    cr.set_font_size(size)
    return cr.text_extents(text)


def draw_text(cr, text: str, x: float, y: float, font: str, size: float, color):
    set_source(cr, color)
    cr.select_font_face(font)
    cr.set_font_size(size)
    cr.move_to(x, y)
    cr.show_text(text)


def draw_text_centered(cr, text: str, cx: float, cy: float, font: str, size: float, color):
    ext = text_extents(cr, text, font, size)
    set_source(cr, color)
    cr.move_to(cx - ext.width / 2 - ext.x_bearing, cy - ext.height / 2 - ext.y_bearing)
    cr.show_text(text)


def draw_arrow(cr, x1: float, y1: float, x2: float, y2: float, color, head: float = 6.0, width: float = 1.4):
    set_source(cr, color)
    cr.set_line_width(width)
    cr.move_to(x1, y1)
    cr.line_to(x2, y2)
    cr.stroke()

    angle = math.atan2(y2 - y1, x2 - x1)
    ax = x2 - head * math.cos(angle - math.pi / 7)
    ay = y2 - head * math.sin(angle - math.pi / 7)
    bx = x2 - head * math.cos(angle + math.pi / 7)
    by = y2 - head * math.sin(angle + math.pi / 7)
    cr.move_to(x2, y2)
    cr.line_to(ax, ay)
    cr.line_to(bx, by)
    cr.close_path()
    cr.fill()
