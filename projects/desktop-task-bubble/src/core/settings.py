"""应用设置的 JSON 持久化。"""
import json
from pathlib import Path

from src.core.config import SETTINGS_FILE


class AppSettings:
    """读写小型应用设置；文件缺失或损坏时使用安全默认值。"""

    def __init__(self, path: Path = SETTINGS_FILE):
        self._path = Path(path)
        self._data = {
            "screen_name": None,
            "panel_opacity": 1.0,
            "bubble_opacity": 1.0,
        }
        self._load()

    @property
    def screen_name(self) -> str | None:
        value = self._data.get("screen_name")
        return value if isinstance(value, str) and value else None

    def set_screen_name(self, screen_name: str) -> None:
        self._data["screen_name"] = screen_name
        self._save()

    @staticmethod
    def _opacity(value) -> float:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return 1.0
        return max(0.2, min(1.0, float(value)))

    @property
    def panel_opacity(self) -> float:
        return self._opacity(self._data.get("panel_opacity"))

    def set_panel_opacity(self, value: float) -> None:
        self._data["panel_opacity"] = self._opacity(value)
        self._save()

    @property
    def bubble_opacity(self) -> float:
        return self._opacity(self._data.get("bubble_opacity"))

    def set_bubble_opacity(self, value: float) -> None:
        self._data["bubble_opacity"] = self._opacity(value)
        self._save()

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            with self._path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            if isinstance(data, dict):
                self._data.update(data)
        except (OSError, json.JSONDecodeError):
            pass

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self._path.with_suffix(self._path.suffix + ".tmp")
        with temporary.open("w", encoding="utf-8") as file:
            json.dump(self._data, file, ensure_ascii=False, indent=2)
        temporary.replace(self._path)
