from __future__ import annotations

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, Gtk


CSS = b"""
textview {
    background: transparent;
    font-family: "JetBrains Mono","Fira Code","Source Code Pro",monospace;
    font-size: 12pt;
}
.visu-editor-card {
    background-color: alpha(@card_bg_color, 0.55);
    border-radius: 10px;
    border: 1px solid alpha(@borders, 0.5);
    padding: 2px;
}
.visu-canvas-frame {
    border-radius: 12px;
}
.visu-section-label {
    font-size: 10pt;
    letter-spacing: 0.04em;
}
.visu-timeline scale {
    min-height: 24px;
}
"""


def install_css():
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS)
    display = Gdk.Display.get_default()
    if display is not None:
        Gtk.StyleContext.add_provider_for_display(
            display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
