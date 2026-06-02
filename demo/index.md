# docserver 示例站点

离线包自带的简易文档。构建产物在 `output/site/`（可在 `run` 脚本里改 `OUT`）。

## 试用步骤

1. 解压离线压缩包，在包根目录执行 `bash run.sh` 或 `run.bat`（默认只构建一次）。
2. 进入 `OUT` 目录启动静态服务，例如：`python3 -m http.server 8080`
3. 浏览器打开 `http://127.0.0.1:8080/`

## 改用你的文档

编辑 `run.sh` / `run.bat` 顶部的 `SOURCES`，指向你的 Markdown 根目录（可写多个，按顺序合并）。需要改完自动重建时，将 `WATCH` 设为 `1`。
