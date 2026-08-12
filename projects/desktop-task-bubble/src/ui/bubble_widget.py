"""单个任务气泡组件。"""
from PySide6.QtWidgets import (
    QWidget, QLabel, QHBoxLayout, QVBoxLayout,
    QGraphicsOpacityEffect,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from src.models.task import Task
from src.core.config import MAX_TITLE_LENGTH


class BubbleWidget(QWidget):
    """单个待办气泡。

    左侧 4px 色条 + 任务标题 + 右侧计时区。
    点击气泡触发 `clicked` 回调。
    """

    def __init__(self, task: Task, opacity: float = 1.0, parent=None):
        super().__init__(parent)
        self.task = task
        self._clicked_callback = None
        self._opacity = max(0.2, min(1.0, opacity))

        self._setup_ui()
        self.refresh(task)

    def set_on_clicked(self, callback) -> None:
        """设置点击回调。"""
        self._clicked_callback = callback

    def refresh(self, task: Task) -> None:
        """根据 task 数据刷新气泡外观。"""
        self.task = task

        # 标题
        title = task.title
        if len(title) > MAX_TITLE_LENGTH:
            title = title[:MAX_TITLE_LENGTH] + "..."
        self._title_label.setText(title)

        # 颜色
        color = QColor(task.color_accent)
        self._strip.setStyleSheet(
            f"background:{color.name()}; border-radius:4px; min-width:4px;"
        )

        # 超时整卡变红
        if task.is_overtime:
            self._card.setStyleSheet(self._bubble_style(task.color_accent))
        else:
            self._card.setStyleSheet(self._bubble_style("#ffffff"))

        # 计时显示
        self._update_time_display()

    def _setup_ui(self) -> None:
        """构建气泡 UI 结构。"""
        self.setFixedHeight(72)
        self.setMinimumWidth(280)
        self.setMaximumWidth(320)
        self.setStyleSheet("background: transparent;")

        # 只使用一层离屏效果。Qt 在外层阴影 + 内层透明度的嵌套
        # QGraphicsEffect 下会重算缓存边界，导致调整透明度后左色条跳位。
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(self._opacity)
        self.setGraphicsEffect(self._opacity_effect)

        # 卡片放在稳定的外层点击区中。
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        self._card = QWidget()
        self._card.setStyleSheet(self._bubble_style("#ffffff"))
        outer_layout.addWidget(self._card)

        # 卡片主布局
        layout = QHBoxLayout(self._card)
        layout.setContentsMargins(0, 0, 12, 0)
        layout.setSpacing(12)

        # 左侧色条
        self._strip = QWidget()
        self._strip.setFixedWidth(4)
        self._strip.setFixedHeight(72)
        self._strip.setStyleSheet("background:#42A5F5; border-radius:4px;")
        layout.addWidget(self._strip)

        from src.core.theme import theme
        text_color = theme.color("text_primary")
        secondary = theme.color("text_secondary")
        hint = theme.color("text_hint")

        # 标题区域
        self._title_label = QLabel("")
        self._title_label.setStyleSheet(
            f"font-size:13px; font-weight:500; color:{text_color};"
        )
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self._title_label, stretch=1)

        # 右侧计时区
        time_container = QWidget()
        time_container.setFixedWidth(56)
        time_layout = QVBoxLayout(time_container)
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.setSpacing(2)
        time_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._time_value_label = QLabel("")
        self._time_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._time_value_label.setStyleSheet(
            f"font-size:11px; font-weight:500; color:{secondary};"
        )
        time_layout.addWidget(self._time_value_label)

        self._time_hint_label = QLabel("")
        self._time_hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._time_hint_label.setStyleSheet(
            f"font-size:10px; color:{hint};"
        )
        time_layout.addWidget(self._time_hint_label)

        layout.addWidget(time_container)

    def set_opacity(self, value: float) -> None:
        """设置气泡卡片整体透明度 0.2-1.0。"""
        self._opacity = max(0.2, min(1.0, value))
        self._opacity_effect.setOpacity(self._opacity)

    def _update_time_display(self) -> None:
        """更新计时显示区域。"""
        task = self.task
        total_secs = task.estimated_minutes * 60

        if task.status == "counting" or task.status == "paused":
            remaining = max(0, total_secs - task.elapsed_seconds)
            mins, secs = divmod(remaining, 60)
            self._time_value_label.setText(f"{mins:02d}:{secs:02d}")
            self._time_value_label.setStyleSheet(
                "font-size:11px; font-weight:500; color:#1976D2;"
            )
            self._time_hint_label.setText(f"总 {task.estimated_minutes}m")
        else:
            # 未开始计时
            if task.estimated_minutes < 60:
                self._time_value_label.setText(f"{task.estimated_minutes}m")
            else:
                h = task.estimated_minutes // 60
                m = task.estimated_minutes % 60
                self._time_value_label.setText(f"{h}h{m:02d}m" if m else f"{h}h")
            self._time_value_label.setStyleSheet(
                "font-size:11px; font-weight:500; color:#757575;"
            )
            self._time_hint_label.setText("待开始")

    def mousePressEvent(self, event) -> None:
        """点击气泡。"""
        if self._clicked_callback:
            self._clicked_callback(self.task, self)

    @staticmethod
    def _bubble_style(bg_color: str) -> str:
        from src.core.theme import theme
        return theme.bubble_css(bg_color)
