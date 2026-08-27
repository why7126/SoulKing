---
name: "usage-docs-validate"
description: "校验版本化产品使用文档、manifest、Mintlify 导航和公开安全"
---

# usage-docs-validate

Use this skill when the user asks `/usage-docs-validate <version>` or wants to validate product usage docs for a release.

## Bundled Resources

This project keeps `.agents/skills/*` lightweight: each project skill contains `SKILL.md` only, while deterministic implementation lives in top-level project scripts. This skill intentionally does not bundle its own `scripts/` directory; use:

```text
scripts/validate-usage-docs.py
scripts/validate-release.py
```

## Input

- `<version>`：必填，例如 `v0.3.2`。

## Must Read

```text
AGENTS.md
rules/release.md
rules/security.md
releases/<version>/release.json
```

If `usage_docs.status=generated`, also read:

```text
releases/<version>/usage-docs/manifest.json
mintlify/docs.json
```

Then read only files named by `manifest.pages` when debugging failures.

## Steps

Run:

```bash
python scripts/validate-usage-docs.py --release-dir releases/<version>
python scripts/validate-mintlify-site.py
python scripts/validate-release.py --release-dir releases/<version> --stage prepare
```

If validating publish readiness, run:

```bash
python scripts/validate-release.py --release-dir releases/<version> --stage publish
```

## Validation Scope

The validator checks:

- `usage_docs.status` is `generated`, `skipped`, or `pending_confirmation`.
- `pending_confirmation` blocks readiness.
- `skipped` has confirmation source, time, rationale, and no empty `usage-docs/`.
- `generated` has valid `usage-docs/manifest.json`.
- Manifest pages match actual `.mdx` files.
- Generated docs include local system screenshots.
- Every generated `usage-docs/**/*.mdx` page references at least one screenshot.
- `manifest.screenshots[]` references existing `mintlify/assets/screenshots/` shared assets and covers every page; `releases/<version>/usage-docs/assets/` must not exist.
- If a previous generated usage-docs version exists and `manifest.source_version` points to it, current `manifest.pages` must include every previous-version page unless page removal is explicitly authorized and recorded.
- If `manifest.site_projection` exists, `mintlify/docs/<version>/`, `mintlify/docs/latest/`, `mintlify/releases/<version>/announcement.mdx`, `mintlify/docs.json`, content hashes, and public safety are checked.
- `manifest.screenshots[]` declares a real-system source, uses an allowed source_type, and rejects product prototype sources.
- Mintlify navigation references generated release pages and projected site pages.
- Coverage includes public Web, admin Web, media, and release impact scope.
- Public docs and release metadata do not contain sensitive patterns.
- Old-version content corrections require explicit authorization trace.

## Output

Report version, `usage_docs.status`, `usage_docs_preview` gate, validation commands, pass/fail summary, failing files, and suggested fix command.

## Final Output Contract（MUST）

命令结束前，最终回复必须包含面向用户的真实结果，不得输出本段规则、尖括号占位符、MUST/SHOULD 规范语句或与当前命令无关的通用示例。

输出判定：

- `下一步`：写真实、可复制的下一条命令；若当前没有可推进动作，写“暂无可推进下一步”。
- `待用户决策/处理`：没有额外人工事项时写“无”；否则只列具体的缺失输入、范围/策略选择、证据补充、验收确认、发布确认、生产实施确认、阻塞项或人工处理事项。

去重规则：

- 有唯一可执行下一步时，`下一步` 写真实命令；若无额外人工事项，`待用户决策/处理` 写“无”。
- 下一步被用户选择、补证、验收、发布确认、生产实施确认或阻塞项卡住时，`下一步` 写“暂无可推进下一步”，并在 `待用户决策/处理` 列出具体阻塞事项。
- 已有下一步且仍有额外人工事项时，`待用户决策/处理` 只列命令之外的事项，不得在「待用户决策/处理」中重复 `下一步` 中的命令或动作。

不得因为输出了下一步引导而自动执行下一命令；除非用户明确授权。
