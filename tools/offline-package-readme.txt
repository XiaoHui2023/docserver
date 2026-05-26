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

三、每层目录的首页（index / readme）
  每个目录可放 index 或 readme 类 Markdown（如 index.md、README.md，扩展名 .md，主文件名大小写不敏感）。

  同一目录内只选一个作该层首页，构建为 index.md（对应网页 index.html）：
    · 有 index 时：index 作首页；同目录的 readme 及其余 index 大小写变体保留原名，作为普通页面。
    · 无 index、仅有 readme 时：优先级最高的 readme 作首页；其余 readme 大小写变体保留原名，作为普通页面。
    · 优先级：index 类整体优于 readme 类；同类中 index 优于 Index 优于 INDEX；readme 优于 Readme 优于 README 等（大写字母越少越优先）。

  普通文档（如 install.md）始终按文件名原样参与构建。

四、文档根目录须有入口（必读）
  SOURCE 根下也须有一份入口 Markdown，构建后 OUT 根目录才有 index.html。

  若根目录只有子文件夹、正文都在深层目录，访问网站根路径 / 将没有首页。
  请至少在文档根部放置一份 index 或 readme 类入口文档。
