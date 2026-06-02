# docserver

将多层 Markdown 文档目录（含静态资源）构建为可部署的静态站点：左栏导航、右侧目录锚点、全文搜索、明/暗主题切换。基于 MkDocs Material，构建链仅需 Python。

## 设计概要

| 环节 | 说明 |
| --- | --- |
| 输入 | 一个或多个源目录（`-s` 可重复）；按顺序深合并，同相对路径后者覆盖前者 |
| 入口页 | 每层目录在 `index` / `readme`（多种大小写）中择一作首页 → `index.md`；同目录其余入口文件保留原名作为普通页面 |
| 导航 | 目录结构即站点结构；各层 `.pages` 控制侧栏顺序与分组标题（取自入口页一级标题） |
| 输出 | `-o` / `--out` 指向的目录即为静态站点根（含 `index.html`），可直接交给 Nginx / 对象存储 |
| 子路径 | `--base-url /xxx` 用于部署在 `https://域名/xxx/` 下；可用 `--site-url` 指定完整 canonical URL |
| 监视 | `--watch`：源目录内文档/静态资源相关后缀（如 `.md`、`.png`、`.svg`）变更即重新构建；`theme/`、`src/` 仍监视全部文件 |

## 命令行

入口：`python src`（或打包后的 `docserver-sync`）。**不提供**内置 HTTP 服务；预览与上线均由 Nginx、`http.server` 等托管 `-o` 目录。页面更新后由用户自行刷新浏览器。

| 长参数 | 短参数 | 说明 |
| --- | --- | --- |
| `--source` | `-s` | 源文档根目录，可写多次（必填） |
| `--out` | `-o` | 构建产物目录（必填） |
| `--cache-dir` | | 构建缓存目录；省略则在**当前工作目录**下使用 `.docserver-cache` |
| `--base-url` | | 子路径前缀，默认 `/` |
| `--site-url` | | 覆盖由 base-url 推导的 `site_url` |
| `--site-name` | | 站点标题，默认「文档」 |
| `--verbose` | `-v` | 打印详细过程 |
| `--watch` | | 监视源与引擎路径变更并持续构建；**启动时先完整构建一次** |
| `--interval` | | 与 `--watch` 合用，轮询间隔（秒），默认 2 |
| `--skip-initial` | | 与 `--watch` 合用，跳过启动时首次构建 |
| `--log` | | 日志目录；写入 `年-月-日/时-分-秒.log`，省略则不写文件 |

构建时 MkDocs 只写入 `{out}.staging/`，成功后再一次性替换 `{out}/`，构建过程中 `{out}/` 内容不变（便于持续预览与搜索）。

示例（仓库根）：

```bash
python src -s example/source -o dist
python src -s base/docs -s overlay -o dist
python src -s example/source -o dist --base-url /docs
python src -s example/source -o dist --watch --interval 2
python src -s example/source -o dist --watch --skip-initial
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
| **在线机**（Ubuntu 等，可访问 PyPI） | `build.sh` / `build.bat` | 安装依赖、拉取 theme vendor、PyInstaller 打离线压缩包 |
| **离线机** | `run.sh` / `run.bat` | 解压即用：默认构建包内 `demo/`，产物在 `output/site/` |

在线机用 **`build.sh`** 得到 `release/docserver-offline-*.tar.gz`（含 `run.sh`）；用 **`build.bat`** 得到 `docserver-offline-win-amd64.zip`（含 `run.bat`）。压缩包内含 `release/bin/docserver-sync`、`theme/`（含 `mermaid.min.js`）、`demo/` 示例源。解压后运行 `run` 即可（无需先改配置）。

**快速体验**

```bash
tar -xzf release/docserver-offline-*.tar.gz -C /path/to/docserver && cd /path/to/docserver
bash run.sh
cd output/site && python3 -m http.server 8080
# 浏览器 http://127.0.0.1:8080/
```

**`run.sh` / `run.bat` 顶部变量**

| 变量 | 默认 | 说明 |
| --- | --- | --- |
| `SOURCES` | `demo` | 源目录列表，多个按顺序合并 |
| `OUT` | `output/site` | 静态站点输出目录 |
| `WATCH` | `0` | `0` 只构建一次后退出；`1` 等同加 `--watch`（启动先构建一次，之后文件变更自动重建，Ctrl+C 结束） |
| `BASE_URL` | `/` | 对应 `--base-url` |
| `SITE_URL` | 空 | 对应 `--site-url` |
| `SITE_NAME` | `docserver 示例` | 对应 `--site-name` |
| `CACHE_DIR` | 空 | 对应 `--cache-dir`；空则用 `.docserver-cache/` |
| `LOG` | 空 | 对应 `--log` |

改用自有文档：把 `SOURCES` 改成你的 Markdown 根路径；日常编辑时设 `WATCH=1`。也可直接调用 `release/bin/docserver-sync`，参数与上表「命令行」一节相同。包内 `README.txt` 有更完整的子路径部署说明。

### 开发机本地

- `update.bat` / `pip install -e ".[dev]"`：开发依赖（pytest）  
- `example.sh` / `example.bat`：`--watch` + `http.server` 预览  
- `python src`：见上文命令行表  

## 打包细节

`build.sh` / `build.bat` 内部调用 `tools/pack.sh`（PyInstaller；Linux 可选 staticx）。说明见 [PACKAGING.md](PACKAGING.md).
