from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from ...interpreter import Snapshot, Structure
from ..animator import Pose
from ..primitives import draw_text
from ..theme import Theme


@dataclass(frozen=True)
class Region:
    x: float
    y: float
    w: float
    h: float

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def cy(self) -> float:
        return self.y + self.h / 2


@dataclass
class NaturalLayout:
    poses: dict[str, Pose] = field(default_factory=dict)
    width: float = 0.0
    height: float = 0.0


class StructureRenderer(ABC):

    kind: str = ""

    def __init__(self, theme: Theme):
        self.theme = theme

    @abstractmethod
    def layout(self, structure: Structure) -> NaturalLayout:
        ...

    @abstractmethod
    def draw(
        self,
        cr,
        structure: Structure,
        snapshot: Snapshot,
        poses: dict[str, Pose],
        scale: float,
    ):
        ...

    def key(self, structure: Structure, element_id: int) -> str:
        return f"{structure.name}#{element_id}"

    def draw_label(self, cr, structure: Structure, region: Region):
        text = f"{structure.kind}  {structure.name}"
        draw_text(
            cr,
            text,
            region.x,
            region.y + 14,
            self.theme.font_sans,
            self.theme.label_size,
            self.theme.muted,
        )

    def draw_empty_placeholder(self, cr, region: Region):
        draw_text(
            cr,
            "(empty)",
            region.x + 4,
            region.cy,
            self.theme.font_sans,
            self.theme.label_size,
            self.theme.muted,
        )

    @staticmethod
    def _fmt(v):
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, float) and v.is_integer():
            return str(int(v))
        if isinstance(v, list):
            return "[" + ", ".join(StructureRenderer._fmt(x) for x in v) + "]"
        if v is None:
            return "null"
        return str(v)
