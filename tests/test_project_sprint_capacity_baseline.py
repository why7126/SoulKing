from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_project_yaml_declares_default_sprint_capacity_baseline() -> None:
    content = (ROOT / "project.yaml").read_text(encoding="utf-8")

    assert "sprint_capacity:" in content
    assert "capacity_person_days: 30" in content
    assert "policy: default_baseline_for_new_sprints" in content


def test_current_capacity_governance_sprint_uses_project_baseline() -> None:
    content = (ROOT / "iterations/change/sprint-002/sprint.yaml").read_text(encoding="utf-8")

    assert "capacity_person_days: 30" in content
    assert "capacity_usage: 0.0667" in content
    assert "fix_buffer_person_days: 28" in content
    assert "fix_buffer_ratio: 0.9333" in content
