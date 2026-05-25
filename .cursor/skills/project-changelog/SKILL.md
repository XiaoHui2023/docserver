---
name: project-changelog
description: 本仓库：按时间记录要求与决议；最新在上；矛盾以最新为准。
---

# 变更记录

## 2026-05-25

- **决议**：`build.sh` / `build.bat` 产出离线压缩包（`release/docserver-offline-*.tar.gz` / `.zip`），内含 `release/bin/docserver-sync`、`project.yaml`、`run.sh`、`run.bat`、`theme/`；新增 `tools/stage-offline.sh`。frozen 下 `repo_root()` 以 `project.yaml` 识别离线包根。
- **修复**：`docserver-cli.spec` 用 `collect_all` + `copy_metadata` 打包 `material` / MkDocs 插件与 entry point 元数据，修复 onefile 下 `Unrecognised theme name: 'material'`。
- **修复**：PyInstaller/staticx 的 `docserver-sync` 在 Ubuntu 等环境构建时退出码 2：`build_site` 在 frozen 下改为进程内调用 MkDocs CLI，不再 `sys.executable -m mkdocs`（会误启动自身导致 argparse 退出 2）；`theme/` 通过 `repo_root()` 从 cwd/可执行文件路径向上解析。
- **决议**：CLI 短参改为小写 `-s` / `-o`（对齐 python-argparse-cli）；`run.sh` / `run.bat` 默认源目录为 `example/source`。
- **修复**：`run.bat` / `build.bat` / `update.bat` 统一 CRLF（`cmd` 在 LF-only 下会拆行乱码）；`run.bat` 增加 `chcp 65001`；`run.sh` 识别 Windows `.venv/Scripts/python.exe` 与 `docserver-sync.exe`。
- **决议**：CLI 合并为单一入口 `python src`；持续构建用 `--watch`（及 `--interval`、`--skip-initial`），不再提供 `watch` 子命令。`run.sh` / `run.bat` 去掉多余的 `build` 参数；仍兼容旧写法 `src build` / `src watch`。
- **决议**：`build.sh`、`run.sh`、`tools/pack.sh` 以 Git `100755` 入库；`.gitattributes` 增加 `*.sh text eol=lf`。`PACKAGING.md` / `tools/README.md` 示例改为 `./tools/pack.sh`，不再要求 clone 后 `chmod +x`。
- **修复**：`build.sh` / `build.bat` 中 `pip download` 去掉非法的 `-e`（仅 `pip install` 支持 editable）。

## 2026-05-24

- **决议**：移除 `--auto-refresh` 及轮询脚本；产物视为稳定静态站，更新后由用户手动刷新。CLI 仅 `build` / `watch`；`example.bat` = `watch` + `http.server`。
- **废弃**：`serve`、`--auto-refresh`、`docserver-build.txt`、自动刷新 JS。

## 2026-05-23

- **决议**：弃用 VitePress，改用 MkDocs Material 一站式构建；CLI 输出即为可部署静态目录（`-O`）。
- **决议**：CLI 仅负责构建/监视；HTTP 预览移至 `example.bat`（`http.server`）。子命令 `serve` 改名为 `watch`。
- **要求**：源目录支持任意静态资源；入口 md 为 readme/index（大小写不敏感）；`--base-url` 支持子路径部署。
- **废弃**：`sync` 子命令、内置预览（`preview.py`）、`serve --open/--port`、VitePress / Node 依赖。

## 2026-05-22

- **决议**：定位为通用文档服务：外部 Markdown 同步与构建（当时为 VitePress）。
- **废弃**：仅手写固定侧栏、无工具的演示流程。
