from __future__ import annotations

import gi

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")
from gi.repository import Adw, Gtk, Pango

from ..docs import DOCS_SECTIONS


class DocsWindow(Adw.Window):

    def __init__(self, parent: Gtk.Window):
        super().__init__()
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_title("Pseudocode reference")
        self.set_default_size(960, 720)

        _install_docs_css()

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        header = Adw.HeaderBar()
        header.add_css_class("flat")
        title = Adw.WindowTitle(
            title="Pseudocode reference",
            subtitle="A friendly tour of the Visu language",
        )
        header.set_title_widget(title)
        root.append(header)

        body = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        body.set_vexpand(True)
        root.append(body)

        self._stack = Gtk.Stack()
        self._stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self._stack.set_transition_duration(160)
        self._stack.set_hexpand(True)
        self._stack.set_vexpand(True)

        body.append(self._build_sidebar())
        body.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        body.append(self._stack)

        for section in DOCS_SECTIONS:
            self._stack.add_named(self._build_section(section), section["id"])

        self.set_content(root)

        if DOCS_SECTIONS:
            self._select_row(0)

    def _build_sidebar(self) -> Gtk.Widget:
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        scroll.set_size_request(240, -1)

        listbox = Gtk.ListBox()
        listbox.add_css_class("navigation-sidebar")
        listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        listbox.connect("row-selected", self._on_row_selected)

        for section in DOCS_SECTIONS:
            row = Gtk.ListBoxRow()
            row.section_id = section["id"]
            label = Gtk.Label(label=section["title"], xalign=0)
            label.set_margin_top(9)
            label.set_margin_bottom(9)
            label.set_margin_start(14)
            label.set_margin_end(14)
            label.set_hexpand(True)
            label.set_ellipsize(Pango.EllipsizeMode.END)
            row.set_child(label)
            listbox.append(row)

        self._listbox = listbox
        scroll.set_child(listbox)
        return scroll

    def _build_section(self, section: dict) -> Gtk.Widget:
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        outer.set_halign(Gtk.Align.CENTER)
        outer.set_margin_top(28)
        outer.set_margin_bottom(36)
        outer.set_margin_start(36)
        outer.set_margin_end(36)
        outer.set_size_request(620, -1)

        title = Gtk.Label(label=section["title"], xalign=0)
        title.add_css_class("docs-title")
        title.set_wrap(True)
        outer.append(title)

        spacer = Gtk.Box()
        spacer.set_size_request(-1, 12)
        outer.append(spacer)

        for block in section["blocks"]:
            outer.append(_build_block(block))

        scroll.set_child(outer)
        return scroll

    def _on_row_selected(self, _listbox, row):
        if row is None:
            return
        self._stack.set_visible_child_name(row.section_id)

    def _select_row(self, index: int):
        row = self._listbox.get_row_at_index(index)
        if row is not None:
            self._listbox.select_row(row)


def _build_block(block: dict) -> Gtk.Widget:
    kind = block["kind"]
    text = block["text"]

    if kind == "p":
        label = Gtk.Label(label=text, xalign=0)
        label.set_wrap(True)
        label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        label.set_max_width_chars(70)
        label.add_css_class("docs-body")
        label.set_margin_bottom(14)
        return label

    if kind == "h":
        label = Gtk.Label(label=text, xalign=0)
        label.add_css_class("docs-subhead")
        label.set_margin_top(10)
        label.set_margin_bottom(8)
        return label

    if kind == "code":
        frame = Gtk.Frame()
        frame.add_css_class("docs-code")
        frame.set_margin_bottom(16)
        view = Gtk.TextView()
        view.set_editable(False)
        view.set_cursor_visible(False)
        view.set_monospace(True)
        view.set_wrap_mode(Gtk.WrapMode.NONE)
        view.set_top_margin(12)
        view.set_bottom_margin(12)
        view.set_left_margin(16)
        view.set_right_margin(16)
        view.get_buffer().set_text(text)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        scroll.set_propagate_natural_height(True)
        scroll.set_child(view)
        frame.set_child(scroll)
        return frame

    if kind == "tip":
        label = Gtk.Label(label=text, xalign=0)
        label.add_css_class("docs-tip")
        label.set_wrap(True)
        label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        label.set_max_width_chars(64)
        label.set_hexpand(True)
        label.set_margin_bottom(16)
        return label

    return Gtk.Label(label=text, xalign=0)


_DOCS_CSS_INSTALLED = False


def _install_docs_css():
    global _DOCS_CSS_INSTALLED
    if _DOCS_CSS_INSTALLED:
        return
    _DOCS_CSS_INSTALLED = True

    from gi.repository import Gdk

    css = b"""
    .docs-title {
        font-size: 22pt;
        font-weight: 700;
        letter-spacing: -0.01em;
    }
    .docs-subhead {
        font-size: 13pt;
        font-weight: 600;
        opacity: 0.92;
    }
    .docs-body {
        font-size: 11pt;
        line-height: 1.55;
        opacity: 0.88;
    }
    .docs-code {
        background-color: alpha(@card_bg_color, 0.55);
        border-radius: 10px;
        border: 1px solid alpha(@borders, 0.5);
    }
    .docs-code textview {
        background: transparent;
        font-family: "JetBrains Mono","Fira Code","Source Code Pro",monospace;
        font-size: 10.5pt;
    }
    .docs-tip {
        background-color: alpha(@accent_bg_color, 0.18);
        border-left: 3px solid @accent_color;
        border-radius: 8px;
        padding: 12px 14px;
    }
    """

    provider = Gtk.CssProvider()
    provider.load_from_data(css)
    display = Gdk.Display.get_default()
    if display is not None:
        Gtk.StyleContext.add_provider_for_display(
            display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
