"""气泡操作菜单。"""
from PySide6.QtWidgets import QMenu, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtGui import QAction, QColor, QFont

from src.models.task import Task


class BubbleContextMenu(QMenu):
    """气泡的右键/点击操作菜单。

    根据任务状态动态显示菜单项：
    - pending:   开始计时 / 编辑 / 完成 / 删除
    - counting:  暂停计时 / 编辑 / 完成 / 删除
    - paused:    继续计时 / 重置计时 / 编辑 / 完成 / 删除
    """

    # 信号
    start_timer = Signal(str)   # task_id
    pause_timer = Signal(str)
    resume_timer = Signal(str)
    reset_timer = Signal(str)
    edit_task = Signal(str)
    complete_task = Signal(str)
    delete_task = Signal(str)

    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        self._task = task
        self._build()
        self._apply_style()

    def _build(self) -> None:
        status = self._task.status

        if status == "pending":
            self._add_action("▶  开始计时", lambda: self.start_timer.emit(self._task.id))
        elif status == "counting":
            self._add_action("⏸  暂停计时", lambda: self.pause_timer.emit(self._task.id))
        elif status == "paused":
            self._add_action("▶  继续计时", lambda: self.resume_timer.emit(self._task.id))
            self._add_action("↺  重置计时", lambda: self.reset_timer.emit(self._task.id))

        self._add_action("✎  编辑", lambda: self.edit_task.emit(self._task.id))
        self._add_action("✓  完成", lambda: self.complete_task.emit(self._task.id))

        self.addSeparator()

        delete_item = self._add_action("✕  删除", lambda: self.delete_task.emit(self._task.id))
        delete_item.setData("destructive")

    def _add_action(self, text: str, callback) -> QAction:
        action = QAction(text, self)
        action.triggered.connect(callback)
        self.addAction(action)
        return action

    def _apply_style(self) -> None:
        self.setStyleSheet("""
            QMenu {
                background: #ffffff;
                border-radius: 8px;
                padding: 4px;
                min-width: 160px;
            }
            QMenu::item {
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 13px;
                color: #212121;
            }
            QMenu::item:selected {
                background: rgba(0, 0, 0, 0.04);
            }
            QMenu::separator {
                height: 1px;
                background: rgba(0, 0, 0, 0.06);
                margin: 4px 8px;
            }
        """)
