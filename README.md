# VibeFoundry

*A vibe-coding workspace for turning ideas into specs and working software.*

`VibeFoundry` 是一个面向单人 + AI 协作的精选主仓，用来把想法逐步推进成需求、设计和可运行程序。

## 仓库定位

- 覆盖完整链路：`idea -> brief -> spec -> build -> validate`
- 同时承载文档与代码，不强绑单一技术栈
- 只收纳值得持续推进的项目，临时想法不直接进入正式项目目录

## UTF-8 约束

所有中文文档与模板统一按 `UTF-8` 保存和读取。

- 适用范围：`md`、`txt`、`json`、`yml`、`yaml`
- AI 或脚本首次读取中文文件时，必须优先按 `UTF-8` 解码
- 不依赖系统默认编码推断，避免 PowerShell / IDE 首次读取乱码
- 推荐 Git 全局配置使用 `core.autocrlf=false` 与 `core.eol=lf`
- 中文文档与代码默认统一使用 `LF`

如果你在新对话里要让 AI 读取本仓库文件，建议明确写上：

```text
请按 UTF-8 读取所有中文文档，再开始分析。
```

## 目录结构

- `ai-kit/`
  AI 协作入口、启动提示词、任务模板和输出约定。
- `docs/briefs/`
  需求卡片。每个任务默认从这里开始。
- `docs/specs/`
  设计文档。brief 信息充分后进入这里。
- `docs/validate/`
  验收记录、测试结果、缺口与后续事项。
- `docs/templates/`
  需求卡片、设计文档、验收模板。
- `docs/archive/`
  暂停、失败、冻结或仅做保留的历史内容。
- `projects/`
  实际程序项目。每个项目子目录独立维护 README、启动方式和依赖说明，并且只在正式进入 `build` 时创建。

## 默认工作流

1. 每个新任务先写 `brief`
2. 只有 `目标 / 范围 / 约束 / 成功标准` 四要素齐全，才进入 `spec`
3. `spec` 默认写到“可直接开干”，至少说明输入输出、边界和验证方式
4. 进入 `build` 前，再做一次人工确认
5. `build` 默认先做最小可运行版本
6. build 完成后补 `validate`
7. 可继续迭代的任务保留在活跃区；暂停、冻结、废弃的任务移入 `archive`

没有需求卡片的任务，默认不直接开始代码实现。
如果你直接要求写代码，但上下文不足，默认先补最小 `brief`。

## 分支与提交

建议采用轻量 trunk-based：

- 默认分支：`main`
- 功能分支：`brief/...`、`spec/...`、`build/...`
- 小改动可直接提交到 `main`

提交标题建议：

```text
[brief][新增] ...
[spec][修改] ...
[build][修复] ...
[validate][整理] ...
[repo][整理] ...
```

提交标题固定格式：

```text
[阶段][动作] 具体结果
```

动作固定使用：

- `新增 / 修改 / 修复 / 重构 / 整理 / 归档 / 删除`

混合改动默认按“主要交付物”选择主阶段。

本仓库已预设提交模板：

```powershell
git config commit.template .gitmessage.txt
```

## 新任务怎么开始

1. 先读 [docs/daily-manual.md](/D:/UGit/VibeFoundry/docs/daily-manual.md)
2. 再发送 [ai-kit/quick_start_prompt.md](/D:/UGit/VibeFoundry/ai-kit/quick_start_prompt.md)
3. 再读 [ai-kit/README.md](/D:/UGit/VibeFoundry/ai-kit/README.md)
4. 根据当前信息是否充分，进入：
   - [docs/templates/需求卡片模板.md](/D:/UGit/VibeFoundry/docs/templates/需求卡片模板.md)
   - [docs/templates/设计文档模板.md](/D:/UGit/VibeFoundry/docs/templates/设计文档模板.md)
5. 通过人工确认后再进入 `projects/` 落实现
6. 完成实现后补 [docs/templates/验收模板.md](/D:/UGit/VibeFoundry/docs/templates/验收模板.md)

日常执行先看 [docs/daily-manual.md](/D:/UGit/VibeFoundry/docs/daily-manual.md)，规则说明再看 [docs/workflow-v1.md](/D:/UGit/VibeFoundry/docs/workflow-v1.md)。

## 示例内容

- 示例 brief：[docs/briefs/sample-task/示例需求卡片.md](/D:/UGit/VibeFoundry/docs/briefs/sample-task/示例需求卡片.md)
- 示例 spec：[docs/specs/sample-task/示例设计文档.md](/D:/UGit/VibeFoundry/docs/specs/sample-task/示例设计文档.md)
- 示例 validate：[docs/validate/sample-task/示例验收记录.md](/D:/UGit/VibeFoundry/docs/validate/sample-task/示例验收记录.md)
- 示例小工具：[projects/demo-tool/README.md](/D:/UGit/VibeFoundry/projects/demo-tool/README.md)
- 示例应用：[projects/demo-app/README.md](/D:/UGit/VibeFoundry/projects/demo-app/README.md)
