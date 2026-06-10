# 打包发布

在可访问 PyPI 的机器上于仓库根执行 **`./tools/pack.sh`** 或 **`tools\pack.bat`**：安装依赖、拉取 theme vendor、PyInstaller 打可执行文件，并组装离线压缩包。产物均在 **`dist/`**。

| 脚本 | 离线压缩包 | 启动器 |
| --- | --- | --- |
| `tools/pack.sh` | `dist/docserver-offline-*.tar.gz` | `run.sh` |
| `tools/pack.bat` | `dist/docserver-offline-win-amd64.zip` | `run.bat` |

压缩包内含 `dist/docserver-sync`、`theme/`（含 `mermaid.min.js`）、`demo/` 示例源。本机调试可直接运行 `dist/docserver-sync`（或 `.exe`）。

```bash
./tools/pack.sh
```

```bat
tools\pack.bat
```

打包产物内含 MkDocs Material 运行依赖，体积较大；若目标环境可联网，更推荐在目标机使用 `pip install -e .` 与 `python src`。

## Linux staticx

在 Linux 上，`tools/pack.sh` 对 ELF 产物再运行 **staticx**，需要系统已安装 **patchelf**（例如 `sudo apt install patchelf`）。**macOS** 当前跳过 staticx，仅保留 PyInstaller onefile。

staticx 之前会把 PyInstaller onefile **复制**为 `dist/docserver-sync-pyi` 并保留；最终发布用的 `dist/docserver-sync` 为 staticx 产物。若打包在 staticx 阶段失败，可先对 `-pyi` 文件单独运行、对照 `build/` 与 PyInstaller 日志，区分是 onefile 还是 staticx 的问题。

staticx 会**无参数**执行 onefile 以收集动态库；`docserver-sync` 在无 `-s`/`-o` 时打印帮助并以 0 退出，否则会报 `required: -s -o` 导致打包失败。

## Spec 文件

PyInstaller 规格放在仓库根目录：

- `docserver-cli.spec` → `docserver-sync`（内含 MkDocs Material 主题与插件的 `collect_all` / `copy_metadata`，避免 onefile 中 `theme: material` 不可用）

修改依赖或 `mkdocs.yml` 插件列表后须重新执行 `./tools/pack.sh` / `tools\pack.bat`。

## 兼容边界

单文件可执行文件的系统兼容性取决于**执行打包的那台机器**。要支持较旧的 Linux 发行版，应在 glibc 基线不高于目标环境的系统上构建，并在目标机实测 staticx 产物。
