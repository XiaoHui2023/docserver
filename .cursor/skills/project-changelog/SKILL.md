---
name: project-changelog
description: 本仓库：按时间记录要求与决议；最新在上；矛盾以最新为准。
---

# 变更记录

## 2026-05-23

- **决议**：弃用 VitePress，改用 MkDocs Material 一站式构建；CLI 输出即为可部署静态目录（`-O`）。
- **决议**：CLI 仅负责构建/监视；HTTP 预览移至 `example.bat`（`http.server`）。子命令 `serve` 改名为 `watch`。
- **要求**：源目录支持任意静态资源；入口 md 为 readme/index（大小写不敏感）；`--base-url` 支持子路径部署。
- **废弃**：`sync` 子命令、内置预览（`preview.py`）、`serve --open/--port`、VitePress / Node 依赖。

## 2026-05-22

- **决议**：定位为通用文档服务：外部 Markdown 同步与构建（当时为 VitePress）。
- **废弃**：仅手写固定侧栏、无工具的演示流程。
