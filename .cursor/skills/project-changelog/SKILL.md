---
name: project-changelog
description: 本仓库：按时间记录要求与决议；最新在上；矛盾以最新为准。
---

# 变更记录

## 2026-07-13

- **修复**：`--watch` 的构建失败/监视异常重试等待改为跟随 `--interval`（最低 0.5 秒），不再把长间隔硬压到 2 秒；`--interval 600` 场景下避免失败重试造成周期性高 CPU。新增 DEBUG 诊断日志与测试覆盖。
- **修复**：运行脚本进程生命周期收口：Linux `run.sh` 不再后台 `setsid`，改为 `exec docserver-sync` 接管脚本 PID；`example.sh` 不再 `exec http.server` 丢失 trap，退出时清理 watch/http 子进程树；Python `mkdocs` 子进程使用独立进程组并在父进程信号中清理，Linux 设置 parent-death signal；Windows `run-lifecycle.ps1` 使用 Job Object `KILL_ON_JOB_CLOSE` 包住进程树。

## 2026-06-19

- **决议**：接入 GitHub Release 滚动自动发布：`.github/workflows/release.yml`（push `main` → Ubuntu 16.04 PyInstaller + staticx → frozen `demo/` example 门禁 → 覆盖 `v{version}` tag 与 Release 附件）；新增 `tools/ci_pack_ubuntu16.sh`、`tools/bundle_release.py`、`tools/run_frozen_example.py`；`pack.sh` staticx 对齐 consolver（源码构建 staticx、`--no-compress` 回退、readelf 校验）并组装 `docserver-<version>-<platform>` 压缩包。

## 2026-06-15

- **决议**：前端配色收口为用户根通用 skill **`frontend-color-theme`**（非 MkDocs 专用）；删除 `mkdocs-material-color-theme`；Material/docserver 映射与路径写入本项目 design-notes **配色与主题** 专节；预加载与 `agent-project-preload` 同步。

## 2026-06-10

- **决议**：`--watch` 在频繁保存下不退出：同步阶段对 `read_text`/`copy2` 短暂重试；构建或监视循环内任意 `Exception` 均等待后重试；成功后再比对快照，构建期间仍有变更则继续重建直至稳定；仅 `Ctrl+C` 正常结束。单次 `build` 仍遇错误时非零退出。
- **决议**：构建暂存与发布备份迁入缓存：MkDocs 写入 `{cache}/site-staging/`，替换时旧 `out/` 暂存 `{cache}/site-out-backup/`；不再在 `-o` 旁生成 `*.staging` / `*.old` / `*.work`。
- **决议**：源目录支持指向目录的软链接：`scan.iter_source_files` 跟随目录软链接展开，路径按源树逻辑位置；`--watch` 对经软链接暴露的文件用逻辑路径监视。同一物理目录允许多链接挂载；递归链上防环。
- **决议**：打包入口迁回 `tools/pack.sh` / `tools/pack.bat`（对齐 `python-pyinstaller-staticx-packaging`）；删除仓库根 `pack.sh` / `pack.bat`；文档与 `run.bat` 提示同步更新。
- **决议**：侧栏展开路径须包含 active 链接所在分组：目录首页（`index`/`README`）时该目录 toggle 保持展开，同级其它目录仍折叠。`nav-active-branch.js` 自 active 项向上逐级展开 `__nav*`。
- **决议**：打包产物统一放入 `dist/`（可执行文件、离线压缩包），取消 `release/`；离线包内可执行文件路径为 `dist/docserver-sync`；`run` 与文档同步更新。
- **决议**：合并 `build.sh` / `build.bat` 与 `tools/pack.sh` 为根目录单一入口 `pack.sh` / `pack.bat`（依赖、vendor、PyInstaller、离线压缩包一步完成）；删除 `build.*` 与 `tools/pack.sh`；Windows 组装逻辑抽到 `tools/stage-offline.bat`。

## 2026-06-09

- **决议**：去掉 `navigation.expand`；侧栏默认只展开当前页祖先路径，同级其它目录折叠。新增 `nav-active-branch.js`：`document$` 后同步 `__nav*` 勾选状态，instant 换页时收起无关分组。

## 2026-06-02

- **决议**：离线包含 `demo/` 简易文档；`run` 默认 `SOURCES=demo`、`WATCH=0`（构建一次后退出便于快速体验）；`WATCH=1` 时加 `--watch`。`stage-offline.sh` / `build.bat` 打包 `demo/`；README 与 `tools/offline-package-readme.txt` 补充 run 变量与 CLI 参数说明。
- **决议**：`build.sh` / `build.bat` 不再跑示例站点自检（`output/smoke-test`）；在线打包仅装依赖、拉 vendor、PyInstaller 与离线压缩包。
- **决议**：instant 换页时 Material 会替换左栏 DOM，侧栏 `scrollTop` 丢失。新增 `sidebar-scroll-persist.js`：在站内链接点击前与侧栏滚动时记住位置，`document$` 后写回（双 `requestAnimationFrame` 覆盖主题后续滚动）。

## 2026-05-26

- **决议**：面包屑 `md-path`：按 `href` 对照 `index_paths` / `page_paths`；链到当前页（如无 index 目录的 `Advanced` 用 `./`）不可点；链到其它真实页面（如 `Guides`→`install`）可点。
- **决议**：MkDocs 写入 `{out}.staging/`，构建成功后目录级一次性替换 `out/`；构建过程中 `out/`（含 `search/`）不随 `--clean` 清空；失败则 `out/` 不变。
- **决议**：构建缓存与 `-o` 输出分离：默认当前工作目录 `.docserver-cache/`；可选 `--cache-dir`；不再生成 `{out}.work/`。
- **决议**：`--watch` 源目录仅轮询 `paths.WATCH_SOURCE_SUFFIXES`（文档与常见静态资源后缀，如 `.md`、`.png`、`.svg`、`.pdf`）；`theme/`、`src/` 仍监视全部文件，避免 `.log`/`.tmp` 等触发无意义重建。
- **决议**：回退侧栏同级克隆（移除 `nav-sync.js`）与路径条粘性；恢复 Material 默认左栏 + `navigation.expand`。保留 `docserver-nav-meta.json` + `path-index.js`：无目录入口的 `md-path` 层级灰显、`pointer-events: none`、无悬停反馈。不恢复侧栏「筛选导航」。
- **决议**：侧栏改为仅显示当前层级同级目录（`nav-sync.js` 克隆渲染，子级默认折叠）；构建写入 `docserver-nav-meta.json` 标记有入口 index 的路径；面包屑 `md-path` 粘性置顶、无入口层级灰显不可点；去掉 `navigation.expand`。（已由上条回退）
- **决议**：去掉侧栏「筛选导航」输入框（移除 `nav-filter.js`）；`nav-sync.js` 负责侧栏与路径条。（`nav-sync` 已移除；筛选仍不恢复）
- **决议**：`--watch` 检测到变更时按文件列出 `[新增]`/`[删除]`/`[修改]` 与相对路径（默认最多 8 条，超出显示「另有 N 个文件」）；不再仅打印一级子目录名。
- **决议**：入口 Markdown：每目录仅一个 `index.md` 首页（index 类优先于 readme 类，同类按大小写次序）；其余 `index`/`readme` 保留原名作普通页。`-s` 可多次指定，按顺序深合并，同路径后者覆盖前者。
- **决议**：复制页链按钮：仅 `:active` 轻微缩小 + 主题色（`--md-default-fg-color` / `--md-default-bg-color`）短暂提示「链接已复制到剪贴板」；去掉勾号换图标、强调色气泡、悬停 tooltip 改文案。
- **决议**：instant 搜索栏闪烁根因：Material `__palette` 按 pathname 分桶，`__md_get` 在新路径为空；`document$` 回写 body + `clearMaterialColors` 触发重绘。修复：`readPaletteColor` 优先顶栏 radio；`docserver-scheme` 全站镜像；`docserver-boot.js` 写 guard；`location$`/`document$` 只 `pinSchemeGuard` 不改 body；去掉 body MO；J 主题顶栏/搜索仅 `data-docserver-scheme-guard` 选择器；`docserver-base.css` 禁用顶栏 search transition。
- **决议**：设计笔记增加 **instant 换页搜索栏闪烁** 排障表。

## 2026-05-25

- **决议**：隐藏左侧导航顶部的站点名行（`md-nav__title` / drawer 标题），站点名仅保留顶栏。
- **决议**：左侧导航增加「筛选导航」输入框（`nav-filter.js`）：按侧栏标题与路径过滤目录树，非 MkDocs 插件；Material 无内置侧栏搜索。
- **决议**：J 主题 `data-docserver-scheme-guard="default"` 下顶栏/搜索栏样式始终 `!important` 锁定浅色（不依赖 `data-md-color-switching`），修复换页搜索框闪黑。
- **决议**：导航筛选框挂到 `.md-sidebar__inner`（在 `md-nav--primary` 外），instant 换页不消失；`data-docserver-scheme-guard` + J 主题 CSS 抑制浅色下闪黑顶栏/搜索；J 浅色搜索 placeholder/图标加深。
- **决议**：instant 的 `document$` 仅 `syncAfterInstantNavigation()`（配色），顶栏控件只 `init` 一次；`mermaid-init.js` 按需加载；`example.bat`/`example.sh` 构建前清空 `dist/`。
- **决议**：instant 换页后同步 `restoreMaterialPalette()`（`data-md-color-switching` 抑制过渡闪屏）并 `refreshDocserverColors()`；去掉正文淡入动画。
- **决议**：`--watch` 监视整个 `src/`（跳过 `__pycache__` 等）；设计笔记增加 **Example 预览与改动生效**（`dist/` 与 `theme/` 分工、example 不变常见原因、Agent 检查清单）；`example.bat` / `example.sh` 提示硬刷新与监视范围。
- **决议**：修复 instant 换页退化为整页刷新：`theme-switcher` 顶栏控件只排序一次，换页后不再反复 `insertBefore` 顶栏 DOM；`nav-filter` 在 Material 换页完成后再挂载。
- **决议**：instant 导航启用 `navigation.instant.prefetch`；正文换页动画改为 0.1s 轻淡入；`theme-switcher` 用 `document$` 换页回调替代点击后 150ms 全量 `init`。
- **决议**：顶栏控件顺序为搜索、分享（复制当前页链接，中文路径用解码后的 Unicode）、配色风格、明暗切换；关闭 Material `search.share`（搜索框内不再出现分享）。
- **决议**：`--watch` 检测到变更时打印归并后的一级子目录名（源下首层目录为粒度，源根文件为 `(根目录)`，主题等为监视根目录名）；不限于 `--verbose`。
- **决议**：工作区同步始终 `clean=True`（删除源中已移除的文件），不再提供 `--clean` 参数。
- **决议**：`--watch` / 单次构建打印「构建开始」「构建结束」时间；`--log DIR` 将控制台输出写入 `DIR/年-月-日/时-分-秒.log`（`run` 脚本变量 `LOG`）。
- **修复**：`mkdocs` privacy 设 `assets_fetch: false`：正文内外链图片/附件不再构建时下载，保留原始 URL（浏览器打开后再加载）；避免内网图床失败导致 `构建失败`。
- **修复**：`.pages` 的 `nav`/`title` 标量统一加引号，允许文件名含 `@`（避免 YAML `cannot start any token`）。
- **修复**：`.pages` 仅把「目录树内至少有一个 `.md`」的子目录写入 `nav`（`image/`、`assets/` 等纯静态目录不再报错）。`prepare_work` 先 `install_theme_assets` 再写 `.pages`。
- **决议**：在线 `build` 预拉 `theme/javascripts/mermaid.min.js` 与 privacy 缓存；离线 zip 含 `cache/plugin/privacy/`；`mkdocs` privacy 使用 `cache_dir: cache/plugin/privacy`。`stage-offline.sh` 对 `run.sh`、二进制 `chmod +x` 后 `tar -p`。
- **决议**：去掉 `project.yaml`；运行参数写在 `run.sh` / `run.bat`（每行一项 CLI 参数）。frozen 根目录以 `theme/` 识别。
- **决议**：`run.sh` / `run.bat` 仅调用 `release/bin/docserver-sync`（`--watch`），不回退 `.venv` / `python src`。离线包不含 `pyproject.toml`。已去掉 `offline-packages` 下载步骤。
- **决议**：离线压缩包仅含与构建脚本对应的启动器：`build.sh` → `run.sh`；`build.bat` → `run.bat`（不同时打包两种）。
- **决议**：`build.sh` / `build.bat` 产出离线压缩包（`release/docserver-offline-*.tar.gz` / `.zip`），内含 `release/bin/docserver-sync`、`project.yaml`、`theme/`；新增 `tools/stage-offline.sh`。frozen 下 `repo_root()` 以 `project.yaml` 识别离线包根。
- **修复**：`docserver-cli.spec` 用 `collect_all` + `copy_metadata` 打包 `material` / MkDocs 插件与 entry point 元数据，修复 onefile 下 `Unrecognised theme name: 'material'`。
- **修复**：PyInstaller/staticx 的 `docserver-sync` 在 Ubuntu 等环境构建时退出码 2：`build_site` 在 frozen 下改为进程内调用 MkDocs CLI，不再 `sys.executable -m mkdocs`（会误启动自身导致 argparse 退出 2）；`theme/` 通过 `repo_root()` 从 cwd/可执行文件路径向上解析。
- **决议**：CLI 短参改为小写 `-s` / `-o`（与 python-argparse-cli 一致）；`run.sh` / `run.bat` 默认源目录为 `example/source`。
- **修复**：`run.bat` / `build.bat` / `update.bat` 统一 CRLF（`cmd` 在 LF-only 下会拆行乱码）；`run.bat` 增加 `chcp 65001`；`run.sh` 识别 Windows `.venv/Scripts/python.exe` 与 `docserver-sync.exe`。
- **决议**：CLI 合并为单一入口 `python src`；持续构建用 `--watch`（及 `--interval`、`--skip-initial`），不再提供 `watch` 子命令。`run.sh` / `run.bat` 去掉多余的 `build` 参数；仍兼容旧写法 `src build` / `src watch`。
- **决议**：`build.sh`、`run.sh`、`tools/pack.sh` 以 Git `100755` 入库；`.gitattributes` 增加 `*.sh text eol=lf`。`PACKAGING.md` / `tools/README.md` 示例改为 `./tools/pack.sh`，不再要求 clone 后 `chmod +x`。
- **修复**：`build.sh` / `build.bat` 中 `pip download` 去掉非法的 `-e`（仅 `pip install` 支持 editable）。

## 2026-05-24

- **决议**：移除 `--auto-refresh` 及轮询脚本；产物视为稳定静态站，更新后由用户手动刷新。CLI 仅 `build` / `watch`；`example.bat` = `watch` + `http.server`。
- **废弃**：`serve`、`--auto-refresh`、`docserver-build.txt`、自动刷新 JS。

## 2026-05-23

- **决议**：弃用 VitePress，改用 MkDocs Material 单命令构建；CLI 输出即为可部署静态目录（`-O`）。
- **决议**：CLI 仅负责构建/监视；HTTP 预览移至 `example.bat`（`http.server`）。子命令 `serve` 改名为 `watch`。
- **要求**：源目录支持任意静态资源；入口 md 为 readme/index（大小写不敏感）；`--base-url` 支持子路径部署。
- **废弃**：`sync` 子命令、内置预览（`preview.py`）、`serve --open/--port`、VitePress / Node 依赖。

## 2026-05-22

- **决议**：定位为通用文档服务：外部 Markdown 同步与构建（当时为 VitePress）。
- **废弃**：仅手写固定侧栏、无工具的演示流程。
