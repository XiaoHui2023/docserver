---
name: project-design-notes
description: 本仓库：Agent 当前有效的设计意图与硬性要求；变更见 project-changelog。
---

# 设计笔记（当前有效）

> 变更记录见 `.cursor/skills/project-changelog/SKILL.md`；矛盾以 changelog 最新条目为准。

## 设计意图

- **通用静态文档构建器**：输入为单一源目录（多层子目录、每层可有入口 Markdown、同级可有静态资源）；输出为可直接部署的静态站点目录。
- **站点引擎**：MkDocs + Material for MkDocs + awesome-pages；左栏导航、右侧 TOC、全文搜索、明/暗主题。
- **入口 Markdown 命名**：`readme` / `index` 等（扩展名 `.md`，文件名大小写不敏感）映射为构建用 `index.md`；同目录同时存在时 **index 优先于 readme**。
- **导航**：目录树 + 每层 `.pages`（构建时生成）；分组标题取自该层 `index.md` 首个 `#` 标题。
- **子路径部署**：`--base-url`（如 `/docs`）写入 `site_url`；可用 `--site-url` 覆盖完整 URL。
- **监视构建**：`build` 加 `--watch` 对源目录任意文件 mtime 轮询；变更后重新 staging 并调用内部 MkDocs 构建（用户不直接执行 `mkdocs` 命令）。
- **预览**：不提供内置 HTTP；`example.sh` / `example.bat` = `--watch` + `http.server`，更新后由用户手动刷新。
- **工作区**：`{out}.work/` 含 `docs/` 与 `mkdocs.yml`；`out/` 仅为发布产物。
- 示例源：`example/source/`；打包见 `tools/pack.sh`（`docserver-sync` onefile）。`build.sh` / `run.sh` / `example.sh` / `tools/pack.sh` 已 Git 跟踪可执行位（Unix clone 可 `./`；Windows 仍用 `.bat` 或 `bash`）。

## 硬性要求

- 用户向文档遵守 `forbidden-doc-comment-vocabulary`。
- `-o` 为构建产物目录，不是源目录；勿与 `-s` 混为同一目录。
- 构建依赖 Python 包：`mkdocs-material`、`mkdocs-awesome-pages-plugin`（见 `pyproject.toml`）。
- 已移除 VitePress / Node 构建链。
- 仓库 `.cursor/skills/` 仅三件套。

## 备忘与待定

- 监视为轮询，非 inotify。
- PyInstaller onefile 体积较大（捆绑 MkDocs/Material）；内网离线运行用 `build` 打的压缩包 + `run`，无需 `pyproject.toml`。
