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

from entries import dest_rel_for_source, is_entry_md  # noqa: E402
from pages import _format_pages_yaml, write_pages_files  # noqa: E402
from scan import scan_source  # noqa: E402
from staging import sync_to_work  # noqa: E402


class TestDocserver(unittest.TestCase):
    def test_entry_names(self) -> None:
        self.assertTrue(is_entry_md("README.md"))
        self.assertTrue(is_entry_md("index.MD"))
        self.assertFalse(is_entry_md("install.md"))

    def test_dest_readme_to_index(self) -> None:
        rel = Path("guides/README.md")
        self.assertEqual(dest_rel_for_source(rel), Path("guides/index.md"))

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
