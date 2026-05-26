from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from entries import dest_rel_for_source, entry_home_priority, is_entry_md  # noqa: E402
from paths import (  # noqa: E402
    DEFAULT_CACHE_DIR_NAME,
    NAV_META_NAME,
    resolve_cache_dir,
    validate_out_and_cache,
)
from pages import _format_pages_yaml, write_pages_files  # noqa: E402
from session_log import log_file_path  # noqa: E402
from scan import scan_source, scan_sources  # noqa: E402
from staging import sync_to_work  # noqa: E402
from watch import _format_changed_files, _snapshot, _watchable_source_file  # noqa: E402


class TestDocserver(unittest.TestCase):
    def test_entry_names(self) -> None:
        self.assertTrue(is_entry_md("README.md"))
        self.assertTrue(is_entry_md("index.MD"))
        self.assertFalse(is_entry_md("install.md"))

    def test_dest_readme_as_homepage(self) -> None:
        rel = Path("guides/README.md")
        self.assertEqual(
            dest_rel_for_source(rel, as_homepage=True),
            Path("guides/index.md"),
        )
        self.assertEqual(
            dest_rel_for_source(rel, as_homepage=False),
            Path("guides/README.md"),
        )

    def test_index_wins_homepage_readme_stays_page(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            src.mkdir()
            (src / "index.md").write_text("# Index\n", encoding="utf-8")
            (src / "README.md").write_text("# Readme\n", encoding="utf-8")
            entries = scan_source(src)
            by_dest = {e.dest_rel: e for e in entries}
            self.assertEqual(by_dest[Path("index.md")].rel_source, Path("index.md"))
            self.assertEqual(by_dest[Path("README.md")].rel_source, Path("README.md"))

    def test_readme_home_when_no_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            src.mkdir()
            (src / "readme.md").write_text("# a\n", encoding="utf-8")
            entries = scan_source(src)
            by_dest = {e.dest_rel: e for e in entries}
            self.assertEqual(by_dest[Path("index.md")].rel_source, Path("readme.md"))

    def test_readme_case_priority_order(self) -> None:
        self.assertLess(
            entry_home_priority("readme.md"),
            entry_home_priority("README.md"),
        )
        self.assertLess(
            entry_home_priority("index.md"),
            entry_home_priority("readme.md"),
        )

    def test_merge_sources_later_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "base"
            overlay = Path(tmp) / "overlay"
            base.mkdir()
            overlay.mkdir()
            (base / "index.md").write_text("# Base\n", encoding="utf-8")
            (base / "guides").mkdir()
            (base / "guides" / "a.md").write_text("# A base\n", encoding="utf-8")
            (overlay / "guides").mkdir()
            (overlay / "guides" / "a.md").write_text("# A overlay\n", encoding="utf-8")
            (overlay / "extra.md").write_text("# Extra\n", encoding="utf-8")
            entries = scan_sources([base, overlay])
            by_dest = {e.dest_rel: e for e in entries}
            self.assertEqual(
                by_dest[Path("index.md")].source_root.resolve(),
                base.resolve(),
            )
            self.assertIn("# A overlay", (overlay / "guides" / "a.md").read_text(encoding="utf-8"))
            work = Path(tmp) / "work"
            sync_to_work([base, overlay], work, verbose=False)
            self.assertIn(
                "# A overlay",
                (work / "docs" / "guides" / "a.md").read_text(encoding="utf-8"),
            )
            self.assertTrue((work / "docs" / "extra.md").is_file())

    def test_scan_example(self) -> None:
        source = ROOT / "example" / "source"
        entries = scan_source(source)
        links = {e.link for e in entries if e.is_markdown}
        self.assertIn("/", links)
        self.assertIn("/guides/install", links)
        self.assertIn("/guides/advanced/config", links)

    def test_remove_stale_without_clean_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            work = Path(tmp) / "work"
            src.mkdir()
            (src / "README.md").write_text("# Hi\n", encoding="utf-8")
            (src / "extra.md").write_text("# Extra\n", encoding="utf-8")
            sync_to_work(src, work, verbose=False)
            self.assertTrue((work / "docs" / "extra.md").is_file())
            (src / "extra.md").unlink()
            sync_to_work(src, work, clean=False, verbose=False)
            self.assertFalse((work / "docs" / "extra.md").exists())

    def test_static_asset_copied(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            src.mkdir()
            (src / "README.md").write_text("# Hi\n", encoding="utf-8")
            (src / "logo.png").write_bytes(b"\x89PNG")
            work = Path(tmp) / "work"
            sync_to_work(src, work, verbose=False)
            self.assertTrue((work / "docs" / "index.md").is_file())
            self.assertTrue((work / "docs" / "logo.png").is_file())

    def test_log_file_path_layout(self) -> None:
        from datetime import datetime

        path = log_file_path(Path("logs"), datetime(2026, 5, 25, 14, 30, 45))
        self.assertEqual(path, Path("logs/2026-05-25/14-30-45.log"))

    def test_pages_yaml_quotes_at_in_filename(self) -> None:
        text = _format_pages_yaml("分组", ["index.md", "a@b.md", "dir@name"])
        self.assertIn("'a@b.md'", text)
        self.assertIn("'dir@name'", text)
        import yaml

        parsed = yaml.safe_load(text)
        self.assertEqual(parsed["nav"], ["index.md", "a@b.md", "dir@name"])

    def test_pages_ignores_static_only_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            work = Path(tmp) / "work"
            src.mkdir()
            (src / "index.md").write_text("# Home\n", encoding="utf-8")
            for name in ("assets", "image", "media"):
                (src / name).mkdir()
                (src / name / "pic.png").write_bytes(b"\x89PNG")
            entries = sync_to_work(src, work, verbose=False)
            write_pages_files(work / "docs", entries)
            text = (work / "docs" / ".pages").read_text(encoding="utf-8")
            self.assertNotIn("assets", text)
            self.assertNotIn("image", text)
            self.assertNotIn("media", text)

    def test_nav_meta_index_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            work = Path(tmp) / "work"
            src.mkdir()
            (src / "index.md").write_text("# Home\n", encoding="utf-8")
            guides = src / "guides"
            guides.mkdir()
            (guides / "install.md").write_text("# Install\n", encoding="utf-8")
            adv = guides / "advanced"
            adv.mkdir()
            (adv / "index.md").write_text("# Advanced\n", encoding="utf-8")
            sync_to_work(src, work, verbose=False)
            meta_path = work / "docs" / "javascripts" / NAV_META_NAME
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            self.assertIn("/", meta["index_paths"])
            self.assertIn("/guides/advanced/", meta["index_paths"])
            self.assertNotIn("/guides/", meta["index_paths"])

    def test_sync_writes_pages(self) -> None:
        source = ROOT / "example" / "source"
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp) / "work"
            entries = sync_to_work(source, work, verbose=False)
            self.assertGreaterEqual(len(entries), 3)
            pages_root = work / "docs"
            self.assertTrue((pages_root / "index.md").is_file())
            count = write_pages_files(pages_root, entries)
            self.assertGreaterEqual(count, 1)
            self.assertTrue((pages_root / ".pages").is_file())

    def test_watch_change_files_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            source.mkdir()
            guides = source / "guides"
            ref = source / "reference"
            guides.mkdir()
            ref.mkdir()
            g_file = guides / "a.md"
            r_file = ref / "b.md"
            root_file = source / "index.md"
            g_file.write_text("a", encoding="utf-8")
            r_file.write_text("b", encoding="utf-8")
            root_file.write_text("c", encoding="utf-8")
            before = {
                g_file.resolve(): 1.0,
                r_file.resolve(): 1.0,
                root_file.resolve(): 1.0,
            }
            after = dict(before)
            after[g_file.resolve()] = 2.0
            after[r_file.resolve()] = 3.0
            lines = _format_changed_files(
                before, after, [source.resolve()], [source.resolve()]
            )
            self.assertEqual(
                lines,
                ["  [修改] guides/a.md", "  [修改] reference/b.md"],
            )

    def test_watch_change_files_truncated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            source.mkdir()
            before: dict[Path, float] = {}
            after: dict[Path, float] = {}
            for i in range(10):
                path = source / f"f{i}.md"
                path.write_text("x", encoding="utf-8")
                before[path.resolve()] = 1.0
                after[path.resolve()] = 2.0
            lines = _format_changed_files(
                before,
                after,
                [source.resolve()],
                [source.resolve()],
                limit=3,
            )
            self.assertEqual(len(lines), 4)
            self.assertTrue(all(line.startswith("  [修改] f") for line in lines[:3]))
            self.assertEqual(lines[-1], "  … 另有 7 个文件")

    def test_watch_change_root_and_engine(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            theme = Path(tmp) / "theme"
            source.mkdir()
            theme.mkdir()
            root_file = source / "readme.md"
            theme_file = theme / "x.css"
            root_file.write_text("r", encoding="utf-8")
            theme_file.write_text("t", encoding="utf-8")
            before = {root_file.resolve(): 1.0, theme_file.resolve(): 1.0}
            after = {root_file.resolve(): 2.0, theme_file.resolve(): 2.0}
            roots = [source.resolve(), theme.resolve()]
            lines = _format_changed_files(before, after, [source.resolve()], roots)
            self.assertEqual(
                lines,
                ["  [修改] readme.md", "  [修改] theme/x.css"],
            )

    def test_watchable_source_suffix(self) -> None:
        self.assertTrue(_watchable_source_file(Path("a.md")))
        self.assertTrue(_watchable_source_file(Path("b.PNG")))
        self.assertTrue(_watchable_source_file(Path("c.svg")))
        self.assertFalse(_watchable_source_file(Path("d.log")))
        self.assertFalse(_watchable_source_file(Path("e.tmp")))

    def test_watch_snapshot_skips_irrelevant_source_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            source.mkdir()
            md = source / "index.md"
            log = source / "debug.log"
            md.write_text("# x", encoding="utf-8")
            log.write_text("noise", encoding="utf-8")
            source_r = source.resolve()
            snap = _snapshot([source_r], source_roots={source_r})
            self.assertIn(md.resolve(), snap)
            self.assertNotIn(log.resolve(), snap)

    def test_watch_snapshot_includes_engine_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            theme = Path(tmp) / "theme"
            theme.mkdir()
            css = theme / "x.css"
            log = theme / "build.log"
            css.write_text("{}", encoding="utf-8")
            log.write_text("x", encoding="utf-8")
            theme_r = theme.resolve()
            snap = _snapshot([theme_r], source_roots=set())
            self.assertIn(css.resolve(), snap)
            self.assertIn(log.resolve(), snap)

    def test_watch_change_added_removed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            source.mkdir()
            kept = source / "kept.md"
            added = source / "new.md"
            removed = source / "gone.md"
            kept.write_text("k", encoding="utf-8")
            before = {kept.resolve(): 1.0, removed.resolve(): 1.0}
            after = {kept.resolve(): 2.0, added.resolve(): 1.0}
            lines = _format_changed_files(
                before, after, [source.resolve()], [source.resolve()]
            )
            self.assertEqual(
                lines,
                [
                    "  [删除] gone.md",
                    "  [修改] kept.md",
                    "  [新增] new.md",
                ],
            )

    def test_resolve_cache_dir_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path.cwd()
            try:
                import os

                os.chdir(tmp)
                self.assertEqual(
                    resolve_cache_dir(None),
                    (Path(tmp) / DEFAULT_CACHE_DIR_NAME).resolve(),
                )
                custom = Path(tmp) / "my-cache"
                self.assertEqual(resolve_cache_dir(custom), custom.resolve())
            finally:
                os.chdir(cwd)

    def test_validate_out_and_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "site"
            cache = Path(tmp) / "cache"
            out.mkdir()
            cache.mkdir()
            validate_out_and_cache(out, cache)
            with self.assertRaises(ValueError):
                validate_out_and_cache(out, out)
            nested_cache = out / "cache"
            nested_cache.mkdir()
            with self.assertRaises(ValueError):
                validate_out_and_cache(out, nested_cache)

    @patch("build_site.subprocess.run")
    @patch("build_site._run_mkdocs_inprocess")
    def test_frozen_mkdocs_inprocess(self, mock_inprocess, mock_run) -> None:
        import build_site

        with patch.object(build_site.sys, "frozen", True, create=True):
            build_site._run_mkdocs(Path("mkdocs.yml"), Path("out"), verbose=False)
        mock_inprocess.assert_called_once()
        mock_run.assert_not_called()

    @patch("build_site._run_mkdocs")
    def test_build_invokes_mkdocs(self, mock_mkdocs) -> None:
        from build_site import build_docs

        source = ROOT / "example" / "source"
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "site"
            count = build_docs(source, out, verbose=False)
            self.assertGreaterEqual(count, 3)
            mock_mkdocs.assert_called_once()


if __name__ == "__main__":
    unittest.main()
