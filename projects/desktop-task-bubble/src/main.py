"""桌面任务气泡 — 应用入口。"""
import sys
from PySide6.QtWidgets import QApplication

from src.models.task import Task, TaskStore
from src.core.hotkey import HotkeyManager
from src.core.timer import TimerEngine
from src.core.settings import AppSettings
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
        self.settings = AppSettings()
        self.tray = SystemTray()

        # 气泡面板
        self._bubble_panel = BubblePanel(
            self.store,
            screen_name=self.settings.screen_name,
            panel_opacity=self.settings.panel_opacity,
            bubble_opacity=self.settings.bubble_opacity,
        )
        self._bubble_panel.set_on_bubble_clicked(self._on_bubble_clicked)

        self._setup_connections()
        self._start()

    def _setup_connections(self) -> None:
        """连接托盘菜单和热键的回调。"""
        # 热键通过 Qt 信号连接（无需 QTimer 中转）
        self.hotkey.triggered.connect(self._show_add_dialog)

        self.tray.set_on_toggle_bubbles(self._on_toggle_bubbles)
        self.tray.set_on_show_history(self._on_show_history)
        self.tray.set_on_show_settings(self._on_show_settings)
        self.tray.set_on_quit(self._on_quit)

        # 计时到时通知
        self.timer.time_reached.connect(self._on_time_reached)

    def _start(self) -> None:
        """启动应用：显示托盘、注册热键、显示气泡面板。"""
        self.tray.show()
        self.tray.build_menu()  # show() 之后再构建菜单
        print("[App] 托盘图标已显示")
        self.hotkey.start()
        self._bubble_panel.show()
        panel_geo = self._bubble_panel.geometry()
        print(f"[App] 气泡面板已显示: x={panel_geo.x()}, y={panel_geo.y()}, w={panel_geo.width()}, h={panel_geo.height()}")
        print(f"[App] 已启动，按 {self.hotkey.current_hotkey} 添加待办")

    # ── 新增待办 ──

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

        def on_panel_opacity(value: float) -> None:
            self.settings.set_panel_opacity(value)
            self._bubble_panel.set_panel_opacity(value)

        def on_bubble_opacity(value: float) -> None:
            self.settings.set_bubble_opacity(value)
            self._bubble_panel.set_bubble_opacity(value)

        def on_pin(enabled: bool) -> None:
            if self._bubble_panel:
                self._bubble_panel.set_always_on_top(enabled)

        def on_screen(screen_name: str) -> None:
            self.settings.set_screen_name(screen_name)
            self._bubble_panel.set_screen(screen_name)

        panel = SettingsPanel(
            current_hotkey=self.hotkey.current_hotkey,
            panel_opacity=self.settings.panel_opacity,
            bubble_opacity=self.settings.bubble_opacity,
            selected_screen_name=self.settings.screen_name,
            on_hotkey_changed=on_hotkey,
            on_panel_opacity_changed=on_panel_opacity,
            on_bubble_opacity_changed=on_bubble_opacity,
            on_pin_changed=on_pin,
            on_screen_changed=on_screen,
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
