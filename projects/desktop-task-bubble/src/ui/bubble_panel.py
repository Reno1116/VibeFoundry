"""桌面右侧气泡面板容器。"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtCore import QRectF
import re

from src.models.task import Task, TaskStore
from src.ui.bubble_widget import BubbleWidget
from src.core.config import DEFAULT_BUBBLE_WIDTH, BUBBLE_GAP, PANEL_PADDING


def resolve_screen(screens, selected_name: str | None, primary_screen):
    """按稳定的 Qt 屏幕名称查找目标，不存在时回退主屏。"""
    if selected_name:
        for screen in screens:
            if screen.name() == selected_name:
                return screen
    return primary_screen


class BubblePanel(QWidget):
    """右侧置顶容器，纵向排列待办气泡。"""

    def __init__(self, store: TaskStore, screen_name: str | None = None,
                 panel_opacity: float = 1.0, bubble_opacity: float = 1.0,
                 parent=None):
        super().__init__(parent)
        self._store = store
        self._bubble_widgets: dict[str, BubbleWidget] = {}
        self._on_bubble_clicked = None
        self._screen_name = screen_name
        self._panel_opacity = self._clamp_opacity(panel_opacity)
        self._bubble_opacity = self._clamp_opacity(bubble_opacity)

        self._setup_window()
        self._setup_ui()
        self._store.on_change(self.refresh)

        # 延迟定位，等事件循环启动
        QTimer.singleShot(100, self._position_on_screen)

    def set_on_bubble_clicked(self, callback) -> None:
        self._on_bubble_clicked = callback

    def refresh(self) -> None:
        """根据 TaskStore 重建气泡列表。"""
        tasks = self._store.pending_tasks

        # 清除旧气泡
        current_ids = {t.id for t in tasks}
        removed = [tid for tid in self._bubble_widgets if tid not in current_ids]
        for tid in removed:
            w = self._bubble_widgets.pop(tid)
            self._bubble_layout.removeWidget(w)
            w.deleteLater()

        # 添加/更新气泡
        for i, task in enumerate(tasks):
            if task.id in self._bubble_widgets:
                self._bubble_widgets[task.id].refresh(task)
            else:
                bubble = BubbleWidget(task, opacity=self._bubble_opacity)
                bubble.set_on_clicked(self._on_bubble_clicked)
                self._bubble_widgets[task.id] = bubble
                self._bubble_layout.insertWidget(i, bubble)

        # 刷新空状态
        self._empty_label.setVisible(len(tasks) == 0)
        self._bubble_container.setVisible(len(tasks) > 0)
        self._apply_style()

    # ── 窗口设置 ──

    def _setup_window(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        # 顶层窗口必须允许 alpha 与桌面合成，否则 stylesheet 中的
        # 半透明背景会先与默认不透明画布合成，20% 和 100% 几乎无差别。
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setMinimumWidth(DEFAULT_BUBBLE_WIDTH + PANEL_PADDING * 2)
        self.setMinimumHeight(120)

    def _position_on_screen(self) -> None:
        """定位到用户选择的屏幕右侧。"""
        app = QApplication.instance()
        if not app:
            return
        screen = resolve_screen(app.screens(), self._screen_name, app.primaryScreen())
        if not screen:
            return
        geo = screen.availableGeometry()
        pw = DEFAULT_BUBBLE_WIDTH + PANEL_PADDING * 2
        x = geo.right() - pw - 8
        y = geo.top() + 8
        h = min(geo.height() - 16, 800)
        self.setGeometry(x, y, pw, h)
        print(
            f"[BubblePanel] 定位屏幕 {screen.name()}: "
            f"x={x}, y={y}, {pw}x{h}"
        )

    def set_screen(self, screen_name: str) -> None:
        """切换目标屏幕并立即重新定位。"""
        self._screen_name = screen_name
        self._position_on_screen()

    # ── UI ──

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(PANEL_PADDING, PANEL_PADDING, PANEL_PADDING, PANEL_PADDING)
        main_layout.setSpacing(BUBBLE_GAP)

        # 空状态
        self._empty_label = QLabel("暂无待办\n按 Ctrl+Shift+N 添加")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setMinimumHeight(80)
        self._empty_label.setStyleSheet(
            "font-size:13px; color:#555; background: transparent; padding:20px;"
        )
        main_layout.addWidget(self._empty_label)

        # 气泡容器
        from PySide6.QtWidgets import QFrame
        self._bubble_container = QFrame()
        self._bubble_container.setStyleSheet("background: transparent;")
        self._bubble_layout = QVBoxLayout(self._bubble_container)
        self._bubble_layout.setContentsMargins(0, 0, 0, 0)
        self._bubble_layout.setSpacing(BUBBLE_GAP)
        self._bubble_layout.addStretch()
        main_layout.addWidget(self._bubble_container, stretch=1)

        self._apply_style()

    @staticmethod
    def _clamp_opacity(value: float) -> float:
        return max(0.2, min(1.0, float(value)))

    @staticmethod
    def _qcolor_with_opacity(color_value: str, opacity: float) -> QColor:
        rgba_match = re.fullmatch(
            r"rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([\d.]+)\s*\)",
            color_value,
        )
        if rgba_match:
            red, green, blue = map(int, rgba_match.groups()[:3])
            alpha = float(rgba_match.group(4))
            color = QColor(red, green, blue)
            color.setAlphaF(max(0.0, min(1.0, alpha)))
        else:
            color = QColor(color_value)
        color.setAlphaF(max(0.0, min(1.0, color.alphaF() * opacity)))
        return color

    @staticmethod
    def _color_with_opacity(color_value: str, opacity: float) -> str:
        color = BubblePanel._qcolor_with_opacity(color_value, opacity)
        return f"rgba({color.red()},{color.green()},{color.blue()},{color.alpha()})"

    def set_panel_opacity(self, value: float) -> None:
        """只调整面板背景，不改变任务气泡。"""
        self._panel_opacity = self._clamp_opacity(value)
        self._apply_style()

    def set_bubble_opacity(self, value: float) -> None:
        """只调整任务气泡，不改变面板背景。"""
        self._bubble_opacity = self._clamp_opacity(value)
        for bubble in self._bubble_widgets.values():
            bubble.set_opacity(self._bubble_opacity)

    def set_always_on_top(self, enabled: bool) -> None:
        """切换置顶状态。"""
        flags = self.windowFlags()
        if enabled:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()

    def _apply_style(self) -> None:
        """更新独立的面板底板颜色。"""
        from src.core.theme import theme
        self._panel_background = self._qcolor_with_opacity(
            theme.color("dialog_bg"), self._panel_opacity
        )
        self._panel_border = self._qcolor_with_opacity(
            theme.color("border_subtle"), self._panel_opacity
        )
        text = theme.color("text_hint")
        self.setStyleSheet("BubblePanel { background: transparent; }")
        if not self._bubble_widgets:
            self._empty_label.setStyleSheet(
                f"font-size:13px; color:{text}; background: transparent; padding:20px;"
            )
        self.update()

    def paintEvent(self, event) -> None:
        """在透明顶层窗口上显式绘制带 alpha 的面板底板。"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(self._panel_background)
        painter.setPen(QPen(self._panel_border, 1))
        painter.drawRoundedRect(QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5), 12, 12)
        painter.end()
        super().paintEvent(event)
