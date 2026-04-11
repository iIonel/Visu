from .array_renderer import ArrayRenderer
from .base import NaturalLayout, Region, StructureRenderer
from .deque_renderer import DequeRenderer
from .graph_renderer import GraphRenderer
from .linked_list_renderer import LinkedListRenderer
from .map_renderer import MapRenderer
from .queue_renderer import QueueRenderer
from .set_renderer import SetRenderer
from .stack_renderer import StackRenderer

RENDERERS: dict[str, type[StructureRenderer]] = {
    "array": ArrayRenderer,
    "stack": StackRenderer,
    "queue": QueueRenderer,
    "deque": DequeRenderer,
    "list": LinkedListRenderer,
    "set": SetRenderer,
    "map": MapRenderer,
    "graph": GraphRenderer,
}

__all__ = [
    "ArrayRenderer",
    "DequeRenderer",
    "GraphRenderer",
    "LinkedListRenderer",
    "MapRenderer",
    "NaturalLayout",
    "QueueRenderer",
    "RENDERERS",
    "Region",
    "SetRenderer",
    "StackRenderer",
    "StructureRenderer",
]
