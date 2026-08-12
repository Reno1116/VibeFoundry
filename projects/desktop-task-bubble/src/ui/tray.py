"""系统托盘图标与菜单。"""
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor, QFont
from PySide6.QtCore import QSize


def _create_default_icon() -> QIcon:
    pixmap = QPixmap(QSize(32, 32))
    pixmap.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor("#1976D2"))
    painter.setPen(QColor(0, 0, 0, 0))
    painter.drawEllipse(4, 4, 24, 24)
    painter.setPen(QColor(255, 255, 255))
    font = QFont("Segoe UI", 14, QFont.Weight.Bold)
    painter.setFont(font)
    painter.drawText(4, 4, 24, 24, 0x0084 | 0x0080, "✓")
    painter.end()
    return QIcon(pixmap)


class SystemTray(QSystemTrayIcon):
    """系统托盘图标，右键显示完整菜单。"""

    def __init__(self, parent=None):
        icon = _create_default_icon()
        super().__init__(icon, parent)
        self._bubbles_visible = True
        self._callbacks = {}
        self._menu = None
        self._toggle_action = None
        self._history_action = None
        self._settings_action = None
        self._quit_action = None

    def set_on_toggle_bubbles(self, callback):
        self._callbacks["toggle"] = callback

    def set_on_show_history(self, callback):
        self._callbacks["history"] = callback

    def set_on_show_settings(self, callback):
        self._callbacks["settings"] = callback

    def set_on_quit(self, callback):
        self._callbacks["quit"] = callback

    def update_toggle_label(self, visible: bool) -> None:
        self._bubbles_visible = visible
        if self._toggle_action is not None:
            self._toggle_action.setText("隐藏气泡" if visible else "显示气泡")

    def build_menu(self) -> None:
        """显式构建菜单（在 show() 之后调用）。"""
        self._menu = QMenu()

        # QAction 必须由长生命周期 QObject 持有。只将无 parent 的局部
        # QAction 传给 addAction() 不会转移所有权，函数返回后会被
        # Python 回收，导致 Windows 托盘菜单项消失。
        self._toggle_action = QAction(
            "隐藏气泡" if self._bubbles_visible else "显示气泡",
            self._menu,
        )
        self._toggle_action.triggered.connect(
            lambda: self._callbacks.get("toggle", lambda: None)()
        )
        self._menu.addAction(self._toggle_action)

        self._menu.addSeparator()

        self._history_action = QAction("历史记录", self._menu)
        self._history_action.triggered.connect(
            lambda: self._callbacks.get("history", lambda: None)()
        )
        self._menu.addAction(self._history_action)

        self._settings_action = QAction("设  置", self._menu)
        self._settings_action.triggered.connect(
            lambda: self._callbacks.get("settings", lambda: None)()
        )
        self._menu.addAction(self._settings_action)

        self._menu.addSeparator()

        self._quit_action = QAction("退  出", self._menu)
        self._quit_action.triggered.connect(
            lambda: self._callbacks.get("quit", lambda: None)()
        )
        self._menu.addAction(self._quit_action)

        self.setContextMenu(self._menu)
        print(f"[Tray] 菜单已构建: {[a.text() for a in self._menu.actions()]}")
