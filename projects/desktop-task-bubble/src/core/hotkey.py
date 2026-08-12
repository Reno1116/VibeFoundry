"""全局快捷键管理器。"""
from PySide6.QtCore import QObject, Signal

import keyboard

from src.core.config import DEFAULT_HOTKEY


class HotkeyManager(QObject):
    """注册和管理全局快捷键。

    使用 `keyboard` 库实现全局热键监听。
    热键触发时通过 Qt 信号 `triggered` 安全地通知主线程。
    """

    triggered = Signal()

    def __init__(self, hotkey: str = DEFAULT_HOTKEY, parent=None):
        super().__init__(parent)
        self._hotkey = hotkey
        self._running = False
        self._hook_id = None

    def start(self) -> None:
        """注册全局热键并开始监听。"""
        if self._running:
            return
        try:
            print(f"[Hotkey] 注册: {self._hotkey}")
            try:
                keyboard.remove_hotkey(self._hotkey)
            except Exception:
                pass
            self._hook_id = keyboard.add_hotkey(self._hotkey, self._fire)
            self._running = True
            print(f"[Hotkey] 注册成功: {self._hotkey}")
        except Exception as e:
            print(f"[Hotkey] 注册失败: {e}")

    def stop(self) -> None:
        """移除热键注册。"""
        if not self._running:
            return
        try:
            if self._hook_id is not None:
                keyboard.remove_hotkey(self._hook_id)
                self._hook_id = None
            self._running = False
        except Exception as e:
            print(f"[Hotkey] 移除失败: {e}")

    def update_hotkey(self, new_hotkey: str) -> None:
        """更换热键组合。"""
        was = self._running
        if was:
            self.stop()
        self._hotkey = new_hotkey
        if was:
            self.start()

    @property
    def current_hotkey(self) -> str:
        return self._hotkey

    def _fire(self) -> None:
        """键盘库回调（在独立线程中）→ 发送 Qt 信号到主线程。"""
        self.triggered.emit()
