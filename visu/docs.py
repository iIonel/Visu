from __future__ import annotations


DOCS_SECTIONS: list[dict] = [
    {
        "id": "welcome",
        "title": "Welcome to Visu",
        "icon": "👋",
        "blocks": [
            {
                "kind": "p",
                "text": (
                    "Visu runs a tiny pseudocode language built for one thing: "
                    "watching algorithms and data structures come alive, step "
                    "by step. You write code on the right, press Run, and the "
                    "canvas on the left replays every change."
                ),
            },
            {
                "kind": "p",
                "text": (
                    "Every statement you execute creates a snapshot. Drag the "
                    "timeline at the bottom to scrub backwards and forwards "
                    "through your program — it's like a video player for "
                    "your code."
                ),
            },
            {
                "kind": "tip",
                "text": (
                    "New here? Open the bundled example from the menu, hit "
                    "Run, and play with the timeline before reading anything "
                    "else. The fastest way to learn Visu is to watch it move."
                ),
            },
            {
                "kind": "h", "text": "How a Visu program is built",
            },
            {
                "kind": "p",
                "text": (
                    "1. Declare the structures you want to visualize "
                    "(arrays, stacks, graphs…).\n"
                    "2. Operate on them with simple statements and loops.\n"
                    "3. Press Run, then scrub the timeline to replay it."
                ),
            },
        ],
    },
    {
        "id": "values",
        "title": "Values & variables",
        "icon": "🔢",
        "blocks": [
            {
                "kind": "p",
                "text": (
                    "Expressions in Visu can produce numbers, strings, "
                    "booleans (true / false), null, or lists like "
                    "[1, 2, 3]. Lists can hold other lists, so a graph "
                    "node can carry a list, an array can contain arrays, "
                    "and so on."
                ),
            },
            {
                "kind": "h", "text": "Comments",
            },
            {
                "kind": "code",
                "text": "# Anything after a hash is ignored — use it to leave notes.",
            },
            {
                "kind": "h", "text": "Variables",
            },
            {
                "kind": "p",
                "text": (
                    "Variables are created the moment you assign to them. "
                    "No types, no declarations — just a name and a value."
                ),
            },
            {
                "kind": "code",
                "text": (
                    "x = 10\n"
                    "y = x + 5\n"
                    "name = \"alice\"\n"
                    "flags = [true, false, true]"
                ),
            },
        ],
    },
    {
        "id": "structures",
        "title": "Structures at a glance",
        "icon": "📦",
        "blocks": [
            {
                "kind": "p",
                "text": (
                    "Visu has eight built-in structures. You declare each "
                    "one once, give it a name, and from then on you operate "
                    "on it by name. Each structure draws itself in its own "
                    "way on the canvas."
                ),
            },
            {
                "kind": "code",
                "text": (
                    "array  a = [5, 2, 9, 1]       # random-access sequence\n"
                    "stack  s = []                 # LIFO\n"
                    "queue  q = []                 # FIFO\n"
                    "deque  d = []                 # double-ended\n"
                    "list   l = [1, 2, 3]          # singly linked list\n"
                    "set    u = [1, 2, 2, 3]       # unique elements\n"
                    "map    m = []                 # key -> value table\n"
                    "graph  g = directed           # or: undirected"
                ),
            },
            {
                "kind": "tip",
                "text": (
                    "Pick the structure that matches what you want to "
                    "show. Sorting? Use array. Exploring a maze? Queue or "
                    "stack. Counting words? Map. The visualization will "
                    "follow your choice."
                ),
            },
        ],
    },
    {
        "id": "array",
        "title": "array — random access",
        "icon": "📚",
        "blocks": [
            {
                "kind": "p",
                "text": (
                    "An array is the workhorse of algorithms: an indexed, "
                    "ordered sequence you can read, write, grow, and "
                    "shrink at will."
                ),
            },
            {
                "kind": "code",
                "text": (
                    "array a = [5, 2, 9, 1]\n"
                    "\n"
                    "a.push(v)            # append to the end\n"
                    "a.pop()              # remove the last element\n"
                    "a.insert(i, v)       # insert v at index i\n"
                    "a.remove(i)          # remove the element at index i\n"
                    "a[i] = v             # assign by index\n"
                    "a[i]                 # read by index\n"
                    "a.length             # number of elements\n"
                    "swap(a, i, j)        # swap two indices in place"
                ),
            },
        ],
    },
    {
        "id": "stack",
        "title": "stack — last in, first out",
        "icon": "🥞",
        "blocks": [
            {
                "kind": "p",
                "text": (
                    "A stack only lets you touch the top. Great for "
                    "undo histories, depth-first search, and matching "
                    "brackets."
                ),
            },
            {
                "kind": "code",
                "text": (
                    "stack s = []\n"
                    "\n"
                    "s.push(v)            # add on top\n"
                    "s.pop()              # remove the top\n"
                    "s[s.length - 1]      # peek at the top"
                ),
            },
        ],
    },
    {
        "id": "queue",
        "title": "queue — first in, first out",
        "icon": "🚶",
        "blocks": [
            {
                "kind": "p",
                "text": (
                    "A queue is a polite line: items leave in the same "
                    "order they joined. Perfect for breadth-first search "
                    "and task scheduling."
                ),
            },
            {
                "kind": "code",
                "text": (
                    "queue q = []\n"
                    "\n"
                    "q.enqueue(v)         # join the back of the line\n"
                    "q.dequeue()          # remove from the front\n"
                    "q[0]                 # peek at the front"
                ),
            },
        ],
    },
    {
        "id": "deque",
        "title": "deque — double-ended",
        "icon": "↔️",
        "blocks": [
            {
                "kind": "p",
                "text": (
                    "A deque is a queue you can also push and pop from "
                    "the front. Use it when you need flexibility on both "
                    "ends — sliding windows, palindrome checks, and so on."
                ),
            },
            {
                "kind": "code",
                "text": (
                    "deque d = []\n"
                    "\n"
                    "d.push_front(v)\n"
                    "d.push_back(v)\n"
                    "d.pop_front()\n"
                    "d.pop_back()"
                ),
            },
        ],
    },
    {
        "id": "list",
        "title": "list — linked list",
        "icon": "🔗",
        "blocks": [
            {
                "kind": "p",
                "text": (
                    "A singly linked list draws each element as a node "
                    "with an arrow to the next one. Great for showing how "
                    "pointers, splicing, and traversal really work."
                ),
            },
            {
                "kind": "code",
                "text": (
                    "list l = [1, 2, 3]\n"
                    "\n"
                    "l.append(v)          # add to the end\n"
                    "l.prepend(v)         # add to the front\n"
                    "l.remove(i)          # remove the i-th node"
                ),
            },
        ],
    },
    {
        "id": "set",
        "title": "set — unique elements",
        "icon": "🎯",
        "blocks": [
            {
                "kind": "p",
                "text": (
                    "A set keeps each value at most once. Adding a "
                    "duplicate is a no-op. Use it to track \"have I "
                    "seen this already?\" — visited nodes in a graph, "
                    "for example."
                ),
            },
            {
                "kind": "code",
                "text": (
                    "set u = [1, 2, 2, 3]   # duplicates dropped on init\n"
                    "\n"
                    "u.add(v)\n"
                    "u.remove(v)\n"
                    "u.contains(v)        # boolean query\n"
                    "u.size               # how many elements"
                ),
            },
        ],
    },
    {
        "id": "map",
        "title": "map — key → value",
        "icon": "🗺️",
        "blocks": [
            {
                "kind": "p",
                "text": (
                    "A map associates a key with a value. Reach for it "
                    "when you want to count things, group things, or "
                    "remember things by name."
                ),
            },
            {
                "kind": "code",
                "text": (
                    "map m = []           # must start empty\n"
                    "\n"
                    "m.set(key, value)    # insert or update\n"
                    "m.remove(key)\n"
                    "m.get(key)           # null if missing\n"
                    "m.has(key)           # boolean\n"
                    "m.size"
                ),
            },
        ],
    },
    {
        "id": "graph",
        "title": "graph — nodes & edges",
        "icon": "🕸️",
        "blocks": [
            {
                "kind": "p",
                "text": (
                    "Graphs are the most flexible structure in Visu. "
                    "Each node has a key (any value — number, string, "
                    "even a list) and an optional payload value. Edges "
                    "connect two keys and may carry a weight. In an "
                    "undirected graph, the pair is symmetric."
                ),
            },
            {
                "kind": "code",
                "text": (
                    "graph g = directed         # or: undirected\n"
                    "\n"
                    "g.node(\"A\")                # node, no payload\n"
                    "g.node(\"B\", 42)            # node \"B\" with value 42\n"
                    "g.node(\"C\", [1, 2])        # payload can be a list\n"
                    "g.edge(\"A\", \"B\")           # unweighted edge\n"
                    "g.edge(\"B\", \"C\", 3.5)      # weighted edge\n"
                    "g.set_value(\"A\", 99)       # update a node's payload\n"
                    "g.remove_edge(\"A\", \"B\")\n"
                    "g.remove_node(\"C\")"
                ),
            },
            {
                "kind": "h", "text": "Asking the graph questions",
            },
            {
                "kind": "code",
                "text": (
                    "g.has_node(\"A\")\n"
                    "g.has_edge(\"A\", \"B\")\n"
                    "g.node_count\n"
                    "g.edge_count\n"
                    "g.neighbors(\"A\")           # returns a list of keys\n"
                    "g.get_value(\"A\")"
                ),
            },
        ],
    },
    {
        "id": "control-flow",
        "title": "Control flow",
        "icon": "🔁",
        "blocks": [
            {
                "kind": "p",
                "text": (
                    "Visu uses indentation for readability, but every "
                    "block is closed with the keyword end. Pick the "
                    "shape that fits and don't forget to close it."
                ),
            },
            {
                "kind": "h", "text": "if / else",
            },
            {
                "kind": "code",
                "text": (
                    "if x > 5:\n"
                    "    print(\"big\")\n"
                    "else:\n"
                    "    print(\"small\")\n"
                    "end"
                ),
            },
            {
                "kind": "h", "text": "for",
            },
            {
                "kind": "p",
                "text": (
                    "for i from A to B walks i through A, A+1, …, B-1. "
                    "The upper bound is exclusive, so for i from 0 to "
                    "a.length covers every index of a."
                ),
            },
            {
                "kind": "code",
                "text": (
                    "for i from 0 to a.length:\n"
                    "    print(a[i])\n"
                    "end"
                ),
            },
            {
                "kind": "h", "text": "while",
            },
            {
                "kind": "code",
                "text": (
                    "while x < 10:\n"
                    "    x = x + 1\n"
                    "end"
                ),
            },
        ],
    },
    {
        "id": "operators",
        "title": "Operators",
        "icon": "➕",
        "blocks": [
            {
                "kind": "p",
                "text": (
                    "Standard arithmetic, comparison, and boolean "
                    "operators — nothing surprising."
                ),
            },
            {
                "kind": "code",
                "text": (
                    "+   -   *   /   %        arithmetic\n"
                    "==  !=  <   >   <=  >=   comparison\n"
                    "and    or    not         boolean"
                ),
            },
        ],
    },
    {
        "id": "builtins",
        "title": "Built-in helpers",
        "icon": "🛠️",
        "blocks": [
            {
                "kind": "p",
                "text": (
                    "A small set of helpers do the things every "
                    "visualization eventually needs."
                ),
            },
            {
                "kind": "code",
                "text": (
                    "print(x, y, ...)         write to the output panel\n"
                    "highlight(target, ...)   flash elements on the canvas\n"
                    "                         (indices for linear structures,\n"
                    "                          keys for graph / map / set)\n"
                    "swap(arr, i, j)          swap two array elements"
                ),
            },
            {
                "kind": "tip",
                "text": (
                    "Sprinkle highlight(...) calls into your loops to "
                    "draw attention to the element you're currently "
                    "comparing or visiting. It makes the replay so much "
                    "easier to follow."
                ),
            },
        ],
    },
    {
        "id": "examples",
        "title": "Worked examples",
        "icon": "✨",
        "blocks": [
            {
                "kind": "h", "text": "Bubble sort",
            },
            {
                "kind": "p",
                "text": (
                    "A classic. Watch the largest values bubble to the "
                    "right one swap at a time."
                ),
            },
            {
                "kind": "code",
                "text": (
                    "array a = [5, 2, 9, 1, 7, 3]\n"
                    "for i from 0 to a.length:\n"
                    "    for j from 0 to a.length - 1:\n"
                    "        if a[j] > a[j + 1]:\n"
                    "            swap(a, j, j + 1)\n"
                    "        end\n"
                    "    end\n"
                    "end"
                ),
            },
            {
                "kind": "h", "text": "Breadth-first search on a graph",
            },
            {
                "kind": "p",
                "text": (
                    "Three structures cooperating: a queue for the "
                    "frontier, a set for visited nodes, and an array "
                    "for the visit order."
                ),
            },
            {
                "kind": "code",
                "text": (
                    "graph g = undirected\n"
                    "g.node(\"A\")\n"
                    "g.node(\"B\")\n"
                    "g.node(\"C\")\n"
                    "g.node(\"D\")\n"
                    "g.edge(\"A\", \"B\")\n"
                    "g.edge(\"A\", \"C\")\n"
                    "g.edge(\"B\", \"D\")\n"
                    "g.edge(\"C\", \"D\")\n"
                    "\n"
                    "queue frontier = []\n"
                    "set   visited  = []\n"
                    "array order    = []\n"
                    "\n"
                    "frontier.enqueue(\"A\")\n"
                    "visited.add(\"A\")\n"
                    "\n"
                    "while frontier.length > 0:\n"
                    "    cur = frontier[0]\n"
                    "    frontier.dequeue()\n"
                    "    order.push(cur)\n"
                    "    neigh = g.neighbors(cur)\n"
                    "    for i from 0 to neigh.length:\n"
                    "        nxt = neigh[i]\n"
                    "        if not visited.contains(nxt):\n"
                    "            visited.add(nxt)\n"
                    "            frontier.enqueue(nxt)\n"
                    "        end\n"
                    "    end\n"
                    "end"
                ),
            },
            {
                "kind": "h", "text": "Word frequency with a map",
            },
            {
                "kind": "code",
                "text": (
                    "array words = [\"a\", \"b\", \"a\", \"c\", \"b\", \"a\"]\n"
                    "map counts = []\n"
                    "for i from 0 to words.length:\n"
                    "    w = words[i]\n"
                    "    if counts.has(w):\n"
                    "        counts.set(w, counts.get(w) + 1)\n"
                    "    else:\n"
                    "        counts.set(w, 1)\n"
                    "    end\n"
                    "end"
                ),
            },
        ],
    },
]


DEFAULT_EXAMPLE = """\
# Welcome to Visu.
# Write pseudocode on the right, press Run, and watch
# the structures on the left. Scrub the timeline to replay.

graph g = directed
g.node("A", 0)
g.node("B", 1)
g.node("C", 2)
g.node("D", 3)
g.edge("A", "B", 4)
g.edge("A", "C", 2)
g.edge("B", "C", 1)
g.edge("B", "D", 5)
g.edge("C", "D", 8)

array order = []
for i from 0 to g.node_count:
    order.push(i)
end

print("nodes:", g.node_count, "edges:", g.edge_count)
"""
