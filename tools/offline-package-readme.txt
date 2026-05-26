docserver 离线运行包

一、构建静态站
  1. 解压到目标目录
  2. 编辑 run.sh 或 run.bat 顶部变量（SOURCES、OUT、BASE_URL、SITE_URL 等）
  3. 运行 run.sh 或 run.bat（持续监视并重建，Ctrl+C 结束）
  可执行文件：release/bin/docserver-sync（Windows 为 docserver-sync.exe）

  构建缓存：默认在当前目录生成 .docserver-cache/（含中间 docs/、mkdocs.yml）；
  可在 run 脚本中设置 CACHE_DIR 指向其它目录。OUT 仅为可部署的静态站点。

  构建时会在 OUT 旁生成临时目录 OUT.staging/（如 dist.staging），MkDocs 只写入该目录；
  构建成功后将整目录一次性替换为 OUT，因此构建过程中 OUT 内文件（含 search/）保持不变。
  OUT.staging/、OUT.old/ 为过程目录，勿作部署或预览根目录。

二、BASE_URL 与 SITE_URL（子路径部署必读）

  run.sh / run.bat 中的变量对应命令行 --base-url、--site-url。

  BASE_URL（--base-url）
    含义：站点挂在域名下的哪一段路径（URL 前缀），不是磁盘上多建一层文件夹。
    默认：/  表示 https://域名/  即站点根。
    示例：对外地址为 https://内网服务器/note/  时，设 BASE_URL=/note/

  SITE_URL（--site-url）
    含义：写入构建产物的「正式站点地址」完整 URL（含 https:// 与末尾 /）。
    可省略：留空时由 BASE_URL 自动推导，域名为占位符 https://docs.local/
      · BASE_URL=/        → site_url 为 https://docs.local/
      · BASE_URL=/note/   → site_url 为 https://docs.local/note/
    何时要填：上线地址与 docs.local 不一致时，必须填写真实地址，例如：
      SITE_URL=https://wiki.company.com/note/

  这两个参数主要影响 HTML 里的 canonical 链接、sitemap.xml 中的 URL。
  内网自用、不做搜索引擎收录时，通常只配 BASE_URL 即可，SITE_URL 可留空。
  顶栏「分享」按钮复制的是浏览器当前地址，与 SITE_URL 基本无关。

  部署方式（重要）
    · 磁盘：OUT 目录内是 index.html、search/、guides/ 等，不会在 OUT 下再出现 note/ 子目录。
    · Web 服务器：把 URL 路径 /note/ 映射到 OUT 目录根。
      例：https://域名/note/  →  OUT/index.html
          https://域名/note/search/search_index.json  →  OUT/search/search_index.json
    · 全文搜索索引在 OUT/search/search_index.json（不是 OUT/note/search/）。

  配置示例
    站点在域名根：
      BASE_URL=/
      SITE_URL=                    （可留空，或填 https://wiki.company.com/）

    站点在 /note/ 子路径：
      BASE_URL=/note/
      SITE_URL=https://wiki.company.com/note/

  预览注意：用 python -m http.server 直接托管 OUT 时，默认只能模拟「域名根」
  （http://127.0.0.1:8080/）。若实际挂在 /note/，应用 Nginx 等按上表映射，
  或访问带 /note/ 前缀的地址；勿只开根路径却按子路径构建，否则链接与搜索可能异常。

三、浏览静态站（构建完成后）
  OUT 目录即为可部署的静态网站。任选一台有 Python 的机器，在 OUT 目录启动 HTTP 服务，例如：

  Linux / macOS：
    cd /path/to/OUT
    python3 -m http.server 8080

  Windows：
    cd \path\to\OUT
    py -3 -m http.server 8080

  浏览器打开 http://127.0.0.1:8080/ 即可预览（站点在子路径时见第二节）。

四、每层目录的首页（index / readme）
  每个目录可放 index 或 readme 类 Markdown（如 index.md、README.md，扩展名 .md，主文件名大小写不敏感）。

  同一目录内只选一个作该层首页，构建为 index.md（对应网页 index.html）：
    · 有 index 时：index 作首页；同目录的 readme 及其余 index 大小写变体保留原名，作为普通页面。
    · 无 index、仅有 readme 时：优先级最高的 readme 作首页；其余 readme 大小写变体保留原名，作为普通页面。
    · 优先级：index 类整体优于 readme 类；同类中 index 优于 Index 优于 INDEX；readme 优于 Readme 优于 README 等（大写字母越少越优先）。

  普通文档（如 install.md）始终按文件名原样参与构建。

五、文档根目录须有入口（必读）
  每个 SOURCES 条目（源目录）根下也须有一份入口 Markdown；至少有一个源目录在站点根提供入口，构建后 OUT 根目录才有 index.html。

  若根目录只有子文件夹、正文都在深层目录，访问网站根路径 / 将没有首页。
  请至少在文档根部放置一份 index 或 readme 类入口文档。
