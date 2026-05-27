# Demo Tool

这是一个最小命令行示例，用来说明 `VibeFoundry` 如何把 brief 和 spec 落到代码。

## 运行方式

```powershell
python main.py --goal "整理一个可执行任务" --has-scope --has-constraints
```

## 示例输出

- 信息不足时输出 `brief`
- 目标、范围、约束齐全但还没有 spec 时输出 `spec`
- 已有 spec 时输出 `build`

## 关联文档

- `../../docs/briefs/sample-task/示例需求卡片.md`
- `../../docs/specs/sample-task/示例设计文档.md`
