<p align="center">
  <img src="data/io.github.iionel.Visu.svg" width="128" height="128" alt="Visu">
</p>

<h1 align="center">Visu</h1>

<p align="center"><em>Visualize algorithms step by step.</em></p>

<p align="center">
  <a href="https://flathub.org/apps/io.github.iionel.Visu"><img src="https://img.shields.io/flathub/v/io.github.iionel.Visu?logo=flathub&label=Flathub" alt="Flathub"></a>
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT License">
  <img src="https://img.shields.io/badge/GTK-4-4A90D9?logo=gnome&logoColor=white" alt="GTK 4">
  <img src="https://img.shields.io/badge/python-3.10+-yellow?logo=python&logoColor=white" alt="Python 3.10+">
</p>

---

Write pseudocode in the editor, press **Run**, and the canvas replays every step on the structures you declared. A timeline at the bottom lets you scrub backwards and forwards through the execution — like a video player for your code.

Visu ships eight built-in structures (`array`, `stack`, `queue`, `deque`, `list`, `set`, `map`, and directed/undirected `graph`), each with a dedicated animated renderer. Built with Python, GTK 4, and libadwaita for modern GNOME desktops.

## Highlights

- **Purpose-built pseudocode language** — small, readable, no setup
- **Step-by-step timeline** — play, pause, step, scrub, and adjust speed
- **Live line highlighting** — see exactly which statement is running
- **Built-in reference** — every structure and helper documented with examples (`F1`)
- **Worked examples included** — bubble sort, DFS, union-find, and more

## Install

### Flatpak (recommended)

```bash
flatpak install flathub io.github.iionel.Visu
flatpak run io.github.iionel.Visu
```

### From source

Install the GTK 4 / libadwaita system libraries, then run directly:

```bash
# Debian / Ubuntu
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1

# Fedora
sudo dnf install python3-gobject gtk4 libadwaita python3-cairo

# Arch
sudo pacman -S python-gobject gtk4 libadwaita python-cairo
```

```bash
python3 -m visu
# or: pip install . && visu
```

### Build the Flatpak locally

```bash
flatpak install flathub org.gnome.Platform//50 org.gnome.Sdk//50
flatpak-builder --user --install --force-clean build-dir \
    flatpak/io.github.iionel.Visu.yml
flatpak run io.github.iionel.Visu
```

## Quick start

1. Launch the app. The editor loads a bundled example.
2. Edit the pseudocode on the right.
3. Press **Run** (`Ctrl+Return` or `F5`).
4. Watch the structures animate on the left. Scrub the timeline to step through.
5. Press `F1` to open the pseudocode reference.

## Keyboard shortcuts

| Action                 | Shortcut                  |
| ---------------------- | ------------------------- |
| Run program            | `Ctrl+Return`, `F5`       |
| Open file              | `Ctrl+O`                  |
| Save / Save as         | `Ctrl+S` / `Ctrl+Shift+S` |
| Undo / Redo            | `Ctrl+Z` / `Ctrl+Y`       |
| Pseudocode reference   | `F1`                      |
| Zoom in / out (canvas) | `+` / `-` or scroll       |
| Reset zoom and pan     | `0`                       |
| Quit                   | `Ctrl+Q`                  |

## Pseudocode reference

Every statement you execute creates a **snapshot**. Drag the timeline at the bottom to scrub backwards and forwards through your program — it's like a video player for your code.

### Values & variables

Expressions produce numbers, strings, booleans (`true` / `false`), `null`, or lists like `[1, 2, 3]`. Lists can hold other lists — graph nodes can carry a list, arrays can contain arrays, and so on.

Variables are created the moment you assign to them. No types, no declarations — just a name and a value.

```text
# Anything after a hash is a comment.
x = 10
y = x + 5
name = "alice"
flags = [true, false, true]
```

### Structures at a glance

Declare each structure once, give it a name, then operate on it by name. Each draws itself in its own way on the canvas.

```text
array  a = [5, 2, 9, 1]       # random-access sequence
stack  s = []                 # LIFO
queue  q = []                 # FIFO
deque  d = []                 # double-ended
list   l = [1, 2, 3]          # singly linked list
set    u = [1, 2, 2, 3]       # unique elements
map    m = []                 # key -> value table
graph  g = directed           # or: undirected
```

### `array` — random access

Indexed, ordered sequence you can read, write, grow, and shrink at will.

```text
array a = [5, 2, 9, 1]

a.push(v)            # append to the end
a.pop()              # remove the last element
a.insert(i, v)       # insert v at index i
a.remove(i)          # remove the element at index i
a[i] = v             # assign by index
a[i]                 # read by index
a.length             # number of elements
swap(a, i, j)        # swap two indices in place
```

### `stack` — last in, first out

Only the top is accessible. Great for undo histories, depth-first search, and matching brackets.

```text
stack s = []

s.push(v)            # add on top
s.pop()              # remove the top
s[s.length - 1]      # peek at the top
```

### `queue` — first in, first out

Items leave in the same order they joined. Perfect for breadth-first search and task scheduling.

```text
queue q = []

q.enqueue(v)         # join the back of the line
q.dequeue()          # remove from the front
q[0]                 # peek at the front
```

### `deque` — double-ended

A queue you can also push and pop from the front. Use it for sliding windows, palindrome checks, and the like.

```text
deque d = []

d.push_front(v)
d.push_back(v)
d.pop_front()
d.pop_back()
```

### `list` — linked list

A singly linked list draws each element as a node with an arrow to the next one. Great for showing pointers, splicing, and traversal.

```text
list l = [1, 2, 3]

l.append(v)          # add to the end
l.prepend(v)         # add to the front
l.remove(i)          # remove the i-th node
```

### `set` — unique elements

Each value appears at most once; adding a duplicate is a no-op. Use it to track "have I seen this already?" — visited nodes in a graph, for example.

```text
set u = [1, 2, 2, 3]   # duplicates dropped on init

u.add(v)
u.remove(v)
u.contains(v)        # boolean query
u.size               # how many elements
```

### `map` — key → value

Associates a key with a value. Reach for it when you want to count, group, or remember things by name.

```text
map m = []           # must start empty

m.set(key, value)    # insert or update
m.remove(key)
m.get(key)           # null if missing
m.has(key)           # boolean
m.size
```

### `graph` — nodes & edges

The most flexible structure in Visu. Each node has a key (any value — number, string, even a list) and an optional payload value. Edges connect two keys and may carry a weight. In an undirected graph the pair is symmetric.

```text
graph g = directed         # or: undirected

g.node("A")                # node, no payload
g.node("B", 42)            # node "B" with value 42
g.node("C", [1, 2])        # payload can be a list
g.edge("A", "B")           # unweighted edge
g.edge("B", "C", 3.5)      # weighted edge
g.set_value("A", 99)       # update a node's payload
g.remove_edge("A", "B")
g.remove_node("C")
```

Asking the graph questions:

```text
g.has_node("A")
g.has_edge("A", "B")
g.node_count
g.edge_count
g.neighbors("A")           # returns a list of keys
g.get_value("A")
```

### Control flow

Indentation is for readability, but every block is closed with `end`.

```text
if x > 5:
    print("big")
else:
    print("small")
end

for i from 0 to a.length:
    print(a[i])
end

while x < 10:
    x = x + 1
end
```

`for i from A to B` walks `i` through `A, A+1, …, B-1`. The upper bound is exclusive, so `for i from 0 to a.length` covers every index of `a`.

### Operators

```text
+   -   *   /   %        arithmetic
==  !=  <   >   <=  >=   comparison
and    or    not         boolean
```

### Built-in helpers

```text
print(x, y, ...)         write to the output panel
highlight(target, ...)   flash elements on the canvas
                         (indices for linear structures,
                          keys for graph / map / set)
swap(arr, i, j)          swap two array elements
```

Sprinkle `highlight(...)` calls into your loops to draw attention to the element you're currently comparing or visiting — it makes the replay far easier to follow.

### Worked examples

**Bubble sort** — watch the largest values bubble to the right one swap at a time.

```text
array a = [5, 2, 9, 1, 7, 3]
for i from 0 to a.length:
    for j from 0 to a.length - 1:
        if a[j] > a[j + 1]:
            swap(a, j, j + 1)
        end
    end
end
```

**Breadth-first search on a graph** — three structures cooperating: a queue for the frontier, a set for visited nodes, and an array for the visit order.

```text
graph g = undirected
g.node("A")
g.node("B")
g.node("C")
g.node("D")
g.edge("A", "B")
g.edge("A", "C")
g.edge("B", "D")
g.edge("C", "D")

queue frontier = []
set   visited  = []
array order    = []

frontier.enqueue("A")
visited.add("A")

while frontier.length > 0:
    cur = frontier[0]
    frontier.dequeue()
    order.push(cur)
    neigh = g.neighbors(cur)
    for i from 0 to neigh.length:
        nxt = neigh[i]
        if not visited.contains(nxt):
            visited.add(nxt)
            frontier.enqueue(nxt)
        end
    end
end
```

**Word frequency with a map**

```text
array words = ["a", "b", "a", "c", "b", "a"]
map counts = []
for i from 0 to words.length:
    w = words[i]
    if counts.has(w):
        counts.set(w, counts.get(w) + 1)
    else:
        counts.set(w, 1)
    end
end
```

More examples (insertion sort, selection sort, iterative quicksort, DFS, union-find) ship inside the app — open the menu and pick one.

## Project layout

```
visu/
    app.py              Application entry point and global actions
    docs.py             Pseudocode reference content
    interpreter/        Lexer, parser, runtime, snapshot recording
    render/             Canvas, animators, per-structure renderers
    ui/                 Window, panels, timeline, dialogs
data/                   Desktop file, AppStream metadata, icon, screenshots
flatpak/                Flathub manifest
tests/                  Test suite
```

## Development

```bash
python3 -m pytest
```

The interpreter pipeline lives under `visu/interpreter/` (lexer, parser, runtime, snapshots, structures). Each canvas renderer is a class under `visu/render/renderers/` that computes a natural layout and draws onto a Cairo context. The UI layer under `visu/ui/` wires everything together with GTK 4 widgets.

## Contributing

Bug reports and pull requests are welcome on the [issue tracker](https://github.com/iIonel/Visu/issues).

## License

Released under the [MIT License](LICENSE).
