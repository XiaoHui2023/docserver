docserver 离线运行包

一、构建静态站
  1. 解压到目标目录
  2. 编辑 run.sh 或 run.bat 顶部变量（SOURCE、OUT 等）
  3. 运行 run.sh 或 run.bat（持续监视并重建，Ctrl+C 结束）
  可执行文件：release/bin/docserver-sync（Windows 为 docserver-sync.exe）

二、浏览静态站（构建完成后）
  OUT 目录即为可部署的静态网站。任选一台有 Python 的机器，在 OUT 目录启动 HTTP 服务，例如：

  Linux / macOS：
    cd /path/to/OUT
    python3 -m http.server 8080

  Windows：
    cd \path\to\OUT
    py -3 -m http.server 8080

  浏览器打开 http://127.0.0.1:8080/ 即可预览。

三、文档入口（必读）
  源目录 SOURCE 的根下须有一份入口 Markdown（readme.md、README.md、index.md 等均可），
  构建后才会在 OUT 根目录生成 index.html。

  若根目录只有子文件夹、正文都在深层目录，访问网站根路径 / 将没有首页。
  请至少在文档根部放置一份入口文档。
