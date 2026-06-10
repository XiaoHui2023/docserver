# 打包辅助脚本

在线打包入口：**`tools/pack.sh`** / **`tools/pack.bat`**（用法与产物见各脚本文件头注释；staticx 等细节见 [PACKAGING.md](../PACKAGING.md)）。

本目录其余脚本由 `pack` 调用，一般无需单独执行：

| 脚本 | 作用 |
| --- | --- |
| `fetch-vendor.sh` / `.bat` | 拉取 `theme/vendor`（mermaid 等） |
| `stage-offline.sh` / `.bat` | 组装离线目录并打成压缩包 |
