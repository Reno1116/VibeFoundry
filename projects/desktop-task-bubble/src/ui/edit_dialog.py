"""编辑待办弹窗（复用 AddTaskDialog，预填值）。"""
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import QDateTime

from src.models.task import Task
from src.ui.add_dialog import AddTaskDialog


class EditTaskDialog(AddTaskDialog):
    """编辑待办弹窗，继承 AddTaskDialog，预填当前任务数据。"""

    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        self._task_id = task.id
        self._prefill(task)

    def _prefill(self, task: Task) -> None:
        """预填任务数据到表单。"""
        # 标题
        self._title_input.setText(task.title)

        # 优先级
        radio_map = {
            "high": self._radio_high,
            "medium": self._radio_medium,
            "low": self._radio_low,
        }
        radio = radio_map.get(task.priority)
        if radio:
            radio.setChecked(True)

        # 预计耗时
        preset_minutes = [15, 30, 60, 120]
        if task.estimated_minutes in preset_minutes:
            idx = preset_minutes.index(task.estimated_minutes)
            self._time_chips[idx].setChecked(True)
            self._time_chips[idx].setStyleSheet(self._chip_style(True))
        else:
            # 自定义时长
            self._is_custom_selected = True
            self._custom_chip_btn.setChecked(True)
            self._custom_chip_btn.setStyleSheet(self._chip_style(True))
            if self._custom_input:
                self._custom_input.setText(str(task.estimated_minutes))
                self._custom_input.setVisible(True)

        # 截止时间
        if task.deadline:
            self._deadline_edit.setDateTime(QDateTime(task.deadline))

        # 启用确认按钮
        self._confirm_btn.setEnabled(True)
        self._confirm_btn.setStyleSheet(self._button_style(True))

    @property
    def task_id(self) -> str:
        return self._task_id
