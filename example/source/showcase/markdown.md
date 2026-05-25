# Markdown 排版演示

本页故意写长，便于观察**右侧本页目录**与**返回顶部**按钮。

## 提示框（Admonition）

!!! note "说明"
    这是一般说明，适合补充背景信息。

!!! tip "提示"
    可操作建议：构建后检查 `dist/index.html` 是否存在。

!!! warning "注意"
    子路径部署时，`site_url` 必须与对外 URL 一致，否则站内链接可能错位。

!!! success "完成"
    构建成功时终端会输出页面数量。

## 折叠详情

??? question "为什么入口可以是 README？"
    docserver 在同步阶段会把 `readme` / `index` 规范为 `index.md`，
    与 Git 仓库习惯兼容，同时满足 MkDocs 目录首页约定。

## 标签页

=== "Windows"

    ```bat
    example.bat
    ```

=== "Linux / macOS"

    ```bash
    python src -s example/source -o dist --watch
    ```

=== "仅构建"

    ```bash
    python src -s example/source -o dist
    ```

## 表格

| 列 | 类型 | 说明 |
| --- | --- | --- |
| `-s` | 路径 | 源文档根 |
| `-o` | 路径 | 输出静态站根 |
| `--base-url` | 文本 | 子路径前缀，如 `/docs` |

## 代码与行内代码

行内：`'use_directory_urls: true'`。

```python
from build_site import build_docs

build_docs(
    Path("example/source"),
    Path("dist"),
    base_url="/",
    verbose=True,
)
```

点击代码块右上角可复制。

## 二级标题锚点

点击右侧「本页内容」会平滑滚动到对应小节（已关闭标题旁的 ¶ 永久链接）。

### 三级标题示例

再深一层仍会出现在右侧目录中。

### 另一个三级标题

用于拉长页面，方便滚动时观察 **toc.follow**（目录高亮跟随）。

## 列表

- 无序项 A
- 无序项 B
  - 嵌套 B.1
  - 嵌套 B.2

1. 有序步骤一
2. 有序步骤二
3. 有序步骤三

> 引用块：适合摘录规范或外部说明。

## 分隔线以下

更多内容用于撑开页面高度。

---

附录：若你看到本段，说明已滚到页底，可点击右上角 **回到顶部**。
