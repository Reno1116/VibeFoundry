"""单个任务气泡组件。"""
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor

from src.models.task import Task
from src.core.config import BUBBLE_RADIUS, MAX_TITLE_LENGTH


class BubbleWidget(QWidget):
    """单个待办气泡。

    左侧 4px 色条 + 任务标题 + 右侧计时区。
    点击气泡触发 `clicked` 回调。
    """

    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        self.task = task
        self._clicked_callback = None

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
            self.setStyleSheet(self._bubble_style(task.color_accent))
        else:
            self.setStyleSheet(self._bubble_style("#ffffff"))

        # 计时显示
        self._update_time_display()

    def _setup_ui(self) -> None:
        """构建气泡 UI 结构。"""
        self.setFixedHeight(72)
        self.setMinimumWidth(280)
        self.setMaximumWidth(320)
        self.setStyleSheet(self._bubble_style("#ffffff"))

        # 投影
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(8)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(shadow)

        # 主布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 12, 0)
        layout.setSpacing(12)

        # 左侧色条
        self._strip = QWidget()
        self._strip.setFixedWidth(4)
        self._strip.setFixedHeight(72)
        self._strip.setStyleSheet("background:#42A5F5; border-radius:4px;")
        layout.addWidget(self._strip)

        # 标题区域
        self._title_label = QLabel("")
        self._title_label.setStyleSheet(
            "font-size:13px; font-weight:500; color:#212121;"
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
            "font-size:11px; font-weight:500; color:#757575;"
        )
        time_layout.addWidget(self._time_value_label)

        self._time_hint_label = QLabel("")
        self._time_hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._time_hint_label.setStyleSheet(
            "font-size:10px; color:#9E9E9E;"
        )
        time_layout.addWidget(self._time_hint_label)

        layout.addWidget(time_container)

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
        return f"""
            BubbleWidget {{
                background: {bg_color};
                border-radius: {BUBBLE_RADIUS}px;
            }}
        """
