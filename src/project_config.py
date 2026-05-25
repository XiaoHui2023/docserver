from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from paths import repo_root


@dataclass(frozen=True)
class ProjectConfig:
    source: Path
    out: Path
    base_url: str = "/"
    site_name: str = "文档"
    site_url: str | None = None


def find_project_yaml() -> Path | None:
    for base in (Path.cwd(), repo_root()):
        path = (base / "project.yaml").resolve()
        if path.is_file():
            return path
    return None


def load_project_yaml(path: Path) -> ProjectConfig:
    base = path.parent.resolve()
    fields: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, _, val = line.partition(":")
        fields[key.strip()] = val.strip().strip("\"'")

    raw_source = fields.get("source", "").strip()
    raw_out = fields.get("out", "").strip()
    if not raw_source or not raw_out:
        raise ValueError("project.yaml 须包含 source 与 out")

    def _resolve(p: str) -> Path:
        path = Path(p)
        return path if path.is_absolute() else (base / path)

    site_url = fields.get("site_url", "").strip() or None

    return ProjectConfig(
        source=_resolve(raw_source),
        out=_resolve(raw_out),
        base_url=fields.get("base_url", "/").strip() or "/",
        site_name=fields.get("site_name", "文档").strip() or "文档",
        site_url=site_url,
    )
