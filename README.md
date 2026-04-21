# Visu

Visu is an interactive visualizer for classic algorithms and data structures.
You write pseudocode in the built-in editor, press **Run**, and the canvas
replays every step on the structures you declared. A timeline at the bottom
lets you scrub backwards and forwards through the execution like a video
player for your code.

Visu is built with Python, GTK 4 and libadwaita, and targets modern GNOME
desktops.

---

## What it does

Visu ships a small, purpose-built pseudocode language with eight data
structures: `array`, `stack`, `queue`, `deque`, linked `list`, `set`, `map`,
and directed or undirected `graph`. Each structure has its own animated
renderer on the canvas.

Every statement you execute creates a **snapshot**. The timeline lets you
play, pause, step forward, step backward, and adjust playback speed so you
can study an algorithm at your own pace.

The editor highlights the line currently being executed. Output from `print`
calls appears in a dedicated panel below the editor. A built-in pseudocode
reference (press `F1` or open it from the menu) documents every structure,
method, and language feature with worked examples.

---

## Installation

### From source

Visu depends on PyGObject and pycairo, which need the system GTK 4 and
libadwaita libraries installed first.

```bash
# Debian / Ubuntu
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1

# Fedora
sudo dnf install python3-gobject gtk4 libadwaita python3-cairo

# Arch
sudo pacman -S python-gobject gtk4 libadwaita python-cairo
```

Run directly from the repository:

```bash
python3 -m visu
```

Or install the package:

```bash
pip install .
visu
```

### Flatpak

A Flathub-ready manifest lives at `flatpak/io.github.iionel.Visu.yml`:

```bash
flatpak install flathub org.gnome.Platform//50 org.gnome.Sdk//50
flatpak-builder --user --install --force-clean build-dir \
    flatpak/io.github.iionel.Visu.yml
flatpak run io.github.iionel.Visu
```

---

## Quick start

1. Launch the application. The editor loads a bundled example so you can
   run something immediately.
2. Edit or replace the pseudocode on the right.
3. Press **Run** (`Ctrl+Return` or `F5`).
4. Watch the structures animate on the left. Use the timeline to step
   through the execution frame by frame.
5. Open the menu to load files, browse the pseudocode reference, or read
   the about dialog.

---

## Keyboard shortcuts

| Action                          | Shortcut             |
| ------------------------------- | -------------------- |
| Run program                     | `Ctrl+Return`, `F5`  |
| Open file                       | `Ctrl+O`             |
| Save                            | `Ctrl+S`             |
| Save as                         | `Ctrl+Shift+S`       |
| Undo / Redo                     | `Ctrl+Z` / `Ctrl+Y`  |
| Pseudocode reference            | `F1`                 |
| Quit                            | `Ctrl+Q`             |
| Zoom in / out (canvas)          | `+` / `-` or scroll  |
| Reset zoom and pan              | `0`                  |

---

## The pseudocode language

The language is intentionally small. The full reference ships inside the
application; the snippet below covers the essentials.

### Declaring structures

```text
array a = [5, 2, 9, 1]
stack s = []
queue q = []
deque d = []
list  l = [1, 2, 3]
set   u = [1, 2, 2, 3]
map   m = []
graph g = directed
```

### Operating on structures

```text
a.push(4)
a[0] = 99
swap(a, 0, 1)
s.push(10)
q.enqueue("task")
d.push_front(0)
l.append(42)
u.add("seen")
m.set("alice", 30)
g.node("A")
g.edge("A", "B", 3.5)
```

### Control flow

```text
if a.length > 0:
    print("not empty")
else:
    print("empty")
end

for i from 0 to a.length:
    print(a[i])
end

while x < 10:
    x = x + 1
end
```

### Built-in helpers

```text
print(x, y, ...)
highlight(target, ...)
swap(arr, i, j)
```

A complete tour with worked examples (bubble sort, breadth-first search,
word frequency counting) is available inside the app via the menu or `F1`.

---

## Project layout

```
visu/
    app.py              Application entry point and global actions
    docs.py             Pseudocode reference content
    interpreter/        Lexer, parser, runtime, and snapshot recording
    render/             Canvas, animators, and renderers for each structure
    ui/                 Window, panels, timeline, dialogs
data/                   Desktop file, AppStream metadata, icon
flatpak/                Flathub manifest
```

---

## Development

Run the test suite:

```bash
python3 -m pytest
```

The interpreter pipeline lives under `visu/interpreter/` (lexer, parser,
runtime, snapshots, structures). Each canvas renderer is a class under
`visu/render/renderers/` that computes a natural layout and draws onto a
Cairo context. The UI layer under `visu/ui/` wires everything together with
GTK 4 widgets.

---

## License

MIT
