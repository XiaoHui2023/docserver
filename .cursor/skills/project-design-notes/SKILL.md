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
- **目录软链接**：源树内指向目录的软链接会展开扫描；站点路径按链接在源树中的逻辑位置（如 `linked/foo.md`）；同一物理目录可经多个链接分别挂载；构建产物仍为普通文件（不保留软链接）。
- **导航**：目录树 + 每层 `.pages`（构建时生成）；分组标题取自该层 `index.md` 首个 `#` 标题。
- **子路径部署**：`--base-url`（如 `/docs`）写入 `site_url`；可用 `--site-url` 覆盖完整 URL。
- **监视构建**：`build` 加 `--watch` 对源目录按 `WATCH_SOURCE_SUFFIXES`（`paths.py`）过滤后的文件 mtime 轮询；`theme/`、`src/` 仍监视全部文件；变更后重新 staging 并调用内部 MkDocs 构建（用户不直接执行 `mkdocs` 命令）。同步、MkDocs 与监视循环内任意可恢复错误均等待后重试，不退出进程（仅 `Ctrl+C` 结束）；构建成功后再比对快照，期间仍有变更则继续重建直至稳定。
- **预览**：不提供内置 HTTP；`example.sh` / `example.bat` = `--watch` + `http.server`，更新后由用户手动刷新。
- **输出与缓存分离**：`-o` 仅为可部署静态站点；构建缓存在当前目录 `.docserver-cache/`（可用 `--cache-dir` 指定），含 `docs/` 与 `mkdocs.yml`。
- **输出原子更新**：MkDocs 只写缓存内 `site-staging/`；成功后将暂存目录替换 `out/`（构建中 `out/` 不变，便于持续预览与搜索）。除 `-o` 与缓存目录外不生成其它路径。
- 示例源：`example/source/`（开发预览）；离线包自带 `demo/`（`run` 默认源，`WATCH=0` 构建一次）。在线打包见 `tools/pack.sh` / `tools/pack.bat`（`docserver-sync` onefile + 离线压缩包）。`tools/pack.sh` / `run.sh` / `example.sh` 已 Git 跟踪可执行位（Unix clone 可 `./`；Windows 仍用 `.bat` 或 `bash`）。

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
5. **instant 换页**：通用配色与 guard 见用户根 **`frontend-color-theme`**；本仓库 Material 专节见下文 **配色与主题（MkDocs Material）**。`mermaid` 用 `mermaid-init.js` 按需加载。

### instant 换页搜索栏闪烁（Agent 排障）

通用排障见 **`frontend-color-theme`**。本仓库对照 **配色与主题** 表中 Material 项；验收：浅色 J 连点 5 个不同层级页面，搜索框无闪变。若改 JS/CSS 仍闪，见上文 **Example 预览**。

## 配色与主题（MkDocs Material）

通用两层模型、scheme-guard、换页禁令见 **`~/.cursor/skills/frontend-color-theme/SKILL.md`**。本仓库映射与专有行为如下。

### 文件与键名

| 路径 / 键 | 职责 |
| --- | --- |
| `src/mkdocs_config.py` | 构建默认 palette（**J**：grey+blue / black+light blue）；`extra_css` / `extra_javascript` 顺序 |
| `theme/palettes/<id>-*.css` | J/I/K/L/C 像素级样式；前缀 `html[data-docserver-style="<id>"]` |
| `theme/docserver-base.css` | 通用 UX；顶栏 search `transition: none` |
| `theme/javascripts/docserver-boot.js` | 首屏写 `data-docserver-style`、`data-docserver-scheme-guard` |
| `theme/javascripts/theme-switcher.js` | `STYLES`、`STYLES_WITH_PALETTE_CSS`、instant 回调 |
| `localStorage` `docserver-style` / `docserver-scheme` | 全站 style 与 scheme 镜像 |
| `THEME-PALETTES.md` | 选型表 A–L、字体 F1–F4 |

构建默认 J；运行时可切 J/I/K/L/C/B/A/D/E/F/G/H。**J/I/K/L/C** 有 `palettes/*.css`；**B–H** 用 Material 内置 primary/accent（连字符 slug）。

### Material 专有

- 明暗属性：`data-md-color-scheme`（`default` / `slate`）；主色 `data-md-color-primary` / `data-md-color-accent`。
- `__palette` 按 **pathname 分桶**存 localStorage；`readPaletteColor()` **优先**顶栏 `input[name="__palette"]:checked`。
- 有 palette CSS 时不再向 body 写 primary/accent（`STYLES_WITH_PALETTE_CSS` + `clearMaterialColors`）。
- **顶栏/搜索** CSS 只认 `html[data-docserver-style][data-docserver-scheme-guard]`，不用仅绑 `body[data-md-color-scheme]`。
- instant：`location$` / `document$` 仅 `pinSchemeGuard()` + `syncPaletteRadios()`；`document$` 可 `refreshDocserverColors()`，**禁止**改 body 配色或重挂顶栏。

### 新增 palette（本仓库）

1. `THEME-PALETTES.md` 补选型；2. `theme/palettes/<id>-<name>.css`；3. `theme-switcher.js` 注册 `STYLES` / `STYLE_ORDER` / `STYLES_WITH_PALETTE_CSS`；4. 重建 `dist/`；5. J 浅色连点 5 页验收。仅改构建默认：改 `mkdocs_config.py` 的 `palette` 两段。

## 硬性要求

- 用户向文档遵守 `forbidden-doc-comment-vocabulary`。
- `-o` 为构建产物目录，不是源目录；勿与 `-s` 混为同一目录。
- 构建依赖 Python 包：`mkdocs-material`、`mkdocs-awesome-pages-plugin`（见 `pyproject.toml`）。
- 已移除 VitePress / Node 构建链。
- 仓库 `.cursor/skills/` 仅三件套。

## 备忘与待定

- 监视为轮询，非 inotify。
- PyInstaller onefile 体积较大（捆绑 MkDocs/Material）；内网离线运行用 `build` 打的压缩包 + `run`，无需 `pyproject.toml`。
