# docserver

通用 VitePress 文档站：站点壳与主题为静态资源；正文 Markdown 由外部目录经同步工具写入本站，可一次同步或监视源目录持续更新。站点内置本地全文搜索（构建后生效）。

## 命令行参数

入口：`python src`（或打包后的 `docserver-sync`）。

| 长参数 | 短参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `--source` | `-S` | 路径 | 必填 | 源文档根目录 |
| `--out` | `-O` | 路径 | 必填 | VitePress 项目根（含 `.vitepress`、`package.json`） |
| `--verbose` | `-v` | 开关 | 关 | 打印每个同步文件 |
| `--clean` | | 开关 | 关 | 删除上次同步、本次已不存在的 Markdown |
| `--interval` | | 数字（秒） | `2` | 仅 `serve`：轮询间隔 |

子命令：

| 子命令 | 说明 |
| --- | --- |
| `sync` | 同步一次 |
| `serve` | 监视源目录并持续同步 |

示例（仓库根）：

```bash
python src sync -S example/source -O .
python src serve -S example/source -O . --interval 2
```

Windows 可先执行 `update.bat` 创建 `.venv`，`example.bat` 同步示例文档。

## 构建与部署静态站

```bash
npm install
python src sync -S <你的文档目录> -O .
npm run docs:build
```

构建产物在 `.vitepress/dist`，将整个目录部署到任意静态 Web 服务器（Nginx、对象存储静态托管等）。开发预览：`npm run docs:dev`；构建后本地预览：`npm run docs:preview`。

## 打包同步工具

仓库根执行 `./tools/pack.sh`（Linux 需 `patchelf`），得到 `dist/docserver-sync`（Windows 为 `.exe`）。说明见 [PACKAGING.md](PACKAGING.md)。
