from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scan import scan_source  # noqa: E402
from sidebar import build_sidebar  # noqa: E402
from sync import sync_docs  # noqa: E402


class TestDocSync(unittest.TestCase):
    def test_scan_example(self) -> None:
        source = ROOT / "example" / "source"
        entries = scan_source(source)
        links = {e.link for e in entries}
        self.assertIn("/", links)
        self.assertIn("/guides/install", links)
        self.assertIn("/guides/advanced/config", links)

    def test_sync_writes_sidebar(self) -> None:
        source = ROOT / "example" / "source"
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / ".vitepress").mkdir(parents=True)
            count = sync_docs(source, out, verbose=False)
            self.assertGreaterEqual(count, 3)
            sidebar_path = out / ".vitepress" / "sidebar.generated.json"
            self.assertTrue(sidebar_path.is_file())
            data = json.loads(sidebar_path.read_text(encoding="utf-8"))
            self.assertIsInstance(data, list)
            self.assertTrue(any(item.get("link") == "/" for item in data))

    def test_sidebar_nested(self) -> None:
        entries = scan_source(ROOT / "example" / "source")
        sidebar = build_sidebar(entries)
        texts = json.dumps(sidebar, ensure_ascii=False)
        self.assertIn("guides", texts)


if __name__ == "__main__":
    unittest.main()
