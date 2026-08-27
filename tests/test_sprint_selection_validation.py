from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate-sprint-selection.py"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_sprint_selection", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_sprint(root: Path, stage: str, sprint_id: str) -> None:
    path = root / "iterations" / stage / sprint_id
    path.mkdir(parents=True)
    (path / "sprint.yaml").write_text(f"sprint_id: {sprint_id}\n", encoding="utf-8")


def test_default_creates_next_when_no_active(tmp_path: Path) -> None:
    module = load_module()
    write_sprint(tmp_path, "archive", "sprint-001")
    inventory = module.collect_sprints(tmp_path)
    ok, message = module.validate_selection(None, inventory)
    assert ok is True
    assert inventory.next_id == "sprint-002"
    assert "默认创建 sprint-002" in message


def test_default_uses_single_active(tmp_path: Path) -> None:
    module = load_module()
    write_sprint(tmp_path, "change", "sprint-003")
    inventory = module.collect_sprints(tmp_path)
    ok, message = module.validate_selection(None, inventory)
    assert ok is True
    assert "默认使用当前 Sprint sprint-003" in message


def test_default_blocks_multiple_active(tmp_path: Path) -> None:
    module = load_module()
    write_sprint(tmp_path, "change", "sprint-003")
    write_sprint(tmp_path, "change", "sprint-004")
    inventory = module.collect_sprints(tmp_path)
    ok, message = module.validate_selection(None, inventory)
    assert ok is False
    assert "多个 active Sprint" in message


def test_new_sprint_must_be_sequential(tmp_path: Path) -> None:
    module = load_module()
    write_sprint(tmp_path, "archive", "sprint-005")
    inventory = module.collect_sprints(tmp_path)
    ok, message = module.validate_selection("sprint-007", inventory)
    assert ok is False
    assert "不得跳号创建 sprint-007" in message


def test_blocks_third_active_sprint(tmp_path: Path) -> None:
    module = load_module()
    write_sprint(tmp_path, "change", "sprint-005")
    write_sprint(tmp_path, "change", "sprint-006")
    inventory = module.collect_sprints(tmp_path)
    ok, message = module.validate_selection("sprint-007", inventory)
    assert ok is False
    assert "不得创建第三个 Sprint" in message
