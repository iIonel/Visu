from __future__ import annotations

from pathlib import Path

import gi

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")
from gi.repository import Adw, Gio, GLib, Gtk

from .. import APP_ID, __version__
from ..docs import BUILTIN_EXAMPLES, DEFAULT_EXAMPLE, EXAMPLES_BY_KEY
from ..interpreter import Snapshot, run_source
from ..render.export import export_video
from .canvas_panel import CanvasPanel
from .docs_window import DocsWindow
from .editor_panel import EditorPanel
from .files import SessionState, build_file_filter, ensure_extension
from .style import install_css


class VisuWindow(Adw.ApplicationWindow):

    def __init__(self, app: Adw.Application):
        super().__init__(application=app)
        self.set_default_size(1240, 780)

        self._snapshots: list[Snapshot] = []
        self._current_index = 0
        self._session = SessionState()
        self._current_file: Path | None = None
        self._is_modified = False
        self._suppress_modified = False

        self._build_ui()
        self._wire_callbacks()
        self._load_initial_source()

    def _build_ui(self):
        install_css()
        self._dark_mode = True
        Adw.StyleManager.get_default().set_color_scheme(Adw.ColorScheme.PREFER_DARK)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(root)
        root.append(self._build_header())

        self.paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.paned.set_wide_handle(True)
        self.paned.set_vexpand(True)
        self.paned.set_position(700)
        root.append(self.paned)

        self.canvas_panel = CanvasPanel()
        self.editor_panel = EditorPanel()

        self.paned.set_start_child(self.canvas_panel)
        self.paned.set_resize_start_child(True)
        self.paned.set_shrink_start_child(False)

        self.paned.set_end_child(self.editor_panel)
        self.paned.set_resize_end_child(True)
        self.paned.set_shrink_end_child(False)

    def _build_header(self) -> Adw.HeaderBar:
        header = Adw.HeaderBar()
        header.add_css_class("flat")
        self._title_widget = Adw.WindowTitle(title="Visu", subtitle="algorithm visualizer")
        header.set_title_widget(self._title_widget)

        run_btn = Gtk.Button()
        run_btn.set_child(self._icon_text("media-playback-start-symbolic", "Run"))
        run_btn.add_css_class("suggested-action")
        run_btn.connect("clicked", lambda *_: self._run())
        header.pack_start(run_btn)

        reset_btn = Gtk.Button.new_from_icon_name("edit-clear-all-symbolic")
        reset_btn.set_tooltip_text("Reset visualization")
        reset_btn.connect("clicked", lambda *_: self._reset())
        header.pack_start(reset_btn)

        header.pack_end(self._build_menu_button())

        return header

    def _build_menu_button(self) -> Gtk.MenuButton:
        menu_btn = Gtk.MenuButton()
        menu_btn.set_icon_name("open-menu-symbolic")
        menu = Gio.Menu()

        file_section = Gio.Menu()
        file_section.append("Open…", "app.open")
        file_section.append("Save", "app.save")
        file_section.append("Save as…", "app.save_as")
        menu.append_section(None, file_section)

        session_section = Gio.Menu()
        session_section.append("Export as video…", "app.export_video")
        menu.append_section(None, session_section)

        examples_menu = Gio.Menu()
        for key, title, _src in BUILTIN_EXAMPLES:
            item = Gio.MenuItem.new(title, None)
            item.set_action_and_target_value("app.example", GLib.Variant("s", key))
            examples_menu.append_item(item)
        menu.append_submenu("Load example", examples_menu)

        view_section = Gio.Menu()
        view_section.append("Dark mode", "app.dark_mode")
        menu.append_section(None, view_section)

        help_section = Gio.Menu()
        help_section.append("Pseudocode reference", "app.docs")
        help_section.append("About Visu", "app.about")
        menu.append_section(None, help_section)

        menu_btn.set_menu_model(menu)
        return menu_btn

    @staticmethod
    def _icon_text(icon: str, label: str) -> Gtk.Widget:
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        box.append(Gtk.Image.new_from_icon_name(icon))
        box.append(Gtk.Label(label=label))
        return box

    def _wire_callbacks(self):
        self.canvas_panel.timeline.connect_change(self._on_timeline_change)
        self.editor_panel.buffer.connect("changed", self._on_buffer_changed)

    def _load_initial_source(self):
        if self._session.last_file is not None:
            try:
                content = self._session.last_file.read_text()
            except OSError:
                content = None
            if content is not None:
                self._apply_source(content, self._session.last_file)
                return
        self._apply_source(DEFAULT_EXAMPLE, None)

    def _apply_source(self, content: str, path: Path | None):
        self._suppress_modified = True
        self.editor_panel.set_source(content)
        self._suppress_modified = False
        self._current_file = path
        self._is_modified = False
        if path is not None:
            self._session.last_file = path
            self._session.write()
        self._update_title()

    def _on_buffer_changed(self, *_):
        if self._suppress_modified:
            return
        self.editor_panel.clear_line_highlight()
        if not self._is_modified:
            self._is_modified = True
            self._update_title()

    def _update_title(self):
        if self._current_file is None:
            title = "Visu"
        else:
            title = self._current_file.name
        if self._is_modified:
            title = f"• {title}"
        self.set_title(title)
        subtitle = str(self._current_file.parent) if self._current_file else "algorithm visualizer"
        self._title_widget.set_title(title)
        self._title_widget.set_subtitle(subtitle)

    def undo(self):
        buffer = self.editor_panel.buffer
        if buffer.get_can_undo():
            buffer.undo()

    def redo(self):
        buffer = self.editor_panel.buffer
        if buffer.get_can_redo():
            buffer.redo()

    def run_program(self):
        self._run()

    def _run(self):
        self.canvas_panel.timeline.pause()
        source = self.editor_panel.get_source()
        snapshots, error = run_source(source)
        self._snapshots = snapshots
        self.canvas_panel.timeline.set_snapshots(len(snapshots))

        if snapshots:
            self._show_snapshot(0)
        else:
            self.canvas_panel.canvas.reset()

        if error:
            existing = snapshots[-1].output if snapshots else ""
            self.editor_panel.set_output((existing + f"\nerror: {error}").strip())

    def _reset(self):
        self.canvas_panel.timeline.set_snapshots(0)
        self._snapshots = []
        self.canvas_panel.canvas.reset()
        self.editor_panel.set_output("")
        self.editor_panel.clear_line_highlight()

    def _on_timeline_change(self, index: int):
        self._show_snapshot(index)

    def _show_snapshot(self, index: int):
        if not self._snapshots:
            return
        index = max(0, min(len(self._snapshots) - 1, index))
        self._current_index = index
        snapshot = self._snapshots[index]
        self.canvas_panel.canvas.set_snapshot(snapshot)
        self.editor_panel.set_output(snapshot.output)
        self.editor_panel.highlight_line(snapshot.line)

    def open_file(self):
        dialog = Gtk.FileDialog.new()
        dialog.set_title("Open pseudocode")
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(build_file_filter())
        dialog.set_filters(filters)
        if self._current_file is not None:
            dialog.set_initial_folder(
                Gio.File.new_for_path(str(self._current_file.parent))
            )
        dialog.open(self, None, self._on_open_finished)

    def _on_open_finished(self, dialog, result):
        try:
            file = dialog.open_finish(result)
        except GLib.Error:
            return
        if file is None:
            return
        path = Path(file.get_path())
        try:
            content = path.read_text()
        except OSError as e:
            self._show_error(f"Could not open {path.name}: {e}")
            return
        self._apply_source(content, path)

    def save_file(self):
        if self._current_file is None:
            self.save_file_as()
            return
        self._write_to(self._current_file)

    def save_file_as(self):
        dialog = Gtk.FileDialog.new()
        dialog.set_title("Save pseudocode")
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(build_file_filter())
        dialog.set_filters(filters)
        if self._current_file is not None:
            dialog.set_initial_name(self._current_file.name)
            dialog.set_initial_folder(
                Gio.File.new_for_path(str(self._current_file.parent))
            )
        else:
            dialog.set_initial_name("untitled.visu")
        dialog.save(self, None, self._on_save_finished)

    def _on_save_finished(self, dialog, result):
        try:
            file = dialog.save_finish(result)
        except GLib.Error:
            return
        if file is None:
            return
        path = ensure_extension(Path(file.get_path()))
        self._write_to(path)

    def _write_to(self, path: Path):
        try:
            path.write_text(self.editor_panel.get_source())
        except OSError as e:
            self._show_error(f"Could not save {path.name}: {e}")
            return
        self._current_file = path
        self._is_modified = False
        self._session.last_file = path
        self._session.write()
        self._update_title()

    def _show_error(self, message: str):
        dialog = Adw.AlertDialog.new("Visu", message)
        dialog.add_response("ok", "OK")
        dialog.set_default_response("ok")
        dialog.present(self)

    def show_docs(self):
        DocsWindow(self).present()

    def load_example_by_key(self, key: str):
        source = EXAMPLES_BY_KEY.get(key)
        if source is None:
            return
        self._apply_source(source, None)

    def set_dark_mode(self, dark: bool):
        self._dark_mode = dark
        scheme = Adw.ColorScheme.PREFER_DARK if dark else Adw.ColorScheme.PREFER_LIGHT
        Adw.StyleManager.get_default().set_color_scheme(scheme)

    def export_video(self):
        if not self._snapshots:
            self._show_error("Run some pseudocode first — there are no snapshots to export.")
            return
        dialog = Gtk.FileDialog.new()
        dialog.set_title("Export animation as video")
        video_filter = Gtk.FileFilter()
        video_filter.set_name("MP4 video")
        video_filter.add_pattern("*.mp4")
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(video_filter)
        dialog.set_filters(filters)
        default_name = (
            f"{self._current_file.stem}.mp4" if self._current_file else "visu.mp4"
        )
        dialog.set_initial_name(default_name)
        dialog.save(self, None, self._on_export_video_finished)

    def _on_export_video_finished(self, dialog, result):
        try:
            file = dialog.save_finish(result)
        except GLib.Error:
            return
        if file is None:
            return
        path = Path(file.get_path())
        if path.suffix.lower() != ".mp4":
            path = path.with_suffix(".mp4")
        try:
            frames = export_video(self._snapshots, path)
        except Exception as e:
            self._show_error(f"Could not export video: {e}")
            return
        self.editor_panel.set_output(
            f"Exported {frames} frames → {path}"
        )

    def show_about(self):
        about = Adw.AboutWindow(
            transient_for=self,
            application_name="Visu",
            application_icon=APP_ID,
            version=__version__,
            developer_name="iIonel",
            comments="Interactive algorithm & data structure visualizer.",
            website="https://github.com/iionel/Visu",
            license_type=Gtk.License.MIT_X11,
        )
        about.present()
