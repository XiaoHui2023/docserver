---
name: project-design-notes
description: 本仓库：Agent 当前有效的设计意图与硬性要求；变更见 project-changelog。
---

# 设计笔记（当前有效）

> 变更记录见 `.cursor/skills/project-changelog/SKILL.md`；矛盾以 changelog 最新条目为准。

## 设计意图

- **通用静态文档构建器**：输入为单一源目录（多层子目录、每层可有入口 Markdown、同级可有静态资源）；输出为可直接部署的静态站点目录。
- **站点引擎**：MkDocs + Material for MkDocs + awesome-pages；左栏导航、右侧 TOC、全文搜索、明/暗主题。
- **入口 Markdown 命名**：`index` / `readme` 多种大小写；每目录择一映射为 `index.md`（**index 类优先于 readme 类**；同类按大小写次序，`readme` 优于 `README` 等）。同目录其余入口文件保留原名作普通页，不丢弃。
- **多源目录**：`-s` 可重复；按顺序深合并，同 `dest_rel` 后者覆盖前者。
- **导航**：目录树 + 每层 `.pages`（构建时生成）；分组标题取自该层 `index.md` 首个 `#` 标题。
- **子路径部署**：`--base-url`（如 `/docs`）写入 `site_url`；可用 `--site-url` 覆盖完整 URL。
- **监视构建**：`build` 加 `--watch` 对源目录按 `WATCH_SOURCE_SUFFIXES`（`paths.py`）过滤后的文件 mtime 轮询；`theme/`、`src/` 仍监视全部文件；变更后重新 staging 并调用内部 MkDocs 构建（用户不直接执行 `mkdocs` 命令）。
- **预览**：不提供内置 HTTP；`example.sh` / `example.bat` = `--watch` + `http.server`，更新后由用户手动刷新。
- **输出与缓存分离**：`-o` 仅为可部署静态站点；构建缓存在当前目录 `.docserver-cache/`（可用 `--cache-dir` 指定），含 `docs/` 与 `mkdocs.yml`。
- **输出原子更新**：MkDocs 只写 `{out}.staging/`；成功后将暂存目录重命名为 `out/`（构建中 `out/` 不变，便于持续预览与搜索）。
- 示例源：`example/source/`（开发预览）；离线包自带 `demo/`（`run` 默认源，`WATCH=0` 构建一次）。打包见 `tools/pack.sh`（`docserver-sync` onefile）。`build.sh` / `run.sh` / `example.sh` / `tools/pack.sh` 已 Git 跟踪可执行位（Unix clone 可 `./`；Windows 仍用 `.bat` 或 `bash`）。

## Example 预览与改动生效（Agent 必查）

`example.bat` / `example.sh` 预览的是 **`dist/`**，不是仓库里的 `theme/` 或 `src/` 源文件。改 UI/引擎后若 example「看起来没变」，先对照下表，**不要**误以为只改 `example/source` 就够。

### 目录分工

| 路径 | 作用 | 是否被 example 直接读取 |
| --- | --- | --- |
| `example/source/` | 演示用 Markdown / 静态资源 | 是（`-s` 源） |
| `theme/` | 站点 CSS/JS、配色方案 | 否；构建时复制进缓存 `docs/` 再进 `dist/` |
| `src/` | 构建逻辑、`mkdocs.yml` 生成 | 否；由 `python src` 在构建时执行 |
| `dist/` | 静态站点产物 | **http.server 只服务此目录** |
| `.docserver-cache/` | 构建缓存（默认，可用 `--cache-dir`） | 否（构建用） |

### 构建链路（单次）

```text
example/source  ──sync──►  .docserver-cache/docs/
theme/          ──copy──►  .docserver-cache/docs/stylesheets|javascripts/
src/            ──生成──►  .docserver-cache/mkdocs.yml
.docserver-cache/ ──mkdocs build──►  dist/
```

### 为何「改了代码 example 不变」

| 原因 | 说明 | 处理 |
| --- | --- | --- |
| 改错目录 | UI 在 `theme/`，配置在 `src/mkdocs_config.py`；仅 `example/source` 管文档内容 | 改对目录后重建 |
| 未重建 `dist/` | 长开 `example.bat` 时后台 `--watch --skip-initial` 只在**监视路径**变更后重建；旧进程可能未覆盖本次改动 | 保存 `theme/` 或 `src/` 触发 watch，或 **关掉 example 再重新运行** |
| 监视未含 `src/`（已修） | 过去只监视 `theme/` 与少量 py；改 `watch.py` 等不触发重建 | 现已监视整个 `src/`；仍建议改 Python 后重启 example |
| 浏览器缓存 | `dist/javascripts/*.js`、`stylesheets/*.css` 易被强缓存 | 重建后 **Ctrl+F5** |
| 文档说明未改 | 功能说明写在 `example/source/**/*.md`；改引擎不会自动改这些 md | 功能变更时同步改 showcase 等 md |

### Agent 改动能进 example 的检查清单

1. 若动 `theme/` 或 `src/`：确认 `dist/javascripts/`、`dist/stylesheets/` 与 `theme/` 一致（或让用户重跑 `example.bat`）。
2. 若动用户可见行为：更新 `example/source/` 内相关说明（如 `showcase/navigation.md`）。
3. 回合结束前提醒：重开 example 或等 watch 打「构建结束」，浏览器 **Ctrl+F5**。
4. **不要**在 `example/` 下复制一份 `theme/`（避免双份漂移）。
5. **instant 换页**：`document$` 回调里**禁止**反复 `insertBefore` 顶栏/乱改侧栏 DOM，否则退化成整页刷新（终端会再次请求 `bundle.js`）；**禁止**在 `document$` 里 `setAttribute`/`clearMaterialColors` 改 `body` 配色（会触发搜索栏重绘闪烁）。顶栏/搜索样式只跟 `html[data-docserver-scheme-guard]`（见 `theme/palettes/*` + `docserver-base.css` 禁用 search transition）。`location$` 与 `document$` 仅 `pinSchemeGuard()` + `syncPaletteRadios()`。顶栏分享/配色控件只在首次 `init` 挂载。`mermaid` 用 `mermaid-init.js` 按需加载。

### instant 换页搜索栏闪烁（Agent 排障）

| 现象 | 常见根因 | 处理 |
| --- | --- | --- |
| 每次点侧栏换页搜索框背景闪一下 | Material `__palette` 按 **pathname 分桶**存 localStorage；新路径上 `__md_get("__palette")` 为空，旧代码误以为「无配色」或把 body 写回构建默认再 `clearMaterialColors` | `readPaletteColor()` **优先读顶栏** `input[name="__palette"]:checked`（instant 不销毁顶栏）；并镜像 `docserver-scheme` 全站键；`docserver-boot.js` 尽早写 `data-docserver-scheme-guard` |
| 改 JS/CSS 仍闪 | example 服务 `dist/` 未重建或浏览器缓存 | 重跑/等 watch 构建，`Ctrl+F5` |
| 顶栏偶发闪、搜索必闪 | 仅用 `body[data-md-color-scheme]` 画顶栏/搜索，与 guard 规则打架 | 自定义 palette（J 等）顶栏/搜索 **只写 guard 选择器**；勿在 `document$` 用 MutationObserver 回写 body |
| 验收 | 浅色方案 J 连点 5 个不同层级页面 | 搜索框白底/边框无可见闪变；深色模式同理 |

## 硬性要求

- 用户向文档遵守 `forbidden-doc-comment-vocabulary`。
- `-o` 为构建产物目录，不是源目录；勿与 `-s` 混为同一目录。
- 构建依赖 Python 包：`mkdocs-material`、`mkdocs-awesome-pages-plugin`（见 `pyproject.toml`）。
- 已移除 VitePress / Node 构建链。
- 仓库 `.cursor/skills/` 仅三件套。

## 备忘与待定

- 监视为轮询，非 inotify。
- PyInstaller onefile 体积较大（捆绑 MkDocs/Material）；内网离线运行用 `build` 打的压缩包 + `run`，无需 `pyproject.toml`。
