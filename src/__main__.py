from __future__ import annotations

import argparse
import sys
from pathlib import Path

from build_site import build_docs
from watch import watch_and_build


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="docserver",
        description="将 Markdown 文档目录构建为可部署的静态站点（MkDocs Material）。",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "-S",
        "--source",
        type=Path,
        required=True,
        help="源文档根目录（含 Markdown 与静态资源）",
    )
    common.add_argument(
        "-O",
        "--out",
        type=Path,
        required=True,
        help="构建产物目录（可直接作为静态站点根目录部署）",
    )
    common.add_argument(
        "--base-url",
        default="/",
        help="站点子路径前缀，如 /docs/（默认 / 表示站点在域名根）",
    )
    common.add_argument(
        "--site-url",
        default=None,
        help="完整 site_url（覆盖由 --base-url 推导的默认值）",
    )
    common.add_argument(
        "--site-name",
        default="文档",
        help="站点标题",
    )
    common.add_argument("-v", "--verbose", action="store_true", help="打印详细过程")
    common.add_argument(
        "--clean",
        action="store_true",
        help="删除工作区中上次同步、本次已不存在的文件",
    )

    build_p = sub.add_parser("build", parents=[common], help="构建一次")
    build_p.set_defaults(func=_cmd_build)

    watch_p = sub.add_parser(
        "watch",
        parents=[common],
        help="监视源目录变更并重新构建",
    )
    watch_p.add_argument(
        "--interval",
        type=float,
        default=2.0,
        help="轮询间隔（秒）",
    )
    watch_p.set_defaults(func=_cmd_watch)

    return parser


def _cmd_build(args: argparse.Namespace) -> int:
    try:
        count = build_docs(
            args.source,
            args.out,
            base_url=args.base_url,
            site_url=args.site_url,
            site_name=args.site_name,
            clean=args.clean,
            verbose=args.verbose,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"构建失败: {exc}", file=sys.stderr)
        return 1
    print(f"已构建 {count} 个页面到 {args.out.resolve()}")
    return 0


def _cmd_watch(args: argparse.Namespace) -> int:
    try:
        watch_and_build(
            args.source,
            args.out,
            base_url=args.base_url,
            site_url=args.site_url,
            site_name=args.site_name,
            interval=args.interval,
            clean=args.clean,
            verbose=args.verbose,
        )
    except KeyboardInterrupt:
        print("\n已停止。")
        return 0
    except (FileNotFoundError, ValueError) as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"构建失败: {exc}", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
