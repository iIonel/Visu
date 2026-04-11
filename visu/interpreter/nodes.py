
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Token:
    kind: str
    value: Any
    line: int


@dataclass
class Node:
    kind: str
    line: int
    data: dict = field(default_factory=dict)
