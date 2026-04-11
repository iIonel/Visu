
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def _copy_value(value: Any) -> Any:
    if isinstance(value, list):
        return [_copy_value(v) for v in value]
    if isinstance(value, tuple):
        return tuple(_copy_value(v) for v in value)
    return value


@dataclass
class Item:
    id: int
    value: Any

    def clone(self) -> "Item":
        return Item(self.id, _copy_value(self.value))


@dataclass
class MapEntry:
    id: int
    key: Any
    value: Any

    def clone(self) -> "MapEntry":
        return MapEntry(self.id, _copy_value(self.key), _copy_value(self.value))


@dataclass
class GraphNode:
    id: int
    key: Any
    value: Any = None

    def clone(self) -> "GraphNode":
        return GraphNode(self.id, _copy_value(self.key), _copy_value(self.value))


@dataclass
class GraphEdge:
    id: int
    src: Any
    dst: Any
    weight: Any = None

    def clone(self) -> "GraphEdge":
        return GraphEdge(
            self.id,
            _copy_value(self.src),
            _copy_value(self.dst),
            _copy_value(self.weight),
        )


@dataclass
class Structure:

    kind: str
    name: str
    items: list = field(default_factory=list)
    edges: list[GraphEdge] = field(default_factory=list)
    directed: bool = False

    def clone(self) -> "Structure":
        return Structure(
            kind=self.kind,
            name=self.name,
            items=[element.clone() for element in self.items],
            edges=[edge.clone() for edge in self.edges],
            directed=self.directed,
        )

    def linear_items(self) -> list[Item]:
        return self.items

    def map_entries(self) -> list[MapEntry]:
        return self.items

    def graph_nodes(self) -> list[GraphNode]:
        return self.items

    def graph_edges(self) -> list[GraphEdge]:
        return self.edges

    def find_node(self, key: Any) -> GraphNode | None:
        for node in self.graph_nodes():
            if node.key == key:
                return node
        return None

    def find_edge(self, src: Any, dst: Any) -> GraphEdge | None:
        for edge in self.edges:
            if edge.src == src and edge.dst == dst:
                return edge
            if not self.directed and edge.src == dst and edge.dst == src:
                return edge
        return None

    def plain_values(self) -> list:
        if self.kind == "map":
            return [e.value for e in self.map_entries()]
        if self.kind == "graph":
            return [n.key for n in self.graph_nodes()]
        return [i.value for i in self.linear_items()]
