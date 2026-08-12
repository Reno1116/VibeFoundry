# Figma 创建规格说明

> 本文档供 Figma 插件 Agent 读取，按规格逐一创建页面和组件。
> 工具名称：desktop-task-bubble

---

## 一、文件设置

- 文件名：`Desktop Task Bubble - Interaction`
- 页面结构：

| 页面名 | 内容 |
|--------|------|
| Components | 所有组件和变体定义 |
| Interaction Map | 总览交互流程图（所有 frame 拼接） |
| Add Task | 添加待办弹窗及变体 |
| Desktop Bubbles | 桌面气泡列表及各种状态 |
| Menus & Panels | 操作菜单、历史面板、设置面板 |

---

## 二、颜色系统（Color Styles）

创建以下 Color Styles，名称用 `/` 分隔分组：

| Style 名称 | 色值 | 用途 |
|------------|------|------|
| `priority/high` | `#E53935` | 高优先级气泡底色 |
| `priority/high-deep` | `#B71C1C` | 高优先级 + 已超时 |
| `priority/medium` | `#FB8C00` | 中优先级气泡底色 |
| `priority/medium-deep` | `#E65100` | 中优先级 + 临近截止 |
| `priority/low` | `#43A047` | 低优先级气泡底色 |
| `priority/low-deep` | `#1B5E20` | 低优先级 + 临近截止 |
| `priority/no-deadline` | `#42A5F5` | 无截止时间 |
| `surface/bubble-bg` | `#FFFFFF` (light) / `#2D2D2D` (dark) | 气泡卡片背景 |
| `surface/dialog-bg` | `#FFFFFF` (light) / `#1E1E1E` (dark) | 弹窗背景 |
| `surface/sidebar-bg` | `rgba(0,0,0,0.02)` (light) / `rgba(255,255,255,0.02)` (dark) | 侧边栏背景 |
| `text/primary` | `#212121` (light) / `#EEEEEE` (dark) | 主要文字 |
| `text/secondary` | `#757575` (light) / `#9E9E9E` (dark) | 次要文字 |
| `text/inverse` | `#FFFFFF` | 深色底上白色文字 |
| `border/subtle` | `rgba(0,0,0,0.08)` (light) / `rgba(255,255,255,0.08)` (dark) | 分割线 |

---

## 三、文字样式（Text Styles）

| Style 名称 | 字号 | 字重 | 用途 |
|------------|------|------|------|
| `heading/dialog` | 16px | SemiBold (600) | 弹窗标题 |
| `body/bubble-title` | 13px | Medium (500) | 气泡上的任务标题 |
| `body/menu-item` | 13px | Regular (400) | 菜单项 |
| `caption/time` | 11px | Regular (400) | 气泡上的倒计时数字 |
| `caption/hint` | 11px | Regular (400) | 输入框 placeholder、引导文字 |

---

## 四、组件：Add Task Dialog（添加待办弹窗）

### 主组件

宽 360px，高自适应（Auto Layout），圆角 12px，投影 `0 4px 24px rgba(0,0,0,0.15)`。

**从上到下：**

```
┌─────────────────────────────────┐
│  新增待办                    ✕  │  ← 标题栏，高 48px，下分割线
├─────────────────────────────────┤
│  ┌─────────────────────────┐    │
│  │ 输入任务标题...          │    │  ← 输入框，高 40px，圆角 8px，border 1px
│  └─────────────────────────┘    │     placeholder 灰色，focus 边框变蓝
│                                 │
│  优先级                         │
│  ○ 高  ○ 中  ● 低              │  ← Radio 按钮组，默认选中"中"
│                                 │
│  预计耗时                       │
│  [15m] [30m] [60m] [120m] 自定义│  ← 预设按钮 80px 宽，选中态用主题色填充
│  [___分钟___]                   │  ← 自定义输入，仅选"自定义"时显示
│                                 │
│  截止时间                       │
│  ┌─────────────────────────┐    │
│  │ 选择日期时间...     📅   │    │  ← DateTime picker，可选字段
│  └─────────────────────────┘    │     placeholder "不设置截止时间"
│                                 │
│  ┌─────────────────────────┐    │
│  │         确  认          │    │  ← 主按钮，高 44px，蓝色 #1976D2，白色字
│  └─────────────────────────┘    │     标题为空时按钮置灰不可点击
└─────────────────────────────────┘
```

### 变体（Component Variants）

创建 COMPONENT_SET，Property: `State`:

| 变体名 | 描述 |
|--------|------|
| `AddDialog / Default` | 所有字段为空，默认中优先级 |
| `AddDialog / Filled` | 已填写标题和耗时，确认按钮可点击 |
| `AddDialog / Error` | 标题为空时点确认 → 标题输入框边框变红 + 下方红色提示"标题不能为空" |

---

## 五、组件：Task Bubble（任务气泡）

### 主组件

宽 300px，高 72px，圆角 12px，外间距 bottom=8px，投影 `0 2px 8px rgba(0,0,0,0.08)`。

**内容布局（Auto Layout，水平 + 垂直嵌套）：**

```
┌────┬──────────────────────────┬──────┐
│    │  任务标题（最多 30 字）   │      │
│ 色 │  超长截断加省略号...      │ ⏱   │  ← 左侧色条 4px 宽
│ 条 │                          │ 计时 │  ← 右侧计时区 56px 宽
│    │  00:24:30               │ 按钮 │
│    │  已用时 / 总 60:00       │      │
└────┴──────────────────────────┴──────┘
```

**详细参数：**
- 左侧色条：宽 4px，高 100%（圆角左半边），颜色根据优先级和截止时间变化
- 标题区：padding 左右 12px，上下居中
- 标题文字：`body/bubble-title`，单行，超出省略号
- 时间显示区：右侧 56px 宽，垂直居中
  - 倒计时数字：`caption/time`，如 `23:59`
  - 下方小字：`caption/hint`，"总 60m"
- 计时按钮：计时区可点击

### 气泡颜色变体

创建 COMPONENT_SET，Property: `Priority × Deadline`:

| 变体名 | 左侧色条颜色 | 标题文字颜色 | 气泡底色 |
|--------|-------------|-------------|---------|
| `Bubble / High / Overdue` | `priority/high-deep` | `text/inverse` 白字 | `priority/high-deep` 整卡 |
| `Bubble / High / Near` | `priority/high` | `text/primary` | `surface/bubble-bg` |
| `Bubble / High / Far` | `priority/high` 50%opacity | `text/primary` | `surface/bubble-bg` |
| `Bubble / Medium / Near` | `priority/medium-deep` | `text/primary` | `surface/bubble-bg` |
| `Bubble / Medium / Far` | `priority/medium` 50%opacity | `text/primary` | `surface/bubble-bg` |
| `Bubble / Low / Near` | `priority/low-deep` | `text/primary` | `surface/bubble-bg` |
| `Bubble / Low / Far` | `priority/low` 50%opacity | `text/primary` | `surface/bubble-bg` |
| `Bubble / No Deadline` | `priority/no-deadline` | `text/primary` | `surface/bubble-bg` |

> 说明：Near = 截止时间在 1 小时内，Far = 1 小时以上，Overdue = 已超时

### 气泡交互状态变体

每种颜色变体下再分状态：

| 状态 | 描述 |
|------|------|
| `Idle` | 默认状态 |
| `Counting` | 倒计时进行中，时间数字每秒刷新 |
| `Paused` | 计时暂停，时间数字闪烁 |
| `Overtime` | 已超时（仅对有截止时间的），整个气泡深红色 + 闪烁动画 |
| `Completed` | 半透明 0.5 + 文字删除线，0.3s 后淡出消失 |

---

## 六、组件：Context Menu（右键/点击菜单）

宽 160px，圆角 8px，投影 `0 4px 12px rgba(0,0,0,0.12)`，padding 4px。

```
┌──────────────────┐
│  ▶ 开始计时       │  ← hover 背景 rgba(0,0,0,0.06)
│  ✎ 编辑          │
│  ✓ 完成          │
│  ──────────      │  ← 分割线
│  ✕ 删除          │  ← 红色文字
└──────────────────┘
```

每项高 36px，左图标 + 右文字，padding 左右 12px。

变体（计时中/非计时中）：

| 变体 | 菜单项 |
|------|--------|
| `Menu / Idle` | 开始计时 / 编辑 / 完成 / 分割线 / 删除 |
| `Menu / Counting` | 暂停计时 / 编辑 / 完成 / 分割线 / 删除 |
| `Menu / Paused` | 继续计时 / 重置计时 / 编辑 / 完成 / 分割线 / 删除 |

---

## 七、其他组件

### 7.1 系统托盘菜单

宽 180px，样式同 Context Menu。

```
┌──────────────────┐
│  显示/隐藏气泡     │
│  ──────────      │
│  历史记录         │
│  设  置          │
│  ──────────      │
│  退  出          │
└──────────────────┘
```

### 7.2 历史记录面板

宽 400px，高 500px，标题"已完成的任务"。

```
┌─────────────────────────────────┐
│  已完成的任务               ✕   │
├─────────────────────────────────┤
│  今天                          │
│  ┌─────────────────────────┐   │
│  │ ● 完成项目文档   14:30  │   │  ← 左色点 + 标题 + 完成时间
│  │   预计 60m  实际 45m    │   │  ← 预计/实际耗时对比
│  └─────────────────────────┘   │
│  昨天                          │
│  ┌─────────────────────────┐   │
│  │ ● 修复登录页 Bug  09:15 │   │
│  │   预计 30m  实际 22m    │   │
│  └─────────────────────────┘   │
│  ...                           │
│                          ┌───┐ │
│                         │清空 │ │ ← 底部清空按钮
│                         └───┘ │
└─────────────────────────────────┘
```

### 7.3 设置面板

宽 400px，Auto Layout，间距 16px。

```
┌─────────────────────────────────┐
│  设  置                    ✕   │
├─────────────────────────────────┤
│  快捷键                        │
│  添加待办：[Ctrl+Shift+N    ]  │  ← 可聚焦输入框，按键捕获
│                                 │
│  显示器                        │
│  ○ 主显示器                     │
│  ○ 显示器 2                    │  ← 自动检测可用显示器
│  ○ 显示器 3                    │
│                                 │
│  面板透明度                    │
│  ─────────●────────  100%      │  ← 20%–100%，仅面板/空状态底板，实时预览
│                                 │
│  气泡透明度                    │
│  ─────────●────────  100%      │  ← 20%–100%，仅任务气泡，实时预览
│                                 │
│  气泡大小                      │
│  ○ 小(280px)  ○ 中(320px) ● 大(360px) │
│                                 │
│  数据                          │
│  存储路径：%APPDATA%/...       │
│  [导出数据] [导入数据]          │
│  [重置所有数据]  ← 红色警告按钮  │
└─────────────────────────────────┘
```

两项透明度独立保存，重启后恢复；调整其中一项不得改变另一项。

---

## 八、Interaction Map 页面布局

在 Interaction Map 页面创建一个 Frame：宽 6000px，高 1200px，背景 `#F5F5F5`。

从左到右排列以下内容，用箭头连接表示流程：

```
┌────────┐    ┌────────┐    ┌──────────────┐    ┌──────────┐
│ 桌面   │───▶│ 快捷键 │───▶│  Add Task    │───▶│ 气泡列表 │
│ 托盘   │    │ 呼出   │    │  Dialog      │    │ 置顶显示 │
│ 图标   │    └────────┘    └──────────────┘    └──────────┘
└────────┘                                           │
     │  ▲                                            ▼
     │  │                                    ┌──────────────┐
     ▼  │                                    │ 气泡操作     │
┌────────────┐                               │ 计时/编辑/   │
│ 托盘菜单   │                               │ 完成/删除    │
│ 隐藏/历史/ │                               └──────────────┘
│ 设置/退出  │                                      │
└────────────┘                               ┌──────┬──────┬──────┐
                                             ▼      ▼      ▼      ▼
                                         ┌────┐ ┌────┐ ┌────┐ ┌────┐
                                         │完成│ │编辑│ │删除│ │计时│
                                         │归档│ │弹窗│ │移除│ │通知│
                                         └────┘ └────┘ └────┘ └────┘
```

在 frame 下方用 4 个区域展示异常状态：

| 状态区域 | 内容 |
|----------|------|
| 空状态 | 无待办时的侧边栏，显示引导文字 |
| 超时状态 | 一个深红色的 bubble，标题"提交周报 (已超时 2 小时)" |
| 计时结束状态 | 一个闪烁的 bubble + Windows 通知 toast |
| 错误状态 | 数据加载失败时的提示 + 空列表 |

---

## 九、创建顺序

Agent 请按以下顺序操作：

1. 创建颜色 Styles（第二节全部）
2. 创建文字 Styles（第三节全部）
3. 在 Components 页面创建 Add Task Dialog 组件及变体
4. 在 Components 页面创建 Task Bubble 组件及所有颜色 × 状态变体
5. 在 Components 页面创建 Context Menu 组件及变体
6. 在 Components 页面创建托盘菜单、历史面板、设置面板
7. 在 Desktop Bubbles 页面拼装气泡列表（各种数量、颜色组合）
8. 在 Add Task 页面放置弹窗的各种状态
9. 在 Menus & Panels 页面放置各面板
10. 在 Interaction Map 页面创建总览帧

---

## 十、注意事项

- 所有组件使用 Auto Layout，方便调整
- Dialog 和 Panel 使用投影，Bubble 使用轻投影
- 颜色变量必须用 Color Styles 引用，不要直接写色值
- 圆角统一：气泡 12px，弹窗 12px，菜单 8px，输入框 8px，按钮 8px
- 间距体系：4px (tight), 8px (default), 12px (relaxed), 16px (section gap), 24px (page padding)
- 图标使用简单的几何形状或 Figma 内置 icon，不需要引入图标库
