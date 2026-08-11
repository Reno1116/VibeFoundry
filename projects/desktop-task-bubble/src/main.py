"""桌面任务气泡 — 应用入口。"""
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from src.models.task import Task, TaskStore
from src.core.hotkey import HotkeyManager
from src.core.timer import TimerEngine
from src.ui.tray import SystemTray
from src.ui.add_dialog import AddTaskDialog
from src.ui.edit_dialog import EditTaskDialog
from src.ui.context_menu import BubbleContextMenu
from src.ui.bubble_panel import BubblePanel
from src.ui.history_panel import HistoryPanel
from src.ui.settings_panel import SettingsPanel


class App:
    """应用主控制器，管理各组件的生命周期。"""

    def __init__(self):
        self.store = TaskStore()
        self.hotkey = HotkeyManager()
        self.timer = TimerEngine(self.store)
        self.tray = SystemTray()

        # 气泡面板
        self._bubble_panel = BubblePanel(self.store)
        self._bubble_panel.set_on_bubble_clicked(self._on_bubble_clicked)

        self._setup_connections()
        self._start()

    def _setup_connections(self) -> None:
        """连接托盘菜单和热键的回调。"""
        self.hotkey.set_callback(self._on_add_task)

        self.tray.set_on_toggle_bubbles(self._on_toggle_bubbles)
        self.tray.set_on_show_history(self._on_show_history)
        self.tray.set_on_show_settings(self._on_show_settings)
        self.tray.set_on_quit(self._on_quit)

        # 计时到时通知
        self.timer.time_reached.connect(self._on_time_reached)

    def _start(self) -> None:
        """启动应用：显示托盘、注册热键、显示气泡面板。"""
        self.tray.show()
        self.hotkey.start()
        self._bubble_panel.show()
        print(f"[App] 已启动，按 {self.hotkey.current_hotkey} 添加待办")

    # ── 新增待办 ──

    def _on_add_task(self) -> None:
        QTimer.singleShot(0, self._show_add_dialog)

    def _show_add_dialog(self) -> None:
        dialog = AddTaskDialog()
        if dialog.exec() == AddTaskDialog.DialogCode.Accepted:
            data = dialog.get_task_data()
            if data and data.get("title"):
                task = Task(
                    title=data["title"],
                    priority=data.get("priority", "medium"),
                    estimated_minutes=data.get("estimated_minutes", 30),
                    deadline=data.get("deadline"),
                )
                self.store.add(task)

    # ── 气泡交互 ──

    def _on_bubble_clicked(self, task: Task, widget) -> None:
        """气泡被点击：弹出操作菜单。"""
        menu = BubbleContextMenu(task)
        menu.start_timer.connect(lambda tid: self.timer.start(tid))
        menu.pause_timer.connect(lambda tid: self.timer.pause(tid))
        menu.resume_timer.connect(lambda tid: self.timer.resume(tid))
        menu.reset_timer.connect(lambda tid: self.timer.reset(tid))
        menu.edit_task.connect(self._on_edit_task)
        menu.complete_task.connect(self._on_complete_task)
        menu.delete_task.connect(self._on_delete_task)
        menu.exec(widget.mapToGlobal(widget.rect().center()))

    def _on_edit_task(self, task_id: str) -> None:
        task = self.store.get(task_id)
        if task is None:
            return
        dialog = EditTaskDialog(task)
        if dialog.exec() == EditTaskDialog.DialogCode.Accepted:
            data = dialog.get_task_data()
            if data:
                self.store.update(task_id, **data)

    def _on_complete_task(self, task_id: str) -> None:
        self.timer.reset(task_id)
        self.store.complete(task_id)

    def _on_delete_task(self, task_id: str) -> None:
        self.timer.reset(task_id)
        self.store.delete(task_id)

    # ── 计时 ──

    def _on_time_reached(self, task_id: str) -> None:
        """计时到时，弹出 Windows 通知。"""
        task = self.store.get(task_id)
        if task is None:
            return
        try:
            from plyer import notification
            notification.notify(
                title="⏰ 计时结束",
                message=f"「{task.title}」预计耗时已到",
                timeout=5,
            )
        except Exception:
            print(f"[App] 计时结束: {task.title}")

    # ── 托盘操作 ──

    def _on_toggle_bubbles(self) -> None:
        visible = not self._bubble_panel.isVisible()
        self._bubble_panel.setVisible(visible)
        self.tray.update_toggle_label(visible)

    def _on_show_history(self) -> None:
        panel = HistoryPanel(self.store)
        panel.exec()

    def _on_show_settings(self) -> None:
        def on_hotkey(new: str) -> None:
            self.hotkey.update_hotkey(new)

        panel = SettingsPanel(
            current_hotkey=self.hotkey.current_hotkey,
            on_hotkey_changed=on_hotkey,
        )
        panel.exec()

    def _on_quit(self) -> None:
        self.hotkey.stop()
        if self.timer.is_running:
            self.timer.pause(self.timer.active_task_id)
        QApplication.quit()


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    app_instance = App()
    app.setProperty("app_instance", app_instance)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
