# 打包发布

在可访问 PyPI 的机器上于仓库根执行一键脚本；Linux 上会在 PyInstaller onefile 之后再做 staticx，得到更易在旧 glibc 环境运行的自解压单文件。

打包产物内含 MkDocs Material 运行依赖，体积较大；若目标环境可联网，更推荐在目标机使用 `pip install -e .` 与 `python src`。

## 一键打包

```bash
./tools/pack.sh
```

脚本会创建或复用根目录 `.venv`，执行 `pip install -e .` 安装项目，再调用 PyInstaller。参数与单入口说明见 [tools/README.md](tools/README.md)。

| 命令 | 产物（`dist/`） |
| --- | --- |
| `./tools/pack.sh` 或 `all` | `docserver-sync` |
| `./tools/pack.sh src` | `docserver-sync` |

Windows 产物为 `docserver-sync.exe`，无 staticx 步骤。

## Linux staticx

在 Linux 上，`tools/pack.sh` 对 ELF 产物再运行 **staticx**，需要系统已安装 **patchelf**（例如 `sudo apt install patchelf`）。**macOS** 当前跳过 staticx，仅保留 PyInstaller onefile。

staticx 会**无参数**执行 onefile 以收集动态库；`docserver-sync` 在无 `-s`/`-o` 时打印帮助并以 0 退出，否则会报 `required: -s -o` 导致打包失败。

## Spec 文件

PyInstaller 规格放在仓库根目录：

- `docserver-cli.spec` → `docserver-sync`

## 兼容边界

单文件可执行文件的系统兼容性取决于**执行打包的那台机器**。要支持较旧的 Linux 发行版，应在 glibc 基线不高于目标环境的系统上构建，并在目标机实测 staticx 产物。
