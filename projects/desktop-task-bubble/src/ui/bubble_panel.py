"""桌面右侧气泡面板容器。"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QTimer
from PySide6.QtGui import QScreen

from src.models.task import Task, TaskStore
from src.ui.bubble_widget import BubbleWidget
from src.core.config import (
    DEFAULT_BUBBLE_WIDTH,
    BUBBLE_GAP,
    PANEL_PADDING,
)


class BubblePanel(QWidget):
    """右侧置顶透明容器，纵向排列待办气泡。

    作为无边框置顶窗口，位于屏幕右侧，不可抢焦点。
    """

    def __init__(self, store: TaskStore, parent=None):
        super().__init__(parent)
        self._store = store
        self._bubble_widgets: dict[str, BubbleWidget] = {}
        self._on_bubble_clicked = None

        self._setup_window()
        self._setup_ui()
        self._store.on_change(self.refresh)

    def set_on_bubble_clicked(self, callback) -> None:
        """设置气泡点击回调。callback(task, widget)。"""
        self._on_bubble_clicked = callback

    def refresh(self) -> None:
        """根据 TaskStore 数据重建气泡列表。"""
        tasks = self._store.pending_tasks

        # 清除不在列表中的气泡
        current_ids = {t.id for t in tasks}
        removed = [tid for tid in self._bubble_widgets if tid not in current_ids]
        for tid in removed:
            w = self._bubble_widgets.pop(tid)
            self._bubble_layout.removeWidget(w)
            w.deleteLater()

        # 添加或更新气泡
        for i, task in enumerate(tasks):
            if task.id in self._bubble_widgets:
                self._bubble_widgets[task.id].refresh(task)
            else:
                bubble = BubbleWidget(task, self._content_widget)
                bubble.set_on_clicked(self._on_bubble_clicked)
                self._bubble_widgets[task.id] = bubble
                self._bubble_layout.insertWidget(i, bubble)

        # 更新空状态
        self._update_empty_state()
        self._adjust_panel_size()

    # ── 窗口设置 ──

    def _setup_window(self) -> None:
        """配置无边框置顶透明窗口。"""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)  # 不抢焦点

        # 定位到主屏幕右侧
        self._position_on_screen()

    def _position_on_screen(self) -> None:
        """将面板定位到主屏幕右侧。"""
        screen = QScreen  # will be replaced with actual screen
        if hasattr(self, "screen"):
            screen = self.screen()
        if not screen:
            from PySide6.QtWidgets import QApplication
            app = QApplication.instance()
            if app:
                screen = app.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            panel_width = DEFAULT_BUBBLE_WIDTH + PANEL_PADDING * 2
            self.setGeometry(
                geo.right() - panel_width - PANEL_PADDING,
                geo.top() + PANEL_PADDING,
                panel_width,
                geo.height() - PANEL_PADDING * 2,
            )

    # ── 内部 UI ──

    def _setup_ui(self) -> None:
        """构建内部 UI 结构。"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(PANEL_PADDING, PANEL_PADDING, PANEL_PADDING, PANEL_PADDING)
        main_layout.setSpacing(0)

        # 内容区域（滚动）
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        self._content_widget = QWidget()
        self._content_widget.setStyleSheet("background: transparent;")
        self._bubble_layout = QVBoxLayout(self._content_widget)
        self._bubble_layout.setContentsMargins(0, 0, 0, 0)
        self._bubble_layout.setSpacing(BUBBLE_GAP)
        self._bubble_layout.addStretch()  # 底部弹簧，让气泡从上到下排列

        scroll.setWidget(self._content_widget)
        main_layout.addWidget(scroll)

        # 空状态提示
        self._empty_label = QLabel("暂无待办，按 Ctrl+Shift+N 添加")
        self._empty_label.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
        )
        self._empty_label.setStyleSheet(
            "font-size:13px; color:#757575; padding-top: 40px;"
            "background: transparent;"
        )
        self._empty_label.setVisible(False)
        main_layout.addWidget(self._empty_label)

    def _update_empty_state(self) -> None:
        """更新空状态显示。"""
        has_tasks = len(self._bubble_widgets) > 0
        self._empty_label.setVisible(not has_tasks)

    def _adjust_panel_size(self) -> None:
        """根据气泡数量调整面板高度。"""
        task_count = len(self._bubble_widgets)
        if task_count == 0:
            return

        # 计算需要的总高度
        bubble_height = 72
        total_height = task_count * bubble_height + (task_count - 1) * BUBBLE_GAP + PANEL_PADDING * 2

        # 限制最大高度为屏幕可用高度的 80%
        screen = self.screen()
        if screen:
            max_height = int(screen.availableGeometry().height() * 0.8)
            total_height = min(total_height, max_height)

        # 更新面板位置（保持右侧对齐）
        geo = self.geometry()
        screen_geo = screen.availableGeometry() if screen else geo
        panel_width = geo.width()
        self.setGeometry(
            screen_geo.right() - panel_width - PANEL_PADDING,
            screen_geo.top() + PANEL_PADDING,
            panel_width,
            total_height,
        )
