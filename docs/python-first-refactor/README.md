# Python First 重构文档归档说明

本目录中的文档已经进入**归档**状态。

它们记录的是本项目早期从本地对话链路切向 `AtlasClaw / xuanwu-server` 的过渡设计，仍然保留用于历史追溯，但**不再作为当前实现依据**。

## 当前应阅读的设计入口

请优先阅读以下现行文档：

1. [XuanWu Platform Blueprint](C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\docs\superpowers\specs\2026-03-30-xuanwu-platform-blueprint.md)
2. [Spec Index](C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\docs\superpowers\specs\README.md)
3. [Platform Implementation Roadmap](C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\docs\project\tasks\2026-03-30-platform-implementation-roadmap.md)

当前蓝图相对路径入口：
- `docs/superpowers/specs/2026-03-30-xuanwu-platform-blueprint.md`

## 归档内容范围

本目录主要保留这些历史专题：

- 早期主对话引擎切换方案
- 早期 runtime provider 方案
- 早期协议冻结稿
- 早期 fallback / Java 下线过渡稿

## 使用规则

- 这些文档只用于理解历史决策背景。
- 当归档内容与现行蓝图冲突时，以 `docs/superpowers/specs/` 和 `docs/project/` 下的最新文档为准。
- 后续开发不得再直接按本目录中的旧 `AtlasClaw` 方案继续落代码。
