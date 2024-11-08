from __future__ import annotations

from app_model import Application
from qtpy import QtWidgets as QtW
from royalapp.widgets import MainWindow
from royalapp.qt._qmain_window import QMainWindow


class MainWindowQt(MainWindow[QtW.QWidget]):
    """Main window with Qt backend."""

    def __init__(self, app: Application) -> None:
        backend = QMainWindow(app=app)
        super().__init__(backend, app)
        backend._royalapp_main_window = self
        backend._tab_widget._init_startup()
