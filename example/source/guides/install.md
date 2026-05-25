# 安装与构建

## 环境

- Python 3.10+
- 仓库根执行 `update.bat`（Windows）或 `pip install -e ".[dev]"`

## 一次构建

```bash
python src -S example/source -O dist
```

`-O` 目录即为可部署的静态站点根（含 `index.html`）。

## 监视并自动重建

```bash
python src -S example/source -O dist --watch
```

会监视 `example/source` 下**任意文件**变更并自动重新构建（不提供 HTTP 服务）。

## 本地预览

构建完成后，对输出目录启动静态服务，例如：

```bash
python -m http.server 8000 --bind 127.0.0.1 --directory dist
```

浏览器打开 `http://127.0.0.1:8000/`。仓库根 `example.bat` 已组合上述两步。

## 入口 Markdown 命名

每层目录可用以下任一名称作为该层首页（不区分大小写）：

- `readme.md` / `README.md`
- `index.md` / `Index.md`

构建时统一为 MkDocs 所需的 `index.md`。
