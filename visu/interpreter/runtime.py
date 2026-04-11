from __future__ import annotations

from typing import Any

from .errors import LexError, ParseError, VisuRuntimeError
from .lexer import tokenize
from .nodes import Node
from .parser import parse
from .snapshot import Snapshot
from .structures import GraphEdge, GraphNode, Item, MapEntry, Structure


LINEAR_KINDS = {"array", "stack", "queue", "deque", "list"}


class Interpreter:
    MAX_STEPS = 20000
    MAX_ITEMS_PER_STRUCTURE = 10000
    MAX_MESSAGE_CHARS = 500

    def __init__(self):
        self.vars: dict[str, Any] = {}
        self.structs: dict[str, Structure] = {}
        self.snapshots: list[Snapshot] = []
        self.output_buf: list[str] = []
        self.highlights: dict[str, list[int]] = {}
        self._id_counter = 0
        self._step_count = 0

    def run(self, src: str) -> list[Snapshot]:
        tokens = tokenize(src)
        program = parse(tokens)
        self._exec_block(program)
        return self.snapshots

    def _next_id(self) -> int:
        self._id_counter += 1
        return self._id_counter

    def _snapshot(self, line: int, message: str = ""):
        self._step_count += 1
        if self._step_count > self.MAX_STEPS:
            raise VisuRuntimeError(line, "step limit exceeded (possible infinite loop)")
        if len(message) > self.MAX_MESSAGE_CHARS:
            message = message[: self.MAX_MESSAGE_CHARS - 1] + "…"
        self.snapshots.append(
            Snapshot(
                line=line,
                structures={k: v.clone() for k, v in self.structs.items()},
                variables=dict(self.vars),
                highlights={k: list(v) for k, v in self.highlights.items()},
                message=message,
                output="\n".join(self.output_buf),
            )
        )

    def _check_capacity(self, line: int, struct: Structure, delta: int = 1):
        if len(struct.items) + delta > self.MAX_ITEMS_PER_STRUCTURE:
            raise VisuRuntimeError(
                line,
                f"{struct.kind} {struct.name} exceeds max item count "
                f"({self.MAX_ITEMS_PER_STRUCTURE})",
            )

    def _check_edge_capacity(self, line: int, struct: Structure):
        if len(struct.edges) + 1 > self.MAX_ITEMS_PER_STRUCTURE:
            raise VisuRuntimeError(
                line,
                f"graph {struct.name} exceeds max edge count "
                f"({self.MAX_ITEMS_PER_STRUCTURE})",
            )

    def _exec_block(self, stmts: list[Node]):
        for s in stmts:
            self._exec_stmt(s)

    def _exec_stmt(self, s: Node):
        self.highlights.clear()
        handler = getattr(self, f"_stmt_{s.kind}", None)
        if handler is None:
            raise VisuRuntimeError(s.line, f"unknown statement {s.kind}")
        handler(s)

    def _stmt_decl(self, s: Node):
        t = s.data["type"]
        name = s.data["name"]
        if t == "graph":
            directed = s.data["directed"]
            self.structs[name] = Structure(
                kind="graph", name=name, items=[], edges=[], directed=directed
            )
            direction_label = "directed" if directed else "undirected"
            self._snapshot(s.line, f"graph {name} ({direction_label}) created")
            return

        expr = s.data["expr"]
        raw_values = self._literal_values(expr)

        if len(raw_values) > self.MAX_ITEMS_PER_STRUCTURE:
            raise VisuRuntimeError(
                s.line,
                f"initial literal exceeds max item count ({self.MAX_ITEMS_PER_STRUCTURE})",
            )

        if t == "set":
            items: list[Item] = []
            seen: list = []
            for v in raw_values:
                if v in seen:
                    continue
                seen.append(v)
                items.append(Item(self._next_id(), v))
            self.structs[name] = Structure(kind="set", name=name, items=items)
        elif t == "map":
            if raw_values:
                raise VisuRuntimeError(
                    s.line, "map must start empty — use .set(key, value) to populate it"
                )
            self.structs[name] = Structure(kind="map", name=name, items=[])
        elif t in LINEAR_KINDS:
            items = [Item(self._next_id(), v) for v in raw_values]
            self.structs[name] = Structure(kind=t, name=name, items=items)
        else:
            raise VisuRuntimeError(s.line, f"unknown structure type {t}")

        self._snapshot(s.line, f"{t} {name} created")

    def _stmt_assign(self, s: Node):
        name = s.data["name"]
        value = self._eval(s.data["value"])
        self.vars[name] = value
        self._snapshot(s.line, f"{name} = {self._fmt(value)}")

    def _stmt_index_assign(self, s: Node):
        name = s.data["name"]
        st = self._get_struct(s, name)
        if st.kind not in LINEAR_KINDS:
            raise VisuRuntimeError(s.line, f"cannot assign {st.kind} by index")
        idx = int(self._eval(s.data["index"]))
        if idx < 0 or idx >= len(st.items):
            raise VisuRuntimeError(s.line, f"index {idx} out of range")
        value = self._eval(s.data["value"])
        new_item = Item(self._next_id(), value)
        st.items[idx] = new_item
        self.highlights[name] = [new_item.id]
        self._snapshot(s.line, f"{name}[{idx}] = {self._fmt(value)}")

    def _stmt_method(self, s: Node):
        MethodDispatcher(self).dispatch(s)

    def _stmt_print(self, s: Node):
        values = [self._fmt(self._eval(a)) for a in s.data["args"]]
        self.output_buf.append(" ".join(values))
        self._snapshot(s.line, f"print {' '.join(values)}")

    def _stmt_swap(self, s: Node):
        args = s.data["args"]
        if len(args) != 3:
            raise VisuRuntimeError(s.line, "swap(arr, i, j) takes 3 arguments")
        name = self._name_of(args[0])
        st = self._get_struct(s, name)
        if st.kind not in LINEAR_KINDS:
            raise VisuRuntimeError(s.line, f"cannot swap within a {st.kind}")
        i = int(self._eval(args[1]))
        j = int(self._eval(args[2]))
        if not (0 <= i < len(st.items) and 0 <= j < len(st.items)):
            raise VisuRuntimeError(s.line, "swap index out of range")
        st.items[i], st.items[j] = st.items[j], st.items[i]
        self.highlights[name] = [st.items[i].id, st.items[j].id]
        self._snapshot(s.line, f"swap {name}[{i}] ↔ {name}[{j}]")

    def _stmt_highlight(self, s: Node):
        args = s.data["args"]
        if not args:
            return
        name = self._name_of(args[0])
        st = self._get_struct(s, name)
        values = [self._eval(a) for a in args[1:]]
        ids: list[int] = []
        if st.kind == "graph":
            for value in values:
                node = st.find_node(value)
                if node is not None:
                    ids.append(node.id)
        elif st.kind == "map":
            for value in values:
                for entry in st.map_entries():
                    if entry.key == value:
                        ids.append(entry.id)
                        break
        elif st.kind == "set":
            for value in values:
                for item in st.linear_items():
                    if item.value == value:
                        ids.append(item.id)
                        break
        else:
            for value in values:
                idx = int(value)
                if 0 <= idx < len(st.items):
                    ids.append(st.items[idx].id)
        self.highlights[name] = ids
        self._snapshot(s.line, f"highlight {name} {self._fmt(values)}")

    def _stmt_if(self, s: Node):
        cond = self._eval(s.data["cond"])
        self._snapshot(s.line, f"if → {bool(cond)}")
        self._exec_block(s.data["then"] if cond else s.data["else"])

    def _stmt_while(self, s: Node):
        while self._eval(s.data["cond"]):
            self._snapshot(s.line, "while true")
            self._exec_block(s.data["body"])
        self._snapshot(s.line, "while done")

    def _stmt_for(self, s: Node):
        start = int(self._eval(s.data["start"]))
        stop = int(self._eval(s.data["stop"]))
        var = s.data["var"]
        step = 1 if stop >= start else -1
        for i in range(start, stop, step):
            self.vars[var] = i
            self._snapshot(s.line, f"{var} = {i}")
            self._exec_block(s.data["body"])
        self._snapshot(s.line, "for done")

    def _eval(self, n: Node):
        k = n.kind
        handler = getattr(self, f"_eval_{k}", None)
        if handler is not None:
            return handler(n)
        if k == "num" or k == "str" or k == "bool":
            return n.data["value"]
        if k == "null":
            return None
        raise VisuRuntimeError(n.line, f"cannot evaluate {k}")

    def _eval_num(self, n): return n.data["value"]
    def _eval_str(self, n): return n.data["value"]
    def _eval_bool(self, n): return n.data["value"]
    def _eval_null(self, n): return None

    def _eval_array_lit(self, n: Node):
        return [self._eval(x) for x in n.data["items"]]

    def _eval_var(self, n: Node):
        name = n.data["name"]
        if name in self.vars:
            return self.vars[name]
        if name in self.structs:
            return self.structs[name].plain_values()
        raise VisuRuntimeError(n.line, f"undefined variable {name}")

    def _eval_index(self, n: Node):
        name = n.data["name"]
        idx = int(self._eval(n.data["index"]))
        if name in self.structs:
            st = self.structs[name]
            if st.kind not in LINEAR_KINDS:
                raise VisuRuntimeError(n.line, f"cannot index {st.kind}")
            if idx < 0 or idx >= len(st.items):
                raise VisuRuntimeError(n.line, f"index {idx} out of range")
            return st.items[idx].value
        if name in self.vars and isinstance(self.vars[name], list):
            return self.vars[name][idx]
        raise VisuRuntimeError(n.line, f"cannot index {name}")

    def _eval_attr(self, n: Node):
        name = n.data["name"]
        attr = n.data["attr"]
        if name in self.structs:
            st = self.structs[name]
            if attr in ("length", "size"):
                return len(st.items)
            if st.kind == "graph":
                if attr == "node_count":
                    return len(st.items)
                if attr == "edge_count":
                    return len(st.edges)
        if name in self.vars and isinstance(self.vars[name], list) and attr in ("length", "size"):
            return len(self.vars[name])
        raise VisuRuntimeError(n.line, f"cannot read {name}.{attr}")

    def _eval_method_expr(self, n: Node):
        name = n.data["name"]
        method = n.data["method"]
        if name not in self.structs:
            raise VisuRuntimeError(n.line, f"unknown structure {name}")
        st = self.structs[name]
        args = [self._eval(a) for a in n.data["args"]]

        query = QUERY_METHODS.get((st.kind, method))
        if query is None:
            raise VisuRuntimeError(n.line, f"{st.kind} has no query {method}")
        return query(st, args, n)

    def _eval_binop(self, n: Node):
        op = n.data["op"]
        left = self._eval(n.data["left"])
        right = self._eval(n.data["right"])
        if op == "+": return left + right
        if op == "-": return left - right
        if op == "*": return left * right
        if op == "/":
            if right == 0:
                raise VisuRuntimeError(n.line, "division by zero")
            return left / right
        if op == "%": return left % right
        if op == "==": return left == right
        if op == "!=": return left != right
        if op == "<": return left < right
        if op == ">": return left > right
        if op == "<=": return left <= right
        if op == ">=": return left >= right
        if op == "and": return bool(left) and bool(right)
        if op == "or": return bool(left) or bool(right)
        raise VisuRuntimeError(n.line, f"unknown operator {op}")

    def _eval_unop(self, n: Node):
        value = self._eval(n.data["operand"])
        op = n.data["op"]
        if op == "-": return -value
        if op == "not": return not value
        raise VisuRuntimeError(n.line, f"unknown unary {op}")

    def _literal_values(self, expr: Node | None) -> list:
        if expr is None:
            return []
        if expr.kind == "array_lit":
            return [self._eval(x) for x in expr.data["items"]]
        value = self._eval(expr)
        return list(value) if isinstance(value, list) else []

    def _get_struct(self, s: Node, name: str) -> Structure:
        if name not in self.structs:
            raise VisuRuntimeError(s.line, f"unknown structure {name}")
        return self.structs[name]

    def _name_of(self, node: Node) -> str:
        if node.kind == "var":
            return node.data["name"]
        raise VisuRuntimeError(node.line, "expected structure name")

    @staticmethod
    def _fmt(v) -> str:
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, float) and v.is_integer():
            return str(int(v))
        if isinstance(v, list):
            return "[" + ", ".join(Interpreter._fmt(x) for x in v) + "]"
        if v is None:
            return "null"
        return str(v)


class MethodDispatcher:
    def __init__(self, interp: Interpreter):
        self.interp = interp

    def dispatch(self, node: Node):
        name = node.data["name"]
        method = node.data["method"]
        args = [self.interp._eval(a) for a in node.data["args"]]
        struct = self.interp._get_struct(node, name)
        handler = getattr(self, f"_{struct.kind}_{method}", None)
        if handler is None:
            raise VisuRuntimeError(
                node.line, f"{struct.kind} has no method {method}"
            )
        handler(node, struct, args)

    def _need(self, node: Node, method: str, args: list, count: int):
        if len(args) != count:
            raise VisuRuntimeError(
                node.line, f"{method} expects {count} argument(s)"
            )

    def _need_between(self, node: Node, method: str, args: list, lo: int, hi: int):
        if not (lo <= len(args) <= hi):
            raise VisuRuntimeError(
                node.line, f"{method} expects {lo}..{hi} arguments"
            )

    def _push_item(self, node: Node, struct: Structure, value) -> Item:
        self.interp._check_capacity(node.line, struct)
        item = Item(self.interp._next_id(), value)
        struct.items.append(item)
        self.interp.highlights[struct.name] = [item.id]
        return item

    def _pop_index(self, node: Node, struct: Structure, index: int):
        if not struct.items:
            raise VisuRuntimeError(node.line, f"pop from empty {struct.kind}")
        if not (0 <= index < len(struct.items)):
            raise VisuRuntimeError(node.line, "pop index out of range")
        return struct.items.pop(index).value

    def _array_push(self, node, struct, args):
        self._need(node, "push", args, 1)
        self._push_item(node, struct, args[0])
        self.interp._snapshot(node.line, f"{struct.name}.push({self.interp._fmt(args[0])})")

    def _array_pop(self, node, struct, args):
        self._need(node, "pop", args, 0)
        value = self._pop_index(node, struct, len(struct.items) - 1)
        self.interp._snapshot(node.line, f"{struct.name}.pop() → {self.interp._fmt(value)}")

    def _array_insert(self, node, struct, args):
        self._need(node, "insert", args, 2)
        self.interp._check_capacity(node.line, struct)
        index = int(args[0])
        item = Item(self.interp._next_id(), args[1])
        struct.items.insert(index, item)
        self.interp.highlights[struct.name] = [item.id]
        self.interp._snapshot(
            node.line,
            f"{struct.name}.insert({index}, {self.interp._fmt(args[1])})",
        )

    def _array_remove(self, node, struct, args):
        self._need(node, "remove", args, 1)
        index = int(args[0])
        value = self._pop_index(node, struct, index)
        self.interp._snapshot(
            node.line, f"{struct.name}.remove({index}) → {self.interp._fmt(value)}"
        )

    def _stack_push(self, node, struct, args):
        self._array_push(node, struct, args)

    def _stack_pop(self, node, struct, args):
        self._array_pop(node, struct, args)

    def _queue_enqueue(self, node, struct, args):
        self._need(node, "enqueue", args, 1)
        self._push_item(node, struct, args[0])
        self.interp._snapshot(
            node.line, f"{struct.name}.enqueue({self.interp._fmt(args[0])})"
        )

    def _queue_dequeue(self, node, struct, args):
        self._need(node, "dequeue", args, 0)
        value = self._pop_index(node, struct, 0)
        self.interp._snapshot(
            node.line, f"{struct.name}.dequeue() → {self.interp._fmt(value)}"
        )

    def _deque_push_front(self, node, struct, args):
        self._need(node, "push_front", args, 1)
        self.interp._check_capacity(node.line, struct)
        item = Item(self.interp._next_id(), args[0])
        struct.items.insert(0, item)
        self.interp.highlights[struct.name] = [item.id]
        self.interp._snapshot(
            node.line, f"{struct.name}.push_front({self.interp._fmt(args[0])})"
        )

    def _deque_push_back(self, node, struct, args):
        self._need(node, "push_back", args, 1)
        self._push_item(node, struct, args[0])
        self.interp._snapshot(
            node.line, f"{struct.name}.push_back({self.interp._fmt(args[0])})"
        )

    def _deque_pop_front(self, node, struct, args):
        self._need(node, "pop_front", args, 0)
        value = self._pop_index(node, struct, 0)
        self.interp._snapshot(
            node.line, f"{struct.name}.pop_front() → {self.interp._fmt(value)}"
        )

    def _deque_pop_back(self, node, struct, args):
        self._need(node, "pop_back", args, 0)
        value = self._pop_index(node, struct, len(struct.items) - 1)
        self.interp._snapshot(
            node.line, f"{struct.name}.pop_back() → {self.interp._fmt(value)}"
        )

    def _list_append(self, node, struct, args):
        self._need(node, "append", args, 1)
        self._push_item(node, struct, args[0])
        self.interp._snapshot(
            node.line, f"{struct.name}.append({self.interp._fmt(args[0])})"
        )

    def _list_prepend(self, node, struct, args):
        self._deque_push_front(node, struct, args)

    def _list_remove(self, node, struct, args):
        self._array_remove(node, struct, args)

    def _set_add(self, node, struct, args):
        self._need(node, "add", args, 1)
        for existing in struct.items:
            if existing.value == args[0]:
                self.interp.highlights[struct.name] = [existing.id]
                self.interp._snapshot(
                    node.line,
                    f"{struct.name}.add({self.interp._fmt(args[0])}) (already present)",
                )
                return
        self._push_item(node, struct, args[0])
        self.interp._snapshot(
            node.line, f"{struct.name}.add({self.interp._fmt(args[0])})"
        )

    def _set_remove(self, node, struct, args):
        self._need(node, "remove", args, 1)
        for idx, existing in enumerate(struct.items):
            if existing.value == args[0]:
                struct.items.pop(idx)
                self.interp._snapshot(
                    node.line, f"{struct.name}.remove({self.interp._fmt(args[0])})"
                )
                return
        raise VisuRuntimeError(node.line, f"{args[0]!r} not in set")

    def _map_set(self, node, struct, args):
        self._need(node, "set", args, 2)
        for entry in struct.map_entries():
            if entry.key == args[0]:
                entry.value = args[1]
                self.interp.highlights[struct.name] = [entry.id]
                self.interp._snapshot(
                    node.line,
                    f"{struct.name}[{self.interp._fmt(args[0])}] = {self.interp._fmt(args[1])}",
                )
                return
        self.interp._check_capacity(node.line, struct)
        entry = MapEntry(self.interp._next_id(), args[0], args[1])
        struct.items.append(entry)
        self.interp.highlights[struct.name] = [entry.id]
        self.interp._snapshot(
            node.line,
            f"{struct.name}.set({self.interp._fmt(args[0])}, {self.interp._fmt(args[1])})",
        )

    def _map_remove(self, node, struct, args):
        self._need(node, "remove", args, 1)
        for idx, entry in enumerate(struct.map_entries()):
            if entry.key == args[0]:
                struct.items.pop(idx)
                self.interp._snapshot(
                    node.line, f"{struct.name}.remove({self.interp._fmt(args[0])})"
                )
                return
        raise VisuRuntimeError(node.line, f"key {args[0]!r} not in map")

    def _graph_node(self, node, struct, args):
        self._need_between(node, "node", args, 1, 2)
        key = args[0]
        value = args[1] if len(args) == 2 else None
        if struct.find_node(key) is not None:
            raise VisuRuntimeError(node.line, f"node {key!r} already exists")
        self.interp._check_capacity(node.line, struct)
        new_node = GraphNode(self.interp._next_id(), key, value)
        struct.items.append(new_node)
        self.interp.highlights[struct.name] = [new_node.id]
        label = self.interp._fmt(key)
        if value is not None:
            label += f"={self.interp._fmt(value)}"
        self.interp._snapshot(node.line, f"{struct.name}.node({label})")

    def _graph_remove_node(self, node, struct, args):
        self._need(node, "remove_node", args, 1)
        key = args[0]
        target = struct.find_node(key)
        if target is None:
            raise VisuRuntimeError(node.line, f"node {key!r} not in graph")
        struct.items = [n for n in struct.graph_nodes() if n.key != key]
        struct.edges = [e for e in struct.edges if e.src != key and e.dst != key]
        self.interp._snapshot(
            node.line, f"{struct.name}.remove_node({self.interp._fmt(key)})"
        )

    def _graph_set_value(self, node, struct, args):
        self._need(node, "set_value", args, 2)
        target = struct.find_node(args[0])
        if target is None:
            raise VisuRuntimeError(node.line, f"node {args[0]!r} not in graph")
        target.value = args[1]
        self.interp.highlights[struct.name] = [target.id]
        self.interp._snapshot(
            node.line,
            f"{struct.name}.set_value({self.interp._fmt(args[0])}, {self.interp._fmt(args[1])})",
        )

    def _graph_edge(self, node, struct, args):
        self._need_between(node, "edge", args, 2, 3)
        src, dst = args[0], args[1]
        weight = args[2] if len(args) == 3 else None
        if struct.find_node(src) is None:
            raise VisuRuntimeError(node.line, f"node {src!r} not in graph")
        if struct.find_node(dst) is None:
            raise VisuRuntimeError(node.line, f"node {dst!r} not in graph")
        if struct.find_edge(src, dst) is not None:
            raise VisuRuntimeError(
                node.line, f"edge {src!r}->{dst!r} already exists"
            )
        self.interp._check_edge_capacity(node.line, struct)
        edge = GraphEdge(self.interp._next_id(), src, dst, weight)
        struct.edges.append(edge)
        src_node = struct.find_node(src)
        dst_node = struct.find_node(dst)
        if src_node and dst_node:
            self.interp.highlights[struct.name] = [src_node.id, dst_node.id]
        label = f"{self.interp._fmt(src)} → {self.interp._fmt(dst)}"
        if weight is not None:
            label += f"  w={self.interp._fmt(weight)}"
        self.interp._snapshot(node.line, f"{struct.name}.edge({label})")

    def _graph_remove_edge(self, node, struct, args):
        self._need(node, "remove_edge", args, 2)
        target = struct.find_edge(args[0], args[1])
        if target is None:
            raise VisuRuntimeError(
                node.line, f"edge {args[0]!r} → {args[1]!r} not in graph"
            )
        struct.edges.remove(target)
        self.interp._snapshot(
            node.line,
            f"{struct.name}.remove_edge({self.interp._fmt(args[0])}, {self.interp._fmt(args[1])})",
        )


def _query_set_contains(struct: Structure, args, node: Node):
    if len(args) != 1:
        raise VisuRuntimeError(node.line, "contains expects 1 argument")
    return any(item.value == args[0] for item in struct.linear_items())


def _query_set_size(struct: Structure, args, node: Node):
    return len(struct.items)


def _query_map_get(struct: Structure, args, node: Node):
    if len(args) != 1:
        raise VisuRuntimeError(node.line, "get expects 1 argument")
    for entry in struct.map_entries():
        if entry.key == args[0]:
            return entry.value
    return None


def _query_map_has(struct: Structure, args, node: Node):
    if len(args) != 1:
        raise VisuRuntimeError(node.line, "has expects 1 argument")
    return any(entry.key == args[0] for entry in struct.map_entries())


def _query_map_size(struct: Structure, args, node: Node):
    return len(struct.items)


def _query_graph_has_node(struct: Structure, args, node: Node):
    if len(args) != 1:
        raise VisuRuntimeError(node.line, "has_node expects 1 argument")
    return struct.find_node(args[0]) is not None


def _query_graph_has_edge(struct: Structure, args, node: Node):
    if len(args) != 2:
        raise VisuRuntimeError(node.line, "has_edge expects 2 arguments")
    return struct.find_edge(args[0], args[1]) is not None


def _query_graph_node_count(struct: Structure, args, node: Node):
    return len(struct.items)


def _query_graph_edge_count(struct: Structure, args, node: Node):
    return len(struct.edges)


def _query_graph_neighbors(struct: Structure, args, node: Node):
    if len(args) != 1:
        raise VisuRuntimeError(node.line, "neighbors expects 1 argument")
    key = args[0]
    result: list = []
    for edge in struct.edges:
        if edge.src == key:
            result.append(edge.dst)
        elif not struct.directed and edge.dst == key:
            result.append(edge.src)
    return result


def _query_graph_get_value(struct: Structure, args, node: Node):
    if len(args) != 1:
        raise VisuRuntimeError(node.line, "get_value expects 1 argument")
    target = struct.find_node(args[0])
    if target is None:
        raise VisuRuntimeError(node.line, f"node {args[0]!r} not in graph")
    return target.value


QUERY_METHODS = {
    ("set", "contains"): _query_set_contains,
    ("set", "size"): _query_set_size,
    ("map", "get"): _query_map_get,
    ("map", "has"): _query_map_has,
    ("map", "size"): _query_map_size,
    ("graph", "has_node"): _query_graph_has_node,
    ("graph", "has_edge"): _query_graph_has_edge,
    ("graph", "node_count"): _query_graph_node_count,
    ("graph", "edge_count"): _query_graph_edge_count,
    ("graph", "neighbors"): _query_graph_neighbors,
    ("graph", "get_value"): _query_graph_get_value,
}


def run_source(src: str) -> tuple[list[Snapshot], str | None]:
    interp = Interpreter()
    try:
        interp.run(src)
        return interp.snapshots, None
    except (LexError, ParseError, VisuRuntimeError) as e:
        return interp.snapshots, str(e)
