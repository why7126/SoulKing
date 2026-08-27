from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate-root-cause-evidence.py"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_root_cause_evidence", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_require_confirmed_blocks_probable_root_cause(tmp_path: Path) -> None:
    module = load_module()
    root_cause = tmp_path / "root-cause.md"
    root_cause.write_text(
        "---\nroot_cause_status: probable\n---\n# 根因\n\n需要继续验证。\n",
        encoding="utf-8",
    )
    findings = module.validate_root_cause_file(root_cause, require_confirmed=True)
    assert any(item.level == "blocker" and "要求 root_cause_status 为 `confirmed`" in item.message for item in findings)


def test_require_confirmed_blocks_missing_root_cause_file(tmp_path: Path) -> None:
    module = load_module()
    findings = module.validate_root_cause_file(tmp_path / "root-cause.md", require_confirmed=True)
    assert findings[0].level == "blocker"


def test_confirmed_with_evidence_passes_require_confirmed(tmp_path: Path) -> None:
    module = load_module()
    root_cause = tmp_path / "root-cause.md"
    root_cause.write_text(
        "---\nroot_cause_status: confirmed\n---\n# 根因\n\n证据：pytest 覆盖复现和修复后回归。\n",
        encoding="utf-8",
    )
    findings = module.validate_root_cause_file(root_cause, require_confirmed=True)
    assert not [item for item in findings if item.level == "blocker"]


def test_default_mode_keeps_probable_as_non_blocking_warning(tmp_path: Path) -> None:
    module = load_module()
    root_cause = tmp_path / "root-cause.md"
    root_cause.write_text(
        "---\nroot_cause_status: probable\n---\n# 根因\n\n需要继续验证。\n",
        encoding="utf-8",
    )
    findings = module.validate_root_cause_file(root_cause)
    assert not [item for item in findings if item.level == "blocker"]
