#!/usr/bin/env python3
"""Validate command skills follow Agent context budget guardrails."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / ".agents" / "skills"
REQUIRED_RULE = "rules/agent-context-budget.md"
COMMAND_SKILL_NAMES = {
    "capture",
    "explore",
    "initialize-project",
    "spec-opt",
    "spec-study",
}
COMMAND_SKILL_PREFIXES = (
    "bug-",
    "build-",
    "git-",
    "image-",
    "opsx-",
    "release-",
    "req-",
    "sprint-",
    "upgrade-",
)
NEXT_GUIDANCE_TERMS = (
    "下一步",
    "## Next",
    "Next:",
    "Next steps",
    "建议下一步",
)
USER_DECISION_TERMS = (
    "待用户决策",
    "待用户处理",
    "决策点",
    "用户决策",
)
NO_DUPLICATE_DECISION_TERMS = (
    "不得在「待用户决策/处理」中重复",
    "不得重复",
)
FINAL_CONTRACT_HEADING = "## Final Output Contract（MUST）"
OUTPUT_EXAMPLE_HEADING = "## Output Examples"
FORBIDDEN_FINAL_OUTPUT_CONTRACT_SNIPPETS = (
    "下一步：<可直接执行的命令",
    "- <需要用户选择",
    "- <仍需用户选择",
    "命令结束前，最终回复 MUST 明确包含",
    "命令结束前最终回复 MUST 明确包含",
    "MUST 给出可复制执行的命令，例如 `/bug-review BUG-0122`",
    "例如 `/bug-review BUG-0122`",
    "例如 /bug-review BUG-0122",
    "确认是否立即执行 /req-opsx",
    "确认是否立即执行 /bug-opsx",
)
REQUIRED_FINAL_OUTPUT_CONTRACT_SNIPPETS = (
    "不得输出本段规则、尖括号占位符、MUST/SHOULD 规范语句或与当前命令无关的通用示例",
    "输出判定",
    "暂无可推进下一步",
    "生产实施确认",
)
OUTPUT_EXAMPLE_NORMATIVE_LEAK_RE = re.compile(r"```text[\s\S]*?(?:MUST|SHOULD|Final Output Contract)[\s\S]*?```")
COMMAND_EXAMPLE_CONTRACTS = {
    "sprint-propose": (
        "/req-opsx REQ-0123-import-audio-metadata",
        "/bug-opsx BUG-0144-audio-upload-thumbnail-regression",
    ),
    "req-opsx": (
        "/opsx-apply REQ-0123-import-audio-metadata",
        "请选择目标 sprint-xxx",
        "请确认本需求拆分策略",
    ),
    "bug-opsx": (
        "/opsx-apply BUG-0144-audio-upload-thumbnail-regression",
        "请选择目标 sprint-xxx",
        "请补齐 confirmed 根因证据",
    ),
    "upgrade-plan": (
        "/upgrade-validate --plan releases/v1.2.0/upgrade-plans/v1.1.0-to-v1.2.0.json",
        "请复核中间版本 release 事实",
        "生产实施确认",
    ),
    "upgrade-validate": (
        "请确认是否按已校验计划执行生产升级",
        "请复核中间版本 release 事实",
        "生产实施确认",
    ),
}
SPRINT_BYPASS_PATTERNS = [
    re.compile(r"(?:non-REQ/BUG|无\s*REQ/BUG|纯治理|pure technical governance).*(?:may bypass|可豁免|可跳过|跳过).*(?:Sprint|sprint|迭代)"),
    re.compile(r"(?:Only|仅).*(?:non-REQ/BUG|无\s*REQ/BUG|纯治理|pure technical governance).*(?:bypass|豁免|跳过)"),
    re.compile(r"Sprint skipped\s*(?:可接受|is acceptable)"),
]
ISSUE_TARGET_CONTRACTS = {
    "req-review": {
        "required": ("/sprint-propose --req <REQ-full-id>", "/req-opsx <REQ-full-id>", "完整 `REQ-xxxx-slug`"),
        "forbidden": (),
    },
    "req-opsx": {
        "required": ("/opsx-apply <REQ-full-id>", "完整 `REQ-xxxx-slug`", "status: in_sprint"),
        "forbidden": ("/opsx-apply <REQ-id>", "/opsx-apply <change>", "/opsx-apply <change-id>"),
    },
    "bug-review": {
        "required": ("/sprint-propose --bug <BUG-full-id>", "/bug-opsx <BUG-full-id>", "完整 `BUG-xxxx-slug`"),
        "forbidden": (),
    },
    "bug-opsx": {
        "required": ("/opsx-apply <BUG-full-id>", "完整 `BUG-xxxx-slug`", "status: in_sprint"),
        "forbidden": ("/opsx-apply <BUG-id>", "/opsx-apply fix-", "/opsx-apply <change>", "/opsx-apply <change-id>"),
    },
    "opsx-apply": {
        "required": ("Target Resolution", "<REQ-full-id>", "<BUG-full-id>", "完整 `REQ-xxxx-slug`", "完整 `BUG-xxxx-slug`"),
        "forbidden": ("/opsx-archive <REQ-id>", "/opsx-archive <BUG-id>"),
    },
    "opsx-archive": {
        "required": ("Target Resolution", "<REQ-full-id>", "<BUG-full-id>", "完整 `REQ-xxxx-slug`", "完整 `BUG-xxxx-slug`"),
        "forbidden": (),
    },
}

# Patterns that are risky when written as a positive/default instruction.
BROAD_READ_PATTERNS = [
    re.compile(r"cat\s+rules/\*\.md"),
    re.compile(r"cat\s+docs/\*\*"),
    re.compile(r"cat\s+issues/\*\*"),
    re.compile(r"cat\s+iterations/\*\*"),
    re.compile(r"ls\s+-R"),
    re.compile(r"rg\s+[^\n]*\s\.\s*(?:$|[;&|])"),
]

LOCAL_PATH_PATTERNS = [
    re.compile(r"/Users/(?!<)[^/`\s]+/"),
    re.compile(r"/home/(?!<)[^/`\s]+/"),
    re.compile(r"/private/var/folders/"),
]

PRIVACY_SCAN_GLOBS = (
    "docs/spec-logs/**/*.md",
    "openspec/changes/**/proposal.md",
    "openspec/changes/**/design.md",
    "openspec/changes/**/tasks.md",
    "openspec/changes/**/trace.md",
)

NEGATION_HINTS = (
    "不要",
    "禁止",
    "不得",
    "MUST NOT",
    "must not",
    "Do not",
    "don't",
    "Don’t",
    "避免",
)

SUMMARY_REUSE_RULE_TERMS = ("规则和 Skill", "规则与 Skill", "rules and Skill", "rules and skills")
SUMMARY_REUSE_ACTION_TERMS = ("摘要承接", "摘要复用", "summary reuse", "reuse summaries")
FORCE_PROCEED_GUARDRAIL_TERMS = (
    "Force-proceed Follow-up Guardrails",
    "force-proceed",
    "MUST NOT 默认自动创建 follow-up REQ/BUG",
    "未自动创建 Issue",
)
FOLLOW_UP_CAPTURE_FIELD_TERMS = (
    "建议命令",
    "类型倾向",
    "标题",
    "背景",
    "影响范围",
    "建议验收或复现要点",
    "来源 Change/Sprint/命令",
)
FOLLOW_UP_AUTH_SYNC_TERMS = (
    "明确授权",
    "/req-capture",
    "/bug-capture",
    "/capture",
    "req.capture",
    "bug.capture",
    "Workflow Sync",
)


def is_negated(line: str) -> bool:
    return any(hint in line for hint in NEGATION_HINTS)


def extract_section(text: str, heading: str) -> str:
    start = text.find(heading)
    if start == -1:
        return ""
    next_heading = re.search(r"\n## (?!#)", text[start + len(heading) :])
    if not next_heading:
        return text[start:]
    end = start + len(heading) + next_heading.start()
    return text[start:end]


def validate_skill(path: Path) -> list[str]:
    rel = path.relative_to(ROOT)
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    if REQUIRED_RULE not in text:
        errors.append(f"{rel}: 缺少 `{REQUIRED_RULE}` 引用")

    if "Context Budget Guardrails" not in text:
        errors.append(f"{rel}: 缺少 Context Budget Guardrails 章节")

    if not has_summary_reuse_constraint(text):
        errors.append(f"{rel}: 缺少规则与 Skill 已读摘要复用约束")

    if not has_force_proceed_follow_up_guardrail(text):
        errors.append(f"{rel}: 缺少 force-proceed follow-up 不自动落盘门禁")

    if not has_follow_up_capture_fields(text):
        errors.append(f"{rel}: 缺少标准 follow-up capture 文案字段")

    if not has_follow_up_authorized_sync_rule(text):
        errors.append(f"{rel}: 缺少显式授权自动 capture 后的 Workflow Sync 约束")

    for lineno, line in enumerate(text.splitlines(), start=1):
        if is_negated(line):
            continue
        for pattern in BROAD_READ_PATTERNS:
            if pattern.search(line):
                errors.append(f"{rel}:{lineno}: 存在默认宽泛读取指令 `{line.strip()}`")
                break

    return errors


def validate_final_output_contract(path: Path) -> list[str]:
    rel = path.relative_to(ROOT)
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if not any(term in text for term in NEXT_GUIDANCE_TERMS):
        errors.append(f"{rel}: 缺少命令完成后的下一步引导")
    if not any(term in text for term in USER_DECISION_TERMS):
        errors.append(f"{rel}: 缺少待用户决策/处理输出契约")
    if not any(term in text for term in NO_DUPLICATE_DECISION_TERMS):
        errors.append(f"{rel}: 缺少下一步与待用户决策/处理去重约束")
    return errors


def validate_output_contract_hygiene(path: Path) -> list[str]:
    rel = path.relative_to(ROOT)
    name = path.parent.name
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    final_contract = extract_section(text, FINAL_CONTRACT_HEADING)
    if not final_contract:
        errors.append(f"{rel}: 缺少 Final Output Contract 章节")
        return errors

    for snippet in REQUIRED_FINAL_OUTPUT_CONTRACT_SNIPPETS:
        if snippet not in final_contract:
            errors.append(f"{rel}: Final Output Contract 缺少输出卫生约束 `{snippet}`")

    for snippet in FORBIDDEN_FINAL_OUTPUT_CONTRACT_SNIPPETS:
        if snippet in final_contract:
            errors.append(f"{rel}: Final Output Contract 残留易被原样输出的旧模板或通用示例 `{snippet}`")

    example_section = extract_section(text, OUTPUT_EXAMPLE_HEADING)
    if OUTPUT_EXAMPLE_NORMATIVE_LEAK_RE.search(example_section):
        errors.append(f"{rel}: Output Examples 的用户可见示例泄漏 MUST/SHOULD/Final Output Contract 规范语气")

    command_terms = COMMAND_EXAMPLE_CONTRACTS.get(name)
    if command_terms:
        for term in command_terms:
            if term.startswith("确认是否立即执行"):
                if term in text:
                    errors.append(f"{rel}: 存在重复要求确认下一步命令的反模式 `{term}`")
            elif term not in text:
                errors.append(f"{rel}: 缺少命令族专属输出示例 `{term}`")

    return errors


def validate_sprint_gate_no_bypass(path: Path) -> list[str]:
    rel = path.relative_to(ROOT)
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        if is_negated(line):
            continue
        for pattern in SPRINT_BYPASS_PATTERNS:
            if pattern.search(line):
                errors.append(f"{rel}:{lineno}: 存在非 REQ/BUG / 纯治理 Change 跳过 Sprint 门禁表述 `{line.strip()}`")
                break
    return errors


def validate_issue_target_contract(path: Path) -> list[str]:
    rel = path.relative_to(ROOT)
    name = path.parent.name
    contract = ISSUE_TARGET_CONTRACTS.get(name)
    if not contract:
        return []
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    for term in contract["required"]:
        if term not in text:
            errors.append(f"{rel}: 缺少下一步 REQ/BUG 参数规范 `{term}`")
    for term in contract["forbidden"]:
        if term in text:
            errors.append(f"{rel}: 存在下一步回退为 Change 参数的模板 `{term}`")
    return errors


def validate_privacy_paths() -> list[str]:
    errors: list[str] = []
    for glob in PRIVACY_SCAN_GLOBS:
        for path in ROOT.glob(glob):
            if not path.is_file():
                continue
            rel = path.relative_to(ROOT)
            text = path.read_text(encoding="utf-8")
            for lineno, line in enumerate(text.splitlines(), start=1):
                for pattern in LOCAL_PATH_PATTERNS:
                    if pattern.search(line):
                        errors.append(f"{rel}:{lineno}: 文档中存在未脱敏本机绝对路径")
                        break
    return errors


def has_summary_reuse_constraint(text: str) -> bool:
    has_scope = any(term in text for term in SUMMARY_REUSE_RULE_TERMS)
    has_action = any(term in text for term in SUMMARY_REUSE_ACTION_TERMS)
    return has_scope and has_action


def has_force_proceed_follow_up_guardrail(text: str) -> bool:
    return all(term in text for term in FORCE_PROCEED_GUARDRAIL_TERMS)


def has_follow_up_capture_fields(text: str) -> bool:
    return all(term in text for term in FOLLOW_UP_CAPTURE_FIELD_TERMS)


def has_follow_up_authorized_sync_rule(text: str) -> bool:
    return all(term in text for term in FOLLOW_UP_AUTH_SYNC_TERMS)


def is_command_skill(path: Path) -> bool:
    name = path.parent.name
    return name in COMMAND_SKILL_NAMES or name.startswith(COMMAND_SKILL_PREFIXES)


def main() -> int:
    all_skill_paths = sorted(SKILLS_DIR.glob("*/SKILL.md"))
    skill_paths = [path for path in all_skill_paths if is_command_skill(path)]
    if not all_skill_paths:
        print("未找到命令技能文件。", file=sys.stderr)
        return 1

    errors: list[str] = []
    for path in skill_paths:
        errors.extend(validate_skill(path))
    for path in all_skill_paths:
        errors.extend(validate_final_output_contract(path))
        errors.extend(validate_output_contract_hygiene(path))
        errors.extend(validate_sprint_gate_no_bypass(path))
        errors.extend(validate_issue_target_contract(path))
    errors.extend(validate_privacy_paths())

    if errors:
        print("Agent 上下文预算校验失败：")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"Agent 上下文预算校验通过：{len(skill_paths)} 个命令技能均已接入预算规则、"
        "摘要复用约束与 force-proceed follow-up 门禁；"
        f"{len(all_skill_paths)} 个技能均已接入下一步与待用户决策/处理输出契约及去重约束，"
        "未发现最终输出占位模板、通用 BUG 示例、重复诱因或规范语气泄漏风险，"
        "且未发现非 REQ/BUG / 纯治理 Change 跳过 Sprint 门禁表述、REQ/BUG 下一步参数回退或治理文档未脱敏本机路径。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
