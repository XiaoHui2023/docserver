from __future__ import annotations

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
from pages import _format_pages_yaml, write_pages_files  # noqa: E402
from session_log import log_file_path  # noqa: E402
from scan import scan_source, scan_sources  # noqa: E402
from staging import sync_to_work  # noqa: E402
from watch import _changed_subrepos, _format_change_dirs  # noqa: E402


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

    def test_watch_change_dirs_by_subrepo(self) -> None:
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
            labels = _changed_subrepos(
                before, after, [source.resolve()], [source.resolve()]
            )
            self.assertEqual(labels, {"guides", "reference"})
            self.assertEqual(_format_change_dirs(labels), "guides、reference")

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
            labels = _changed_subrepos(before, after, [source.resolve()], roots)
            self.assertEqual(labels, {"(根目录)", "theme"})
            self.assertEqual(_format_change_dirs(labels), "theme、(根目录)")

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
