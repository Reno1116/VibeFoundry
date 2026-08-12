"""历史记录面板。"""
from datetime import datetime

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QWidget,
)
from PySide6.QtCore import Qt

from src.models.task import Task, TaskStore
from src.core.config import DIALOG_RADIUS, BUTTON_RADIUS


class HistoryPanel(QDialog):
    """已完成任务历史面板。"""

    def __init__(self, store: TaskStore, parent=None):
        super().__init__(parent)
        self._store = store

        self._setup_ui()
        self._store.on_change(self._refresh)

    def _setup_ui(self) -> None:
        self.setWindowTitle("历史记录")
        self.setFixedSize(400, 500)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Dialog
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("HistoryPanel { background: transparent; }")

        from src.core.theme import theme

        container = QWidget()
        container.setObjectName("container")
        container.setStyleSheet(theme.dialog_css())

        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(12)

        # 标题栏
        header = QHBoxLayout()
        title = QLabel("已完成的任务")
        title.setStyleSheet(f"font-size:16px; font-weight:600; color:{theme.color('text_primary')};")
        header.addWidget(title)
        header.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet(
            "QPushButton {"
            f"  background: transparent; border: none; font-size: 14px; color: {theme.color('text_secondary')};"
            "}"
            " QPushButton:hover {"
            f"  color: {theme.color('text_primary')};"
            "}"
        )
        header.addWidget(close_btn)
        layout.addLayout(header)

        # 列表区
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self._list_widget = QWidget()
        self._list_widget.setStyleSheet("background: transparent;")
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(0)
        self._list_layout.addStretch()

        scroll.setWidget(self._list_widget)
        layout.addWidget(scroll, stretch=1)

        # 底部清空按钮
        footer = QHBoxLayout()
        footer.addStretch()
        clear_btn = QPushButton("清空历史")
        clear_btn.setFixedSize(100, 32)
        clear_btn.clicked.connect(self._on_clear)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: #d32f2f;
                border: 1px solid rgba(211,47,47,0.3);
                border-radius: {BUTTON_RADIUS}px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: rgba(211,47,47,0.05);
            }}
        """)
        footer.addWidget(clear_btn)
        layout.addLayout(footer)

        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(container)

        self._refresh()

    # ── 内部 ──

    def _refresh(self) -> None:
        """刷新历史列表。"""
        # 清除旧项
        while self._list_layout.count() > 1:  # 保留底部 stretch
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        from src.core.theme import theme as thm
        tasks = self._store.completed_tasks
        if not tasks:
            empty = QLabel("暂无已完成的任务")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet(f"font-size:13px; color:{thm.color('text_secondary')}; padding: 40px 0;")
            self._list_layout.insertWidget(0, empty)
            return

        groups: dict[str, list[Task]] = {}
        for t in tasks:
            date_key = t.created_at.strftime("%Y-%m-%d")
            groups.setdefault(date_key, []).append(t)

        for date_key, items in groups.items():
            today = datetime.now().strftime("%Y-%m-%d")
            if date_key == today:
                label_text = "今天"
            else:
                label_text = date_key

            date_label = QLabel(label_text)
            date_label.setStyleSheet(
                f"font-size:11px; font-weight:600; color:{thm.color('text_hint')};"
                "padding: 12px 0 4px 0;"
            )
            self._list_layout.insertWidget(self._list_layout.count() - 1, date_label)

            for task in items:
                item = self._build_history_item(task)
                self._list_layout.insertWidget(self._list_layout.count() - 1, item)

    def _build_history_item(self, task: Task) -> QWidget:
        """构建单个历史记录项。"""
        from src.core.theme import theme as thm
        border = thm.color('border_subtle')
        item = QWidget()
        item.setStyleSheet(f"""
            background: transparent;
            padding: 8px 0;
            border-bottom: 1px solid {border};
        """)

        layout = QHBoxLayout(item)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(8)

        dot = QWidget()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"background: {task.color_accent}; border-radius: 4px;")
        layout.addWidget(dot)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        title = QLabel(task.title)
        title.setStyleSheet(f"font-size:13px; font-weight:500; color:{thm.color('text_primary')};")
        text_layout.addWidget(title)

        time_str = task.created_at.strftime("%H:%M")
        detail = QLabel(
            f"预计 {task.estimated_minutes}m  ·  实际 {task.elapsed_seconds // 60}m  ·  {time_str}"
        )
        detail.setStyleSheet(f"font-size:11px; color:{thm.color('text_hint')};")
        text_layout.addWidget(detail)

        layout.addLayout(text_layout, stretch=1)
        return item

    def _on_clear(self) -> None:
        """清空所有历史记录。"""
        self._store.clear_completed()
