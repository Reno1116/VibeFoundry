# VibeFoundry AI Kit

`ai-kit/` 是本仓库的 AI 协作主入口。

规则说明看 `../docs/workflow-v1.md`，日常执行先看 `../docs/daily-manual.md`。

它只负责四件事：

- 说明新任务默认从 `brief` 开始
- 说明什么时候进入 `spec`，什么时候才开始 `build`
- 说明 build 完成后必须补 `validate`
- 强制提醒读取中文文件时先按 `UTF-8` 解码

## 首要规则

在读取任何中文文档前，先执行这条规则：

```text
请按 UTF-8 读取所有中文文档，再开始分析。
```

如果没有先确认编码，不要直接引用或改写中文文件内容。

## 默认分流

### 进入 `brief`

适用于以下情况：

- 问题还没说清楚
- 目标、范围、约束、成功标准还不完整
- 只是一个想法，还没变成可执行任务

对应模板：

- `../docs/templates/需求卡片模板.md`

### 进入 `spec`

适用于以下情况：

- 已经有明确目标
- 已经有明确范围
- 已经有明确约束
- 已经有明确成功标准

对应模板：

- `../docs/templates/设计文档模板.md`

### 进入 `build`

只有在 `brief` 和 `spec` 足够清晰时才进入实现。

进入 `build` 前必须确认：

- `spec` 已写清输入输出
- `spec` 已写清边界与失败场景
- `spec` 已写清验证方式
- 已完成一次人工确认

如果用户直接要求写代码，但任务定义仍缺关键条件，先补最小 brief，再继续。

### 进入 `validate`

只要本轮实现结束，就补一份最小验收记录。

最低要求：

- 说明结果是否符合目标
- 说明怎么验证的
- 说明还有哪些缺口

## 文件使用顺序

1. 先读 `ai-kit/README.md`
2. 判断当前信息是否足够进入 `spec`
3. 信息不足则读 `../docs/templates/需求卡片模板.md`
4. 信息充分则读 `../docs/templates/设计文档模板.md`
5. 进入实现前做一次人工确认
6. 需要收口结果时读 `../docs/templates/验收模板.md`

## 文件说明

- `quick_start_prompt.md`
  新对话可直接复制的启动提示词。
- `conversation_starter.md`
  用来快速采集目标、范围、约束和成功标准。
- `task_templates.md`
  常见任务触发语。
- `response_template.md`
  AI 默认输出结构建议。
- `system_prompt.md`
  长期协作时可复用的角色与行为约定。
