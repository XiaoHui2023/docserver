# Material 主题配色选型

docserver 通过 `src/mkdocs_config.py` 里的 `theme.palette` 设置外观。每种方案包含 **浅色（default）** 与 **深色（slate）** 两套；用户可在站点顶栏切换。

## 可调维度

| 维度 | 可选值 | 作用 |
| --- | --- | --- |
| **scheme** | `default`（浅）、`slate`（深） | 背景与正文对比 |
| **primary** | 见下表「主色」列 | 顶栏、侧栏、链接主色 |
| **accent** | 见下表「强调色」列 | 悬停、按钮、滚动条等交互色 |
| **font.text** | 任意 [Google Font](https://fonts.google.com/) 名 | 正文（当前默认 `Noto Sans SC`） |
| **font.code** | 同上 | 代码块（当前 `Roboto Mono`） |

### 官方主色（primary）全集

`red` · `pink` · `purple` · `deep purple` · `indigo` · `blue` · `light blue` · `cyan` · `teal` · `green` · `light green` · `lime` · `yellow` · `amber` · `orange` · `deep orange` · `brown` · `grey` · `blue grey` · `black` · `white`

### 官方强调色（accent）全集

`red` · `pink` · `purple` · `deep purple` · `indigo` · `blue` · `light blue` · `cyan` · `teal` · `green` · `light green` · `lime` · `yellow` · `amber` · `orange` · `deep orange`

（accent 不含 brown / grey / black / white。）

---

## 推荐组合（精选 8 套）

任选一套，将 `primary` / `accent` 写入 `mkdocs_config.py` 中 **两段** `palette`（`default` 与 `slate` 建议相同）。

| 编号 | 名称 | primary | accent | 风格简述 |
| --- | --- | --- | --- | --- |
| **A** | 经典靛蓝（当前默认） | `indigo` | `indigo` | 常见技术文档，稳重 |
| **B** | 企业蓝 | `blue` | `light blue` | 偏商务、清晰 |
| **C** | 青绿运维 | `teal` | `green` | 清爽、偏基础设施文档 |
| **D** | 深紫产品 | `deep purple` | `pink` | 现代 SaaS 感 |
| **E** | 蓝灰专业 | `blue grey` | `cyan` | 低饱和、长时间阅读 |
| **F** | 青橙对比 | `cyan` | `orange` | 活泼、强调可点击元素 |
| **G** | 森林绿 | `green` | `light green` | 开源 / 数据平台 |
| **H** | 深色顶栏 | `black` | `amber` | 浅色模式下顶栏偏「控制台」风 |

### 黑白灰 / GitHub 风（无内置「GitHub 主题」，可近似）

Material **没有**一键 GitHub 皮肤，但可用 **灰阶主色 + 蓝色强调（链接）** 接近 [GitHub Docs](https://docs.github.com/) / README 阅读体验：

| 编号 | 名称 | 浅色 primary | 浅色 accent | 深色 primary | 深色 accent | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| **I** | GitHub 经典 | `white` | `blue` | `black` | `blue` | 浅底白顶栏 + 深底黑顶栏，链接蓝（最接近） |
| **J** | GitHub 灰栏 | `grey` | `blue` | `black` | `light blue` | 浅灰侧栏/顶栏，深色模式偏 `#0d1117` 感 |
| **K** | 纯灰极简 | `blue grey` | `blue` | `blue grey` | `light blue` | 整体低饱和蓝灰，几乎无彩色块 |
| **L** | 黑白+蓝链 | `black` | `blue` | `black` | `light blue` | 仅黑顶栏 + 蓝链接，侧栏仍随 scheme |

说明：

- 灰阶主色只用 **`grey` · `blue grey` · `black` · `white`**（primary 表内）。
- 链接色用 **`blue` / `light blue`** 代替 GitHub 的 `#0969da` / `#58a6ff`。
- 深色模式用 **`scheme: slate`**；可把 `--md-hue` 调到约 `210`（偏冷灰，见 [自定义配色](https://squidfunk.github.io/mkdocs-material/setup/changing-the-colors/#custom-color-schemes)）。
- 字体建议配 **F4（系统字体）** 或 **F2（Roboto）**，更接近 GitHub 无衬线栈。
- 若要 **像素级** 还原，在 `theme/palettes/` 增加对应 CSS，并在 `theme-switcher.js` 的 `STYLES` 中注册。

**docserver 构建默认：J GitHub 灰栏**（`src/mkdocs_config.py` + `theme/palettes/j-github.css`）。

**静态站运行时**：顶栏或左栏下拉可切换 **J、I、K、L、C、B、A、D、E、F、G、H**（`theme/javascripts/theme-switcher.js`，默认 **J**，偏好键 `docserver-style`）。**J / I / K / L / C** 有 `theme/palettes/*.css` 像素级样式；**B–H** 使用 Material 内置色板（名称须为连字符，如 `deep-purple`）。

**推荐首选：I 或 J + F4。**

### 配置片段示例（以 B「企业蓝」为例）

在 `write_mkdocs_yml` 生成的 `palette` 中：

```yaml
  palette:
    - scheme: default
      primary: blue
      accent: light blue
      toggle:
        icon: material/brightness-7
        name: 切换到深色模式
    - scheme: slate
      primary: blue
      accent: light blue
      toggle:
        icon: material/brightness-4
        name: 切换到浅色模式
```

---

## 如何选定

回复 **编号（A–L / I–J 等）** 或 **primary + accent 名称**（如 `grey` + `blue`），可在 `mkdocs_config.py` 中改默认配色。

若需 **跟随系统明/暗**，可在 `palette` 条目上增加 `media: "(prefers-color-scheme: light)"` / `dark`（见 [Material 文档](https://squidfunk.github.io/mkdocs-material/setup/changing-the-colors/#system-preference)）。

---

## 字体备选（与配色独立）

| 编号 | text | code | 说明 |
| --- | --- | --- | --- |
| F1 | `Noto Sans SC` | `Roboto Mono` | **当前默认**，中文友好 |
| F2 | `Roboto` | `Roboto Mono` | Material 原版英文组合 |
| F3 | `Noto Serif SC` | `JetBrains Mono` | 正文偏衬线、代码更锐 |
| F4 | `false` | `false` | 不加载 Google Font，用系统字体（内网 / 隐私） |
