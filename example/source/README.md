# Docserver 示例站

本目录是 **docserver** 的演示源文档。运行仓库根的 `example.sh`（Unix）或 `example.bat`（Windows）：后台 `--watch` 构建，`http.server` 提供预览；保存源文件后请在浏览器中手动刷新。

## 站点功能一览

在预览页中可逐项体验：

| 功能 | 在哪里试 |
| --- | --- |
| **左侧导航** | 本页侧栏：首页、指南、功能演示、参考 |
| **右侧本页目录** | 任意长文（如 [Markdown 能力](showcase/markdown.md)）右侧锚点 |
| **顶栏全文搜索** | 搜索框输入 `搜索演示词` 或页面标题关键词 |
| **明 / 暗主题** | 顶栏右侧太阳 / 月亮图标切换 |
| **代码复制** | 代码块右上角复制按钮 |
| **静态资源** | [资源与图片](showcase/static-files.md) 中的示意图 |

## 推荐浏览顺序

1. [安装与构建](guides/install.md)
2. [功能演示](showcase/index.md)
3. [部署与子路径](guides/advanced/config.md)
4. [术语表](reference/glossary.md)

## 快速命令

```bash
python src -S example/source -O dist --watch
python -m http.server 8000 --bind 127.0.0.1 --directory dist
```

Unix：`bash example.sh`；Windows 可双击 `example.bat`（后台 `--watch` + 浏览器预览）。
