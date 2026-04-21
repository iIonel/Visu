from __future__ import annotations

from pathlib import Path

import cairo
import imageio.v2 as imageio
import numpy as np
from PIL import Image

from ..interpreter import Snapshot
from .animator import Pose
from .renderers import RENDERERS
from .renderers.base import Region
from .theme import DARK_THEME, Theme


LABEL_RESERVE = 28.0
REGION_PADDING = 12.0


def export_video(
    snapshots: list[Snapshot],
    path: Path,
    width: int = 1280,
    height: int = 720,
    fps: int = 6,
    theme: Theme = DARK_THEME,
) -> int:
    if not snapshots:
        return 0

    width = width + (width % 2)
    height = height + (height % 2)

    renderers = {kind: cls(theme) for kind, cls in RENDERERS.items()}
    writer = imageio.get_writer(
        str(path),
        fps=fps,
        codec="libx264",
        quality=8,
        macro_block_size=1,
    )
    try:
        for snap in snapshots:
            surface = _render_snapshot(snap, width, height, theme, renderers)
            writer.append_data(_surface_to_rgb_array(surface))
    finally:
        writer.close()
    return len(snapshots)


def _render_snapshot(snapshot, width, height, theme, renderers) -> cairo.ImageSurface:
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    cr = cairo.Context(surface)
    cr.set_source_rgb(*theme.bg)
    cr.paint()

    regions = _regions_for(snapshot, width, height, theme)
    poses_by_struct, scales = _compute_targets(regions, renderers)

    for structure, region in regions:
        renderer = renderers.get(structure.kind)
        if renderer is None:
            continue
        renderer.draw_label(cr, structure, region)
        poses = poses_by_struct.get(structure.name, {})
        if not poses:
            renderer.draw_empty_placeholder(cr, region)
            continue
        renderer.draw(cr, structure, snapshot, poses, scales.get(structure.name, 1.0))

    _draw_footer(cr, width, height, snapshot, theme)
    return surface


def _regions_for(snapshot, width, height, theme):
    structures = list(snapshot.structures.values())
    if not structures:
        return []

    pad = theme.outer_pad
    gap = theme.section_gap
    footer = theme.footer_height

    weights = [
        2.5 if s.kind == "graph" else (1.6 if s.kind == "map" else 1.0)
        for s in structures
    ]
    total_weight = sum(weights) or 1.0
    usable_h = max(120.0, height - 2 * pad - footer - gap * (len(structures) - 1))

    regions = []
    y = pad
    for structure, weight in zip(structures, weights):
        slot_h = max(110.0, usable_h * (weight / total_weight))
        regions.append(
            (structure, Region(x=pad, y=y, w=width - 2 * pad, h=slot_h))
        )
        y += slot_h + gap
    return regions


def _compute_targets(regions, renderers):
    poses_by_struct: dict[str, dict[str, Pose]] = {}
    scales: dict[str, float] = {}

    for structure, region in regions:
        renderer = renderers.get(structure.kind)
        if renderer is None:
            continue
        layout = renderer.layout(structure)
        if not layout.poses:
            scales[structure.name] = 1.0
            continue

        w = max(1.0, layout.width)
        h = max(1.0, layout.height)
        avail_w = max(1.0, region.w - 2 * REGION_PADDING)
        avail_h = max(1.0, region.h - LABEL_RESERVE - REGION_PADDING)
        scale = max(0.05, min(1.0, avail_w / w, avail_h / h))
        scales[structure.name] = scale

        content_cx = region.cx
        content_cy = region.y + LABEL_RESERVE + (region.h - LABEL_RESERVE) / 2

        positioned: dict[str, Pose] = {}
        for key, pose in layout.poses.items():
            positioned[key] = Pose(
                x=pose.x * scale + content_cx,
                y=pose.y * scale + content_cy,
                alpha=pose.alpha,
                scale=scale,
            )
        poses_by_struct[structure.name] = positioned

    return poses_by_struct, scales


def _draw_footer(cr, width, height, snapshot, theme):
    from .primitives import draw_text

    footer_msg = snapshot.message if len(snapshot.message) <= 200 else snapshot.message[:199] + "…"
    draw_text(
        cr,
        f"line {snapshot.line}   {footer_msg}",
        18,
        height - 28,
        theme.font_mono,
        theme.footer_size,
        theme.muted,
    )
    if snapshot.variables:
        vars_str = "  ".join(f"{k}={_fmt(v)}" for k, v in snapshot.variables.items())
        draw_text(cr, vars_str[:200], 18, height - 12, theme.font_mono, theme.footer_size, theme.muted)


def _fmt(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    if isinstance(v, list):
        return "[" + ", ".join(_fmt(x) for x in v) + "]"
    if v is None:
        return "null"
    return str(v)


def _surface_to_rgb_array(surface: cairo.ImageSurface) -> np.ndarray:
    width = surface.get_width()
    height = surface.get_height()
    raw = bytes(surface.get_data())
    img = Image.frombuffer("RGBA", (width, height), raw, "raw", "BGRA", 0, 1)
    return np.asarray(img.convert("RGB"))
