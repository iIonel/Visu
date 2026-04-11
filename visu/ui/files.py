from __future__ import annotations

import json
from pathlib import Path

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk


CONFIG_DIR = Path(GLib.get_user_config_dir()) / "visu"
STATE_FILE = CONFIG_DIR / "state.json"
FILE_EXTENSION = ".visu"
FILE_FILTER_NAME = "Visu pseudocode"


class SessionState:
    def __init__(self):
        self.last_file: Path | None = None
        self._read()

    def _read(self):
        if not STATE_FILE.is_file():
            return
        try:
            data = json.loads(STATE_FILE.read_text())
        except (OSError, json.JSONDecodeError):
            return
        raw = data.get("last_file")
        if not raw:
            return
        path = Path(raw)
        if path.is_file():
            self.last_file = path

    def write(self):
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            payload = {
                "last_file": str(self.last_file) if self.last_file else None,
            }
            STATE_FILE.write_text(json.dumps(payload, indent=2))
        except OSError:
            pass


def build_file_filter() -> Gtk.FileFilter:
    f = Gtk.FileFilter()
    f.set_name(FILE_FILTER_NAME)
    f.add_pattern("*.visu")
    f.add_pattern("*.txt")
    f.add_mime_type("text/plain")
    return f


def ensure_extension(path: Path) -> Path:
    if path.suffix == "":
        return path.with_suffix(FILE_EXTENSION)
    return path
