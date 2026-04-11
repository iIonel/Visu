
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .structures import Structure


@dataclass
class Snapshot:
    line: int
    structures: dict[str, Structure] = field(default_factory=dict)
    variables: dict[str, Any] = field(default_factory=dict)
    highlights: dict[str, list[int]] = field(default_factory=dict)
    message: str = ""
    output: str = ""
