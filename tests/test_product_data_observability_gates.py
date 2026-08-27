from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GATES_SCRIPT = ROOT / "scripts" / "validate-product-data-observability-gates.py"
STANDARD_SCRIPT = ROOT / "scripts" / "validate-product-data-observability-standard.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_entry_files(root: Path) -> None:
    required = [
        "AGENTS.md",
        "rules/api.md",
        "rules/database.md",
        "rules/testing.md",
        "rules/data-management.md",
        "rules/document-governance.md",
        "rules/requirement-management.md",
        "rules/iterations-lifecycle.md",
        ".agents/skills/req-generate/SKILL.md",
        ".agents/skills/req-complete/SKILL.md",
        ".agents/skills/req-review/SKILL.md",
        ".agents/skills/req-opsx/SKILL.md",
        ".agents/skills/opsx-propose/SKILL.md",
        ".agents/skills/opsx-apply/SKILL.md",
        ".agents/skills/opsx-modify/SKILL.md",
        ".agents/skills/opsx-archive/SKILL.md",
        ".agents/skills/sprint-propose/SKILL.md",
        ".agents/skills/sprint-apply/SKILL.md",
        ".agents/skills/sprint-archive/SKILL.md",
    ]
    text = (
        "docs/standards/product-data-collection-observability.md\n"
        "product_data_collection_observability\n"
        "affected_layers\n"
        "reason\n"
        "validation\n"
        "not_applicable\n"
    )
    for item in required:
        path = root / item
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def test_gate_blocks_triggered_change_without_declaration(tmp_path: Path) -> None:
    module = load_module(GATES_SCRIPT, "validate_product_data_observability_gates_missing")
    write_entry_files(tmp_path)
    change = tmp_path / "openspec/changes/add-play-log"
    change.mkdir(parents=True)
    (change / "proposal.md").write_text("新增播放 API 和 request_logs。", encoding="utf-8")

    code = module.main(["--root", str(tmp_path), "--change", "add-play-log"])
    assert code == 1


def test_gate_accepts_applicable_declaration(tmp_path: Path) -> None:
    module = load_module(GATES_SCRIPT, "validate_product_data_observability_gates_ok")
    write_entry_files(tmp_path)
    change = tmp_path / "openspec/changes/add-play-log"
    change.mkdir(parents=True)
    (change / "proposal.md").write_text(
        """
新增播放 API 和 request_logs。

```yaml
product_data_collection_observability:
  status: applicable
  affected_layers:
    - api
    - request_logs
  reason: 播放日志会写入请求日志。
  validation: 覆盖请求日志和脱敏验证。
```
""",
        encoding="utf-8",
    )

    code = module.main(["--root", str(tmp_path), "--change", "add-play-log"])
    assert code == 0


def test_gate_blocks_empty_na_reason(tmp_path: Path) -> None:
    module = load_module(GATES_SCRIPT, "validate_product_data_observability_gates_na")
    write_entry_files(tmp_path)
    change = tmp_path / "openspec/changes/update-api-doc"
    change.mkdir(parents=True)
    (change / "proposal.md").write_text(
        """
更新 API 文档。

```yaml
product_data_collection_observability:
  status: not_applicable
  affected_layers: []
  reason: 无
  validation: 已确认。
```
""",
        encoding="utf-8",
    )

    code = module.main(["--root", str(tmp_path), "--change", "update-api-doc"])
    assert code == 1


def test_standard_validator_reports_missing_terms(tmp_path: Path) -> None:
    module = load_module(STANDARD_SCRIPT, "validate_product_data_observability_standard")
    (tmp_path / "docs/standards").mkdir(parents=True)
    (tmp_path / "docs/standards/product-data-collection-observability.md").write_text("usage_events\n", encoding="utf-8")
    code = module.main.__globals__.update({"ROOT": tmp_path}) or module.main()
    assert code == 1
