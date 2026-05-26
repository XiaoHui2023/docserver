# 部署与子路径

## 部署在站点根

将 `dist/` 整个目录挂到 Web 服务器根路径即可。

```bash
python src -s <你的文档> -o dist
```

## 部署在子路径（如 `/docs/`）

构建时指定前缀，并给出与对外访问一致的完整 `site_url`：

```bash
python src -s <你的文档> -o dist --base-url /docs --site-url https://example.com/docs/
```

Nginx 需将 `/docs/` 映射到 `dist/`；页面内链接会带上此前缀。

## 监视模式参数

| 参数 | 说明 |
| --- | --- |
| `--interval` | 监视源目录间隔（秒），默认 `2` |

同步时会自动删除工作区里源目录已不存在的文件，无需额外开关。

```bash
python src -s example/source -o dist --watch --interval 1
```

预览端口由你自己启动的 `http.server`（或其它 Web 服务器）决定，与 `--watch` 无关。
