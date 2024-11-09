from pathlib import Path
from tempfile import TemporaryDirectory
from qtpy.QtWidgets import QApplication
from himena import MainWindow, anchor
from himena.types import WidgetDataModel
from himena.qt import register_frontend_widget, MainWindowQt
from himena.builtins.qt import widgets as _qtw

def test_new_window(ui: MainWindow):
    ui.show()
    assert len(ui.tabs) == 0
    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "test.txt"
        path.write_text("Hello, World!")
        ui.read_file(path)
    assert len(ui.tabs) == 1
    assert len(ui.tabs[0]) == 1
    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "test.txt"
        path.write_text("Hello, World! 2")
        ui.read_file(path)
    assert len(ui.tabs) == 1
    assert len(ui.tabs[0]) == 2
    ui.add_tab("New tab")
    assert len(ui.tabs) == 2
    assert len(ui.tabs.current()) == 0
    assert ui.tabs.current().title == "New tab"

def test_builtin_commands(ui: MainWindow):
    ui.show()
    ui.exec_action("new-tab")
    assert len(ui.tabs) == 1
    assert len(ui.tabs[0]) == 0
    ui.exec_action("builtins:console")
    ui.exec_action("builtins:filetree")
    ui.exec_action("builtins:output")
    ui.exec_action("builtins:new-text")
    assert len(ui.tabs[0]) == 1
    ui.exec_action("builtins:fetch-seaborn-test-data")
    ui.exec_action("quit")

def test_io_commands(ui: MainWindow, tmpdir, sample_dir: Path):
    response_open = lambda: [sample_dir / "text.txt"]
    response_save = lambda: Path(tmpdir) / "text_out.txt"
    ui._instructions = ui._instructions.updated(confirm=False)
    ui._instructions = ui._instructions.updated(file_dialog_response=response_open)
    ui.exec_action("open-file")
    ui.add_data("Hello", type="text")
    ui._instructions = ui._instructions.updated(file_dialog_response=response_save)
    ui.exec_action("save")
    ui.exec_action("save-as")

    # session
    response_session = lambda: Path(tmpdir) / "a.session.yaml"
    ui._instructions = ui._instructions.updated(file_dialog_response=response_session)
    ui.exec_action("save-session")
    ui.exec_action("load-session")

def test_builtin_commands_with_window(ui: MainWindowQt, sample_dir: Path):
    ui.exec_action("show-command-palette")
    ui.read_file(sample_dir / "text.txt")
    assert len(ui.tabs) == 1
    assert len(ui.tabs[0]) == 1
    ui._backend_main_window.setFocus()
    ui.exec_action("open-recent")
    ui._backend_main_window.setFocus()
    ui.exec_action("copy-screenshot")
    ui.exec_action("copy-screenshot-area")
    ui.exec_action("copy-screenshot-window")

    ui.exec_action("duplicate-window")
    ui.exec_action("duplicate-window")
    assert len(ui.tabs[0]) == 3
    ui.exec_action("rename-window")
    ui.exec_action("show-command-palette")

def test_custom_widget(ui: MainWindow):
    from qtpy.QtWidgets import QLabel

    ui.show()
    label = QLabel("Custom widget test")
    widget = ui.add_widget(label)
    assert len(ui.tabs) == 1
    assert len(ui.tabs[0]) == 1
    widget.title = "New title"
    assert widget.title == "New title"
    widget.rect = (10, 20, 100, 200)
    assert widget.rect == (10, 20, 100, 200)
    widget.anchor = "top-left"
    assert isinstance(widget.anchor, anchor.TopLeftConstAnchor)
    widget.anchor = "top-right"
    assert isinstance(widget.anchor, anchor.TopRightConstAnchor)
    widget.anchor = "bottom-left"
    assert isinstance(widget.anchor, anchor.BottomLeftConstAnchor)
    widget.anchor = "bottom-right"
    assert isinstance(widget.anchor, anchor.BottomRightConstAnchor)
    widget.state = "max"
    assert widget.state == "max"
    widget.state = "min"
    assert widget.state == "min"
    widget.state = "normal"
    assert widget.state == "normal"
    widget.state = "full"
    assert widget.state == "full"

def test_custom_dock_widget(ui: MainWindow):
    from qtpy.QtWidgets import QLabel

    ui.show()
    widget = QLabel("Dock widget test")
    dock = ui.add_dock_widget(widget)
    QApplication.processEvents()
    assert dock.visible
    dock.visible = False
    assert not dock.visible
    dock.title = "New title"
    assert dock.title == "New title"

def test_fallback_widget(ui: MainWindow):
    from himena.qt.registry._widgets import QFallbackWidget
    model = WidgetDataModel(value=object(), type="unsupported")
    win = ui.add_data_model(model)
    assert isinstance(win.widget, QFallbackWidget)

def test_register_frontend_widget(ui: MainWindow):
    from qtpy.QtWidgets import QLabel

    class QCustomTextView(QLabel):
        @classmethod
        def from_model(cls, model: WidgetDataModel):
            self = cls()
            self.setText(model.value)
            return self

    model = WidgetDataModel(value="abc", type="text.xyz")
    win = ui.add_data_model(model)
    assert type(win.widget) is _qtw.QDefaultTextEdit
    register_frontend_widget("text.xyz", QCustomTextView)

    win2 = ui.add_data_model(model)
    assert type(win2.widget) is QCustomTextView

def test_tile_window(ui: MainWindow):
    ui.add_data("A", type="text")
    ui.add_data("B", type="text")
    ui.tabs[0].tile_windows()
    ui.add_data("C", type="text")
    ui.tabs[0].tile_windows()
    ui.add_data("D", type="text")
    ui.tabs[0].tile_windows()
    ui.add_data("E", type="text")
    ui.tabs[0].tile_windows()
    ui.add_data("F", type="text")
    ui.tabs[0].tile_windows()
    ui.add_data("G", type="text")
    ui.tabs[0].tile_windows()
    ui.add_data("H", type="text")
    ui.tabs[0].tile_windows()
