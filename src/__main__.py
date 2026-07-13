from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from build_site import build_docs
from session_log import session, set_log_level
from watch import watch_and_build


def _is_script_entry_token(token: str) -> bool:
    """是否为 ``python src`` / ``python …/__main__.py`` 的入口脚本参数。"""
    if token.endswith("__main__.py"):
        return True
    return Path(token).name == "src"


def _is_python_launcher(argv0: str) -> bool:
    name = Path(argv0).name.lower()
    return name in ("python", "python3", "python.exe", "python3.exe") or name.startswith(
        "python"
    )


def _normalize_argv(argv: list[str]) -> list[str]:
    """去掉 ``python src`` 脚本名与旧 ``build`` / ``watch`` 子命令。"""
    if not argv:
        return argv
    head, *rest = argv
    cleaned: list[str] = []
    want_watch = False
    # 仅去掉紧跟 python 的入口脚本名；勿把 -s 的源路径（如名为 src 的目录）删掉
    drop_entry = bool(rest) and _is_python_launcher(head) and _is_script_entry_token(rest[0])
    for token in rest[1:] if drop_entry else rest:
        if token in ("build", "watch"):
            if token == "watch":
                want_watch = True
            continue
        cleaned.append(token)
    if head in ("build", "watch"):
        if head == "watch":
            want_watch = True
        head = sys.executable or "docserver"
    elif head == "src" or _is_script_entry_token(head):
        head = sys.executable or "docserver"
    if want_watch and "--watch" not in cleaned:
        cleaned.insert(0, "--watch")
    return cleaned


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="docserver",
        description="将 Markdown 文档目录构建为可部署的静态站点（MkDocs Material）。",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-s",
        "--source",
        type=Path,
        nargs="+",
        required=True,
        metavar="DIR",
        help="源文档根目录，可多次指定；按顺序深合并，同路径后者覆盖前者",
    )
    parser.add_argument(
        "-o",
        "--out",
        type=Path,
        required=True,
        help="构建产物目录（可直接作为静态站点根目录部署）",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=None,
        metavar="DIR",
        help="构建缓存目录（含 docs/ 与 mkdocs.yml）；省略则在当前工作目录下使用 .docserver-cache",
    )
    parser.add_argument(
        "--base-url",
        default="/",
        help="站点子路径前缀，如 /docs/（默认 / 表示站点在域名根）",
    )
    parser.add_argument(
        "--site-url",
        default=None,
        help="完整 site_url（覆盖由 --base-url 推导的默认值）",
    )
    parser.add_argument(
        "--site-name",
        default="文档",
        help="站点标题",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="打印详细过程")
    parser.add_argument(
        "--watch",
        action="store_true",
        help="监视源目录与主题配置变更并持续重新构建",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=2.0,
        metavar="SEC",
        help="与 --watch 合用：轮询间隔（秒），默认 2",
    )
    parser.add_argument(
        "--settle",
        type=float,
        default=1.0,
        metavar="SEC",
        help="与 --watch 合用：检测到变更后等待稳定时间（秒），默认 1",
    )
    parser.add_argument(
        "--skip-initial",
        action="store_true",
        help="与 --watch 合用：跳过启动时首次构建",
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=None,
        metavar="DIR",
        help="将输出写入该目录下的 年-月-日/时-分-秒.log；省略则不写文件",
    )
    parser.add_argument(
        "--log-level",
        type=str.upper,
        choices=("DEBUG", "INFO"),
        default="INFO",
        help="日志等级，默认 INFO；DEBUG 输出 watch/构建耗时诊断",
    )
    return parser


def main() -> int:
    parser = _build_parser()
    argv = _normalize_argv(sys.argv)
    # staticx 打包时会无参数执行 onefile 以收集依赖，不能因缺少 -s/-o 非零退出。
    if len(argv) <= 1:
        parser.print_help()
        return 0
    args = parser.parse_args(argv)
    args.sources = [p.resolve() for p in args.source]
    args.out = args.out.resolve()
    if args.cache_dir is not None:
        args.cache_dir = args.cache_dir.resolve()
    if args.watch:
        return _run_watch(args)
    return _run_build(args)


def _run_build(args: argparse.Namespace) -> int:
    set_log_level(args.log_level)
    with session(args.log):
        try:
            build_docs(
                args.sources,
                args.out,
                cache_dir=args.cache_dir,
                base_url=args.base_url,
                site_url=args.site_url,
                site_name=args.site_name,
                verbose=args.verbose,
            )
        except (FileNotFoundError, ValueError) as exc:
            print(f"错误: {exc}", file=sys.stderr)
            return 1
        except subprocess.CalledProcessError as exc:
            print(f"构建失败: MkDocs 退出码 {exc.returncode}", file=sys.stderr)
            return 1
        except Exception as exc:
            print(f"构建失败: {exc}", file=sys.stderr)
            return 1
    return 0


def _run_watch(args: argparse.Namespace) -> int:
    set_log_level(args.log_level)
    with session(args.log):
        try:
            watch_and_build(
                args.sources,
                args.out,
                cache_dir=args.cache_dir,
                base_url=args.base_url,
                site_url=args.site_url,
                site_name=args.site_name,
                interval=args.interval,
                settle=args.settle,
                verbose=args.verbose,
                skip_initial=args.skip_initial,
            )
        except KeyboardInterrupt:
            print("\n已停止。")
            return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
