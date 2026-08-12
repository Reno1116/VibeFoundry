# desktop-task-bubble

桌面常驻待办气泡工具 — 随时输入待办，气泡置顶显示，按优先级和截止时间变色，支持倒计时追踪。

## 启动方式

```bash
cd projects/desktop-task-bubble
pip install -r requirements.txt
python -m src.main
```

- 启动后托盘出现蓝色图标
- 按 `Ctrl+Shift+N` 添加待办
- 气泡自动出现在桌面右侧
- 右键托盘图标可隐藏/显示气泡、查看历史、修改设置

## 当前能力（v1.0）

- 全局快捷键 `Ctrl+Shift+N` 快速添加待办
- 三级优先级（高红 / 中橙 / 低绿）+ 截止时间颜色深浅
- 无截止时间的任务显示蓝色
- 预设耗时按钮（15m / 30m / 60m / 120m）+ 手动输入
- 手动开始/暂停/继续/重置倒计时
- 计时结束时 Windows 原生通知
- 桌面右侧无边框置顶气泡面板，不抢焦点
- 气泡自动按截止时间 + 优先级排序
- 点击气泡弹出操作菜单（计时 / 编辑 / 完成 / 删除）
- 编辑可修改全部字段
- 完成任务归档到历史记录面板
- 本地 JSON 文件持久化，重启不丢失
- 系统托盘常驻，右键切换显示/隐藏
- 跟随 Windows 深浅色主题
- 多显示器支持
- 面板透明度与气泡透明度可独立调节并自动保存

## 已知问题

- 托盘右键菜单在 Windows 上偶现不完整，仅显示"隐藏/显示气泡"一项。根因是 PySide6 `QSystemTrayIcon.setContextMenu()` 与 Windows 存在兼容性问题。下个版本可考虑用 `pystray` 替代 Qt 托盘
- 快捷键修改目前仅支持 Ctrl/Shift/Alt 组合键
- `keyboard` 库在某些安全软件下可能需要管理员权限

## 技术栈

- Python 3.12+
- PySide6 6.7+（Qt 绑定）
- keyboard（全局热键）
- darkdetect（系统主题检测）
- plyer（Windows 通知）

## 数据存储

所有数据保存在 `%APPDATA%/desktop-task-bubble/tasks.json`，自动备份到 `.bak`。
显示器选择保存在 `%APPDATA%/desktop-task-bubble/settings.json`。
