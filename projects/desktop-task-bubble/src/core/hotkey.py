"""全局快捷键管理器。"""
import threading
from typing import Callable

import keyboard

from src.core.config import DEFAULT_HOTKEY


class HotkeyManager:
    """注册和管理全局快捷键。

    使用 `keyboard` 库实现全局热键监听，在独立线程中运行。
    """

    def __init__(self, hotkey: str = DEFAULT_HOTKEY):
        self._hotkey = hotkey
        self._callback: Callable[[], None] | None = None
        self._running = False
        self._hook_id = None

    def set_callback(self, callback: Callable[[], None]) -> None:
        """设置热键触发时的回调函数。"""
        self._callback = callback

    def start(self) -> None:
        """注册全局热键并开始监听。"""
        if self._running:
            return
        try:
            self._hook_id = keyboard.add_hotkey(self._hotkey, self._handle_trigger)
            self._running = True
        except Exception as e:
            print(f"[Hotkey] 注册热键失败 ({self._hotkey}): {e}")

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
            print(f"[Hotkey] 移除热键失败: {e}")

    def update_hotkey(self, new_hotkey: str) -> None:
        """更换热键组合。"""
        was_running = self._running
        if was_running:
            self.stop()
        self._hotkey = new_hotkey
        if was_running:
            self.start()

    @property
    def current_hotkey(self) -> str:
        return self._hotkey

    def _handle_trigger(self) -> None:
        """热键触发时的内部处理（在 keyboard 线程中运行）。"""
        if self._callback:
            self._callback()
