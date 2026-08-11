"""倒计时引擎。"""
from PySide6.QtCore import QObject, QTimer as QtTimer, Signal

from src.models.task import Task


class TimerEngine(QObject):
    """管理单个任务的倒计时。

    信号:
        tick(task_id, elapsed) — 每秒触发
        time_reached(task_id) — 倒计时到时
    """

    tick = Signal(str, int)  # task_id, elapsed_seconds
    time_reached = Signal(str)  # task_id

    def __init__(self, store, parent=None):
        super().__init__(parent)
        self._store = store
        self._qt_timer = QtTimer(self)
        self._qt_timer.setInterval(1000)  # 1 秒
        self._qt_timer.timeout.connect(self._on_tick)

        self._active_task_id: str | None = None

    # ── 控制 API ──

    def start(self, task_id: str) -> None:
        """开始或继续计时。"""
        task = self._store.get(task_id)
        if task is None:
            return
        self._active_task_id = task_id
        self._store.update(task_id, status="counting")
        self._qt_timer.start()

    def pause(self, task_id: str) -> None:
        """暂停计时。"""
        if task_id == self._active_task_id:
            self._qt_timer.stop()
            self._store.update(task_id, status="paused")

    def resume(self, task_id: str) -> None:
        """继续计时（同 start）。"""
        self.start(task_id)

    def reset(self, task_id: str) -> None:
        """重置计时。"""
        if task_id == self._active_task_id:
            self._qt_timer.stop()
            self._active_task_id = None
        self._store.update(task_id, elapsed_seconds=0, status="pending")

    @property
    def is_running(self) -> bool:
        return self._qt_timer.isActive()

    @property
    def active_task_id(self) -> str | None:
        return self._active_task_id

    # ── 内部 ──

    def _on_tick(self) -> None:
        """每秒触发。"""
        if self._active_task_id is None:
            self._qt_timer.stop()
            return

        task = self._store.get(self._active_task_id)
        if task is None or task.status != "counting":
            self._qt_timer.stop()
            self._active_task_id = None
            return

        elapsed = task.elapsed_seconds + 1
        total = task.estimated_minutes * 60

        if elapsed >= total:
            # 到时
            self._qt_timer.stop()
            self._store.update(self._active_task_id, elapsed_seconds=total, status="paused")
            self.time_reached.emit(self._active_task_id)
            self._active_task_id = None
        else:
            self._store.update(self._active_task_id, elapsed_seconds=elapsed)
            self.tick.emit(self._active_task_id, elapsed)
