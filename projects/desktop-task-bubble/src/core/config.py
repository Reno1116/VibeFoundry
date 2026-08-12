"""应用配置常量与路径管理。"""
import os
from pathlib import Path

# 应用名称
APP_NAME = "desktop-task-bubble"

# 数据目录: %APPDATA%/desktop-task-bubble/
DATA_DIR = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) / APP_NAME
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 数据文件
TASKS_FILE = DATA_DIR / "tasks.json"
TASKS_BACKUP = DATA_DIR / "tasks.json.bak"
SETTINGS_FILE = DATA_DIR / "settings.json"

# 默认设置
DEFAULT_HOTKEY = "ctrl+shift+n"
DEFAULT_BUBBLE_WIDTH = 300
DEFAULT_BUBBLE_HEIGHT = 72
BUBBLE_GAP = 8  # 气泡之间的间距
PANEL_PADDING = 12  # 面板与屏幕边缘的间距

# 优先级颜色（色值参考 Figma spec）
PRIORITY_COLORS = {
    "high": {"normal": "#E53935", "deep": "#B71C1C"},
    "medium": {"normal": "#FB8C00", "deep": "#E65100"},
    "low": {"normal": "#43A047", "deep": "#1B5E20"},
    "no_deadline": "#42A5F5",
}

# 紧迫度判断阈值
URGENCY_OVERDUE = 0       # 已超时
URGENCY_NEAR_HOURS = 1    # 1 小时内为"临近"

# 预设耗时选项（分钟）
TIME_PRESETS = [15, 30, 60, 120]

# 标题最大字数
MAX_TITLE_LENGTH = 30

# 圆角
BUBBLE_RADIUS = 12
DIALOG_RADIUS = 12
MENU_RADIUS = 8
INPUT_RADIUS = 8
BUTTON_RADIUS = 8
