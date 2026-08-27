from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_PROPOSE_SKILL = ROOT / ".agents/skills/sprint-propose/SKILL.md"
ITERATIONS_RULE = ROOT / "rules/iterations-lifecycle.md"
CAPACITY_SPEC = ROOT / "openspec/changes/tighten-soulking-sprint-capacity-governance/specs/governance-workflow-tooling/spec.md"
ADD_SCOPE_SCRIPT = ROOT / "scripts/add-sprint-scope-item.py"


def load_add_scope_module():
    spec = importlib.util.spec_from_file_location("add_sprint_scope_item", ADD_SCOPE_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_sprint_capacity_gate_is_documented_in_rule_skill_and_spec() -> None:
    rule = ITERATIONS_RULE.read_text(encoding="utf-8")
    skill = SPRINT_PROPOSE_SKILL.read_text(encoding="utf-8")
    spec = CAPACITY_SPEC.read_text(encoding="utf-8")

    for content in (rule, skill, spec):
        assert "estimated_person_days <= capacity_person_days" in content
        assert "capacity_person_days < estimated_person_days <= capacity_person_days * 1.2" in content
        assert "estimated_person_days > capacity_person_days * 1.2" in content
        assert "pass_with_risk" in content
        assert "blocked" in content


def test_sprint_yaml_template_includes_capacity_gate_fields() -> None:
    skill = SPRINT_PROPOSE_SKILL.read_text(encoding="utf-8")

    assert "capacity_person_days: <number>" in skill
    assert "capacity_usage: <number>" in skill
    assert "fix_buffer_person_days: <number>" in skill
    assert "fix_buffer_ratio: <number>" in skill
    assert "capacity_gate:" in skill


def test_add_scope_item_refreshes_capacity_gate_result_and_note() -> None:
    module = load_add_scope_module()
    lines = [
        "capacity_person_days: 10",
        "scope_estimates:",
        "  - id: first",
        "    story_points: 13",
        "    estimated_person_days: 13",
        "estimated_story_points: 0",
        "estimated_person_days: 0",
        "capacity_usage: 0",
        "fix_buffer_person_days: 0",
        "fix_buffer_ratio: 0",
        "capacity_gate:",
        "  capacity_person_days: 10",
        "  estimated_person_days: 0",
        "  capacity_usage: 0",
        "  result: pass",
        "  note: old",
    ]

    changed = module.update_capacity(lines)

    assert changed is True
    assert "estimated_person_days: 13" in lines
    assert "capacity_usage: 1.3" in lines
    assert "fix_buffer_person_days: 0" in lines
    assert "  result: blocked" in lines
    assert any("超过 120% 硬阻断阈值" in line for line in lines)

