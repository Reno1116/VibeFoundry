"""Task 数据模型与 TaskStore 持久化层。"""
import json
import uuid
import shutil
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Callable, Optional

from src.core.config import (
    TASKS_FILE,
    TASKS_BACKUP,
    PRIORITY_COLORS,
    URGENCY_OVERDUE,
    URGENCY_NEAR_HOURS,
)


@dataclass
class Task:
    """单个待办任务的数据模型。"""

    title: str
    priority: str = "medium"  # "high" | "medium" | "low"
    estimated_minutes: int = 30
    deadline: Optional[datetime] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"  # "pending" | "counting" | "paused" | "completed"
    elapsed_seconds: int = 0  # 已计时秒数

    # ── 计算属性 ──

    @property
    def urgency(self) -> str:
        """返回紧迫度: "overdue" | "near" | "far" | "no-deadline"."""
        if self.deadline is None:
            return "no-deadline"
        now = datetime.now()
        if now >= self.deadline:
            return "overdue"
        remaining = self.deadline - now
        if remaining <= timedelta(hours=URGENCY_NEAR_HOURS):
            return "near"
        return "far"

    @property
    def sort_key(self) -> tuple:
        """排序关键字: (有无截止时间, 紧迫度权重, 优先级权重, 创建时间)。

        排序结果:
        1. 有截止时间在前, 无截止时间在后
        2. 截止时间越近越靠前
        3. 同紧迫度内: 高 > 中 > 低
        4. 无截止时间的按优先级排
        """
        urgency_order = {"overdue": 0, "near": 1, "far": 2, "no-deadline": 3}
        priority_order = {"high": 0, "medium": 1, "low": 2}

        if self.deadline:
            # 有截止时间: 按截止时间 + 优先级
            return (0, self.deadline, priority_order.get(self.priority, 1))
        else:
            # 无截止时间: 排最后, 内部按优先级
            return (1, datetime.max, priority_order.get(self.priority, 1))

    @property
    def color_accent(self) -> str:
        """返回左侧色条颜色（HEX）。"""
        if self.deadline is None:
            return PRIORITY_COLORS["no_deadline"]

        urgency = self.urgency
        if urgency == "overdue":
            return PRIORITY_COLORS["high"]["deep"]
        if urgency == "near":
            return PRIORITY_COLORS[self.priority]["deep"]
        return PRIORITY_COLORS[self.priority]["normal"]

    @property
    def is_overtime(self) -> bool:
        """已超时（深红色整卡）。"""
        return self.urgency == "overdue"

    # ── 序列化 ──

    def to_dict(self) -> dict:
        d = asdict(self)
        d["deadline"] = self.deadline.isoformat() if self.deadline else None
        d["created_at"] = self.created_at.isoformat()
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Task":
        d = d.copy()
        d["deadline"] = datetime.fromisoformat(d["deadline"]) if d.get("deadline") else None
        d["created_at"] = datetime.fromisoformat(d["created_at"])
        return cls(**d)


class TaskStore:
    """任务存储管理器，负责 CRUD 和 JSON 文件持久化。

    通过 `on_change(callback)` 注册监听，数据变更时自动调用所有回调。
    UI 层可以用此机制刷新显示。
    """

    def __init__(self):
        self._tasks: list[Task] = []
        self._listeners: list[Callable[[], None]] = []
        self._load()

    def on_change(self, callback: Callable[[], None]) -> None:
        """注册数据变更回调。"""
        self._listeners.append(callback)

    def _notify(self) -> None:
        """通知所有监听器。"""
        for cb in self._listeners:
            try:
                cb()
            except Exception:
                pass

    # ── 属性 ──

    @property
    def pending_tasks(self) -> list[Task]:
        """返回未完成的任务，按 sort_key 排序。"""
        return sorted(
            [t for t in self._tasks if t.status != "completed"],
            key=lambda t: t.sort_key,
        )

    @property
    def completed_tasks(self) -> list[Task]:
        """返回已完成的任务，按完成时间倒序。"""
        return sorted(
            [t for t in self._tasks if t.status == "completed"],
            key=lambda t: t.created_at,
            reverse=True,
        )

    @property
    def all_tasks(self) -> list[Task]:
        return list(self._tasks)

    # ── CRUD ──

    def add(self, task: Task) -> None:
        """添加任务并保存。"""
        self._tasks.append(task)
        self._save()
        self._notify()

    def update(self, task_id: str, **kwargs) -> Optional[Task]:
        """更新任务字段并保存。返回更新后的 Task，找不到则返回 None。"""
        task = self.get(task_id)
        if task is None:
            return None
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        self._save()
        self._notify()
        return task

    def delete(self, task_id: str) -> bool:
        """删除任务并保存。返回是否成功。"""
        task = self.get(task_id)
        if task is None:
            return False
        self._tasks.remove(task)
        self._save()
        self._notify()
        return True

    def get(self, task_id: str) -> Optional[Task]:
        """按 ID 查找任务。"""
        for t in self._tasks:
            if t.id == task_id:
                return t
        return None

    def complete(self, task_id: str) -> Optional[Task]:
        """标记任务为已完成。"""
        return self.update(task_id, status="completed")

    def clear_completed(self) -> int:
        """清除所有已完成任务。返回清除数量。"""
        count = len([t for t in self._tasks if t.status == "completed"])
        self._tasks = [t for t in self._tasks if t.status != "completed"]
        self._save()
        self._notify()
        return count

    # ── 持久化 ──

    def _save(self) -> None:
        """保存到 JSON 文件。先写备份再写正式文件。"""
        try:
            # 备份旧文件
            if TASKS_FILE.exists():
                shutil.copy2(TASKS_FILE, TASKS_BACKUP)
        except OSError:
            pass  # 备份失败不影响主写入

        data = [t.to_dict() for t in self._tasks]
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load(self) -> None:
        """从 JSON 文件加载任务列表。"""
        if not TASKS_FILE.exists():
            self._tasks = []
            return

        try:
            with open(TASKS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._tasks = [Task.from_dict(d) for d in data]
        except (json.JSONDecodeError, KeyError, TypeError):
            # 文件损坏 → 尝试从备份恢复
            if TASKS_BACKUP.exists():
                try:
                    with open(TASKS_BACKUP, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    self._tasks = [Task.from_dict(d) for d in data]
                    # 恢复正式文件
                    self._save()
                except (json.JSONDecodeError, KeyError, TypeError):
                    self._tasks = []
            else:
                self._tasks = []
