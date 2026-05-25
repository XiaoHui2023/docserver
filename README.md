# docserver

将多层 Markdown 文档目录（含静态资源）构建为可部署的静态站点：左栏导航、右侧目录锚点、全文搜索、明/暗主题切换。基于 MkDocs Material，构建链仅需 Python。

## 设计概要

| 环节 | 说明 |
| --- | --- |
| 输入 | 单一源目录：递归包含 `.md` 与图片等任意静态文件 |
| 入口页 | 每层目录可用 `readme` / `README` / `index` 等（不区分大小写）作为该层首页，构建时统一为 `index.md` |
| 导航 | 目录结构即站点结构；各层 `.pages` 控制侧栏顺序与分组标题（取自入口页一级标题） |
| 输出 | `-o` / `--out` 指向的目录即为静态站点根（含 `index.html`），可直接交给 Nginx / 对象存储 |
| 子路径 | `--base-url /xxx` 用于部署在 `https://域名/xxx/` 下；可用 `--site-url` 指定完整 canonical URL |
| 监视 | `--watch`：源目录任意文件变更即重新构建 |

## 命令行

入口：`python src`（或打包后的 `docserver-sync`）。**不提供**内置 HTTP 服务；预览与上线均由 Nginx、`http.server` 等托管 `-o` 目录。页面更新后由用户自行刷新浏览器。

| 长参数 | 短参数 | 说明 |
| --- | --- | --- |
| `--source` | `-s` | 源文档根目录（必填） |
| `--out` | `-o` | 构建产物目录（必填） |
| `--base-url` | | 子路径前缀，默认 `/` |
| `--site-url` | | 覆盖由 base-url 推导的 `site_url` |
| `--site-name` | | 站点标题，默认「文档」 |
| `--clean` | | 删除工作区中已不存在的同步文件 |
| `--verbose` | `-v` | 打印详细过程 |

| `--watch` | | 监视源目录并持续构建 |
| `--interval` | | 与 `--watch` 合用，轮询间隔（秒），默认 2 |
| `--skip-initial` | | 与 `--watch` 合用，跳过启动时首次构建 |

示例（仓库根）：

```bash
python src -s example/source -o dist
python src -s example/source -o dist --base-url /docs
python src -s example/source -o dist --watch --interval 2
```

本地查看：先构建或 `--watch` 生成 `dist`，再启动静态服务，例如：

```bash
python -m http.server 8000 --bind 127.0.0.1 --directory dist
```

修改源文件后等待 `--watch` 重建完成，在浏览器中手动刷新页面。

Unix：`bash example.sh`；Windows：`example.bat`。均为后台 `--watch` + 前台 `http.server`（无 `.venv` 时会自动创建并安装依赖）。

## 部署

将 `-o` 目录整体部署为静态站点。若使用 `--base-url /docs`，Web 服务器需把该路径映射到该目录，且构建时的 `site_url` 须与对外访问前缀一致（可用 `--site-url https://你的域名/docs/`）。

### 在线构建 + 离线运行（推荐内网）

| 环境 | 脚本 | 作用 |
| --- | --- | --- |
| **在线机**（Ubuntu 等，可访问 PyPI） | `build.sh` / `build.bat` | 安装依赖、示例构建、PyInstaller 打离线压缩包 |
| **离线机** | `run.sh`（由 `build.sh` 打的包）或 `run.bat`（由 `build.bat` 打的包） | 解压后编辑 `project.yaml`，运行 `run` 持续监视并重建静态站 |

在线机用 **`build.sh`** 得到 `release/docserver-offline-*.tar.gz`（含 `run.sh`）；用 **`build.bat`** 得到 `docserver-offline-win-amd64.zip`（含 `run.bat`）。二者均含 `release/bin/docserver-sync`、`project.yaml`、`theme/`（含本地 `mermaid.min.js`）、`cache/plugin/privacy/`（构建时缓存的外链脚本，内网重建不再访问外网）。编辑 `project.yaml` 后执行 `run`（`--watch`，Ctrl+C 结束）；Web 托管 `out` 目录即可。

### 开发机本地

- `update.bat` / `pip install -e ".[dev]"`：开发依赖（pytest）  
- `example.sh` / `example.bat`：`--watch` + `http.server` 预览  
- `python src`：见上文命令行表  

## 打包细节

`build.sh` / `build.bat` 内部调用 `tools/pack.sh`（PyInstaller；Linux 可选 staticx）。说明见 [PACKAGING.md](PACKAGING.md).
