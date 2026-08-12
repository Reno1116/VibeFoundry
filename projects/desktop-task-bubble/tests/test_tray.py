"""系统托盘菜单回归测试。"""
import gc
import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from src.ui.tray import SystemTray


class SystemTrayTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.tray = SystemTray()
        self.tray.build_menu()

    def tearDown(self):
        self.tray.hide()
        self.tray.deleteLater()
        self.app.processEvents()

    def test_menu_actions_survive_garbage_collection(self):
        gc.collect()
        self.app.processEvents()

        self.assertEqual(
            [action.text() for action in self.tray._menu.actions()],
            ["隐藏气泡", "", "历史记录", "设  置", "", "退  出"],
        )

    def test_actions_invoke_callbacks_once(self):
        calls = []
        self.tray.set_on_toggle_bubbles(lambda: calls.append("toggle"))
        self.tray.set_on_show_history(lambda: calls.append("history"))
        self.tray.set_on_show_settings(lambda: calls.append("settings"))
        self.tray.set_on_quit(lambda: calls.append("quit"))

        self.tray._toggle_action.trigger()
        self.tray._history_action.trigger()
        self.tray._settings_action.trigger()
        self.tray._quit_action.trigger()

        self.assertEqual(calls, ["toggle", "history", "settings", "quit"])

    def test_toggle_label_updates_stable_action(self):
        self.tray.update_toggle_label(False)
        self.assertEqual(self.tray._toggle_action.text(), "显示气泡")

        self.tray.update_toggle_label(True)
        self.assertEqual(self.tray._toggle_action.text(), "隐藏气泡")


if __name__ == "__main__":
    unittest.main()
