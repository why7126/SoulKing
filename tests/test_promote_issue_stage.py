from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location("promote_issue_stage", ROOT / "scripts/promote-issue-stage.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_find_archived_change_uses_canonical_archive_root(tmp_path: Path) -> None:
    module = load_module()
    archived = tmp_path / "openspec/archive/2026-08-31-update-example"
    archived.mkdir(parents=True)
    (archived / "trace.md").write_text("# trace\n", encoding="utf-8")

    assert module.find_archived_change(tmp_path, "update-example") == archived
