docserver 离线运行包

零、快速体验（解压即用）
  1. 解压到任意目录
  2. 运行 run.sh（Linux/macOS）或 run.bat（Windows）
     默认使用包内 demo/ 作源，构建一次后退出，产物在 output/site/
  3. 预览（在 output/site 目录）：
       python3 -m http.server 8080
     浏览器打开 http://127.0.0.1:8080/

  改用自己的文档：编辑 run 顶部 SOURCES；需要保存文件后自动重建时设 WATCH=1。

一、run 脚本变量（对应 docserver-sync 参数）

  SOURCES     源文档根目录，可列多个（按顺序合并）
  OUT         静态站点输出目录
  CACHE_DIR   run.sh 的实例缓存目录；留空则按实例使用 .docserver-cache/<实例ID>/
  BASE_URL    子路径前缀，默认 /
  SITE_NAME   站点标题
  SITE_URL    完整 canonical URL；留空则由 BASE_URL 推导
  LOG         日志目录；留空不写日志文件
  LOG_LEVEL   日志等级；默认 INFO，排查 CPU 占用时可设 DEBUG
  INTERVAL    WATCH=1 时的轮询秒数；也作为失败/异常后的重试等待，默认 2
  DOCSERVER_INSTANCE  run.sh 实例名；留空时由 SOURCES/OUT/BASE_URL/SITE_NAME/SITE_URL 推导
  WATCH       0=只构建一次；1=持续监视并重建（等同 --watch，启动时先构建一次）

二、命令行参数（直接调用 dist/docserver-sync 时）

  必填：-s / --source（可多次）  -o / --out

  可选：
    --base-url          子路径，默认 /
    --site-url          覆盖 site_url
    --site-name         站点名
    --cache-dir         构建缓存目录
    --watch             监视变更并重建
    --interval N        与 --watch 合用，轮询秒数；也作为失败/异常后的重试等待，默认 2
    --skip-initial      与 --watch 合用，跳过启动时首次构建
    --log DIR           过程日志目录
    --log-level LEVEL   日志等级：INFO 或 DEBUG，默认 INFO
    -v / --verbose      详细输出

  示例（包根目录）：
    ./dist/docserver-sync -s demo -o output/site
    ./dist/docserver-sync -s demo -o output/site --watch
    ./dist/docserver-sync -s demo -o output/site --watch --interval 600 --log logs --log-level DEBUG

三、构建说明

  可执行文件：dist/docserver-sync（Windows 为 .exe）

  构建缓存：run.sh 默认 .docserver-cache/<实例ID>/；直接调用 dist/docserver-sync 且省略 --cache-dir 时默认 .docserver-cache/；
  OUT 仅为可部署静态站。

  构建时 MkDocs 写入缓存内 site-staging/；成功后再替换 OUT，
  构建过程中 OUT 内文件（含 search/）保持不变。除 OUT 与缓存外不生成其它目录。

四、BASE_URL 与 SITE_URL（子路径部署）

  BASE_URL（--base-url）
    站点 URL 前缀。默认 / 表示域名根。
    例：对外为 https://内网/note/ 时设 BASE_URL=/note/

  SITE_URL（--site-url）
    写入产物的完整站点 URL。留空时由 BASE_URL 推导（域名为 https://docs.local/）。
    上线地址与 docs.local 不一致时必须填写真实 URL。

  磁盘上 OUT 不会多出一层 note/；Web 服务器把 /note/ 映射到 OUT 根。

五、浏览静态站

  Linux / macOS：cd OUT && python3 -m http.server 8080
  Windows：cd OUT && py -3 -m http.server 8080

  子路径部署时勿仅用 http.server 根路径模拟 /note/，见第四节。

六、每层目录的首页（index / readme）

  每目录可放 index 或 readme 类 .md；同目录只选一个作首页（index 类优先于 readme 类）。
  其余入口变体保留原名作普通页。

七、文档根须有入口

  每个 SOURCES 目录根下须有一份入口 Markdown，否则站点根无 index.html。
