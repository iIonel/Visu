# Visu

Visu is an interactive visualizer for classic algorithms and data structures.
You write a small pseudocode program in the editor, press **Run**, and the
canvas replays every step on the data structures you declared. A timeline at
the bottom of the canvas lets you scrub backwards and forwards through the
execution like a video.

Visu is built with Python, GTK 4 and libadwaita, and is designed to feel at
home on modern GNOME desktops.

---

## Highlights

- **Eight built-in structures.** `array`, `stack`, `queue`, `deque`, linked
  `list`, `set`, `map`, and directed or undirected `graph`. Each one has its
  own renderer on the canvas.
- **Step-by-step replay.** Every statement produces a snapshot. The timeline
  exposes play, pause, and frame-by-frame stepping so you can study an
  algorithm at your own pace.
- **A small, readable pseudocode language.** Familiar `if` / `for` / `while`
  control flow, simple expressions, and direct method calls on the
  structures you declare. No types to learn, no boilerplate.
- **In-app reference.** A friendly tour of the language ships with the
  application (menu → *Pseudocode reference*, or press `F1`).
- **File support.** Open and save `.visu` source files; the most recent
  file is restored on the next launch.
- **Native look and feel.** Adwaita styling, dark mode by default, keyboard
  shortcuts, and a Flatpak manifest targeting Flathub.

---

## Screenshots

The split layout puts the canvas on the left and the editor on the right,
with the playback timeline anchored under the canvas. Output from `print`
calls appears in the panel below the editor, and the line currently being
executed is highlighted as you scrub the timeline.

---

## Installation

### From source

Visu depends on PyGObject and pycairo, which in turn need the system GTK 4
and libadwaita libraries. Install the platform packages first, then run
the module directly from the repository.

```bash
# Debian / Ubuntu
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1

# Fedora
sudo dnf install python3-gobject gtk4 libadwaita python3-cairo

# Arch
sudo pacman -S python-gobject gtk4 libadwaita python-cairo
```

Then, from the project root:

```bash
python3 -m visu
```

Optionally install the package into your environment:

```bash
pip install .
visu
```

### Flatpak

A Flathub-ready manifest lives at `flatpak/io.github.iionel.Visu.yml`. To
build and install it locally:

```bash
flatpak install flathub org.gnome.Platform//47 org.gnome.Sdk//47
flatpak-builder --user --install --force-clean build-dir \
    flatpak/io.github.iionel.Visu.yml
flatpak run io.github.iionel.Visu
```

---

## Using Visu

1. Launch the application. The editor starts with a small bundled example
   so you have something to run immediately.
2. Edit or replace the pseudocode on the right.
3. Press **Run** in the header bar (or `Ctrl+Return` / `F5`).
4. Watch the structures animate on the left and use the timeline to step
   through the execution.
5. Use the menu (the button on the right of the header bar) to open or
   save files, load the bundled example, browse the pseudocode reference,
   or read the about dialog.

### Keyboard shortcuts

| Action                          | Shortcut             |
| ------------------------------- | -------------------- |
| Run program                     | `Ctrl+Return`, `F5`  |
| Open file                       | `Ctrl+O`             |
| Save                            | `Ctrl+S`             |
| Save as                         | `Ctrl+Shift+S`       |
| Undo / Redo                     | `Ctrl+Z` / `Ctrl+Y`  |
| Pseudocode reference            | `F1`                 |
| Quit                            | `Ctrl+Q`             |

---

## The pseudocode language

Visu's language is intentionally small. The complete reference is built
into the application; the snippet below is enough to get started.

```text
# Declare structures by kind and name.
array a = [5, 2, 9, 1]
stack s = []
queue q = []
deque d = []
list  l = [1, 2, 3]
set   u = []
map   m = []
graph g = directed

# Operate on them with method calls.
a.push(4)
swap(a, 0, 1)
s.push(10)
q.enqueue("task")
d.push_front(0)
l.append(42)
u.add("seen")
m.set("alice", 30)
g.node("A")
g.edge("A", "B", 3.5)

# Standard control flow.
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

# Built-in helpers.
print(a, "done")
highlight(a, 0, 1)
```

A complete tour with worked examples (bubble sort, breadth-first search,
word frequency counting) is available inside the app at any time via the
menu or `F1`.

---

## Project layout

```
visu/
    app.py              Application entry point and global actions
    docs.py              Pseudocode reference content
    interpreter/         Lexer, parser, runtime, and snapshot recording
    render/              Canvas renderers for each structure kind
    ui/                  Window, panels, timeline, dialogs
data/                    Desktop file, AppStream metadata, icon
flatpak/                 Flathub manifest
tests/                   Unit tests for the interpreter
```

---

## Development

Run the test suite from the project root:

```bash
python3 -m pytest
```

When working on the interpreter, the lexer, parser, runtime, and snapshot
machinery live under `visu/interpreter/`. Each canvas renderer is a small
class under `visu/render/renderers/` that takes a snapshot and draws onto a
Cairo context.

---

## License

Visu is released under the MIT License. See the project metadata for
details.
