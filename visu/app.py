from __future__ import annotations

from pathlib import Path

import gi

gi.require_version("Adw", "1")
gi.require_version("Gdk", "4.0")
gi.require_version("Gtk", "4.0")
from gi.repository import Adw, Gdk, Gio, Gtk

from . import APP_ID
from .ui import VisuWindow

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class VisuApplication(Adw.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID, flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self._register_icon()
        self._window: VisuWindow | None = None
        self._install_actions()

    @staticmethod
    def _register_icon():
        icons_dir = _DATA_DIR / "icons"
        if not icons_dir.is_dir():
            return
        theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        theme.add_search_path(str(icons_dir))

    def _install_actions(self):
        actions = (
            ("open", self._action_open),
            ("save", self._action_save),
            ("save_as", self._action_save_as),
            ("undo", self._action_undo),
            ("redo", self._action_redo),
            ("run", self._action_run),
            ("docs", self._action_docs),
            ("example", self._action_example),
            ("about", self._action_about),
            ("quit", lambda *_: self.quit()),
        )
        for name, handler in actions:
            action = Gio.SimpleAction.new(name, None)
            action.connect("activate", handler)
            self.add_action(action)

        self.set_accels_for_action("app.open", ["<Ctrl>o"])
        self.set_accels_for_action("app.save", ["<Ctrl>s"])
        self.set_accels_for_action("app.save_as", ["<Ctrl><Shift>s"])
        self.set_accels_for_action("app.undo", ["<Ctrl>z"])
        self.set_accels_for_action("app.redo", ["<Ctrl><Shift>z", "<Ctrl>y"])
        self.set_accels_for_action("app.run", ["<Ctrl>Return", "F5"])
        self.set_accels_for_action("app.quit", ["<Ctrl>q"])
        self.set_accels_for_action("app.docs", ["F1"])

    def _action_open(self, *_):
        if self._window:
            self._window.open_file()

    def _action_save(self, *_):
        if self._window:
            self._window.save_file()

    def _action_save_as(self, *_):
        if self._window:
            self._window.save_file_as()

    def _action_undo(self, *_):
        if self._window:
            self._window.undo()

    def _action_redo(self, *_):
        if self._window:
            self._window.redo()

    def _action_run(self, *_):
        if self._window:
            self._window.run_program()

    def _action_docs(self, *_):
        if self._window:
            self._window.show_docs()

    def _action_example(self, *_):
        if self._window:
            self._window.load_example()

    def _action_about(self, *_):
        if self._window:
            self._window.show_about()

    def do_activate(self):
        if self._window is None:
            self._window = VisuWindow(self)
        self._window.present()
