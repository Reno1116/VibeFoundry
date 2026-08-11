"""系统托盘图标与菜单。"""
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor, QFont
from PySide6.QtCore import QSize


def _create_default_icon() -> QIcon:
    """创建一个默认的圆形图标（任务图标简笔画）。"""
    pixmap = QPixmap(QSize(32, 32))
    pixmap.fill(QColor(0, 0, 0, 0))  # 透明背景

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 圆形背景
    painter.setBrush(QColor("#1976D2"))
    painter.setPen(QColor(0, 0, 0, 0))
    painter.drawEllipse(4, 4, 24, 24)

    # 勾号
    painter.setPen(QColor(255, 255, 255))
    font = QFont("Segoe UI", 14, QFont.Weight.Bold)
    painter.setFont(font)
    painter.drawText(4, 4, 24, 24, 0x0084 | 0x0080, "✓")  # AlignCenter | AlignVCenter

    painter.end()
    return QIcon(pixmap)


class SystemTray(QSystemTrayIcon):
    """系统托盘图标，右键菜单提供：显示/隐藏气泡、历史记录、设置、退出。"""

    def __init__(self, parent=None):
        icon = _create_default_icon()
        super().__init__(icon, parent)

        self._bubbles_visible = True
        self._build_menu()

    # ── 菜单回调（由 main.py 设置）──

    def set_on_toggle_bubbles(self, callback):
        self._on_toggle_bubbles = callback

    def set_on_show_history(self, callback):
        self._on_show_history = callback

    def set_on_show_settings(self, callback):
        self._on_show_settings = callback

    def set_on_quit(self, callback):
        self._on_quit = callback

    # ── 公开方法 ──

    def update_toggle_label(self, visible: bool) -> None:
        """更新显示/隐藏菜单项的文字。"""
        self._bubbles_visible = visible
        self._toggle_action.setText("隐藏气泡" if visible else "显示气泡")

    # ── 内部 ──

    def _build_menu(self) -> None:
        menu = QMenu()

        self._toggle_action = QAction("隐藏气泡")
        self._toggle_action.triggered.connect(self._handle_toggle)
        menu.addAction(self._toggle_action)

        menu.addSeparator()

        history_action = QAction("历史记录")
        history_action.triggered.connect(lambda: self._safe_call("_on_show_history"))
        menu.addAction(history_action)

        settings_action = QAction("设  置")
        settings_action.triggered.connect(lambda: self._safe_call("_on_show_settings"))
        menu.addAction(settings_action)

        menu.addSeparator()

        quit_action = QAction("退  出")
        quit_action.triggered.connect(lambda: self._safe_call("_on_quit"))
        menu.addAction(quit_action)

        self.setContextMenu(menu)

    def _handle_toggle(self) -> None:
        """切换气泡显示/隐藏。"""
        self._safe_call("_on_toggle_bubbles")

    def _safe_call(self, attr_name: str) -> None:
        """安全调用回调（如果已设置）。"""
        callback = getattr(self, attr_name, None)
        if callable(callback):
            callback()
