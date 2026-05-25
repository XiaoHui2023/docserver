# 打包工具

## 一键打包（PyInstaller；Linux 再 staticx）

在仓库根执行（使用根目录 `.venv`，无则创建）：

```bash
./tools/pack.sh
```

默认构建同步工具入口。只打主入口时传入 `src`：

```bash
./tools/pack.sh src
```

Linux 另需系统安装 **patchelf**（如 `sudo apt install patchelf`）。产物写入 `dist/`：

| 目标 | 产物 |
| --- | --- |
| 主入口（src） | `docserver-sync` / `docserver-sync.exe` |
| 主入口（Linux，调试） | `docserver-sync-pyi`（仅 PyInstaller，staticx 前复制保留） |

Linux 上 `docserver-sync` 为 staticx 自解压包；同目录下的 `docserver-sync-pyi` 为未做 staticx 的 PyInstaller onefile，便于 staticx 失败时单独运行排查。Windows 无 staticx 步骤。**macOS** 当前脚本跳过 staticx，仅 PyInstaller 产物。

更完整的说明见仓库根目录 [PACKAGING.md](../PACKAGING.md)。
