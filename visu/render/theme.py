from __future__ import annotations

from dataclasses import dataclass


RGB = tuple[float, float, float]
RGBA = tuple[float, float, float, float]


@dataclass(frozen=True)
class Theme:
    bg: RGB
    panel: RGB
    fg: RGB
    muted: RGB

    accent: RGB
    accent_fill: RGBA

    highlight: RGB
    highlight_fill: RGBA

    font_sans: str = "Sans"
    font_mono: str = "Monospace"
    label_size: int = 11
    value_size: int = 14
    index_size: int = 10
    footer_size: int = 11

    box_w: float = 60.0
    box_h: float = 52.0
    box_gap: float = 10.0
    corner: float = 8.0
    node_radius: float = 22.0
    stroke: float = 1.6

    outer_pad: float = 24.0
    section_gap: float = 16.0
    footer_height: float = 48.0


DARK_THEME = Theme(
    bg=(0.075, 0.078, 0.094),
    panel=(0.105, 0.11, 0.128),
    fg=(0.93, 0.93, 0.96),
    muted=(0.55, 0.56, 0.62),
    accent=(0.42, 0.73, 0.98),
    accent_fill=(0.42, 0.73, 0.98, 0.14),
    highlight=(0.98, 0.62, 0.32),
    highlight_fill=(0.98, 0.62, 0.32, 0.9),
)


LIGHT_THEME = Theme(
    bg=(0.98, 0.98, 0.99),
    panel=(1.0, 1.0, 1.0),
    fg=(0.12, 0.12, 0.14),
    muted=(0.48, 0.5, 0.55),
    accent=(0.16, 0.45, 0.85),
    accent_fill=(0.16, 0.45, 0.85, 0.12),
    highlight=(0.92, 0.45, 0.15),
    highlight_fill=(0.92, 0.45, 0.15, 0.9),
)
