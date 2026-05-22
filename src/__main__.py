from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sync import sync_docs
from watch import serve_watch


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="docserver-sync",
        description="将 Markdown 文档目录同步到 VitePress 站点根目录，并可监视源目录持续更新。",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "-S",
        "--source",
        type=Path,
        required=True,
        help="源文档根目录（可含多层子目录）",
    )
    common.add_argument(
        "-O",
        "--out",
        type=Path,
        required=True,
        help="VitePress 项目根目录（含 .vitepress 与 package.json）",
    )
    common.add_argument("-v", "--verbose", action="store_true", help="打印每个同步文件")
    common.add_argument(
        "--clean",
        action="store_true",
        help="删除上次同步写入、本次已不存在的 Markdown",
    )

    sync_p = sub.add_parser("sync", parents=[common], help="同步一次")
    sync_p.set_defaults(func=_cmd_sync)

    serve_p = sub.add_parser("serve", parents=[common], help="监视源目录并持续同步")
    serve_p.add_argument(
        "--interval",
        type=float,
        default=2.0,
        help="轮询间隔（秒）",
    )
    serve_p.set_defaults(func=_cmd_serve)

    return parser


def _cmd_sync(args: argparse.Namespace) -> int:
    try:
        count = sync_docs(args.source, args.out, clean=args.clean, verbose=args.verbose)
    except (FileNotFoundError, ValueError) as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1
    print(f"已同步 {count} 个页面到 {args.out.resolve()}")
    return 0


def _cmd_serve(args: argparse.Namespace) -> int:
    try:
        serve_watch(
            args.source,
            args.out,
            interval=args.interval,
            clean=args.clean,
            verbose=args.verbose,
        )
    except KeyboardInterrupt:
        print("\n已停止监视。")
        return 0
    except (FileNotFoundError, ValueError) as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
