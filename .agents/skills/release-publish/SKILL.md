---
name: "release-publish"
description: "记录产品版本发布确认结果和最终公告位置"
created_at: "2026-07-02 14:56:58"
updated_at: "2026-08-03 23:10:00"
---

# release-publish

Use this skill when the user asks `/release-publish <version>` or wants to record the final release confirmation.

## Context Budget Guardrails（MUST）

### Force-proceed Follow-up Guardrails（MUST）

- `force-proceed` 仅允许继续当前命令的非阻断部分，MUST NOT 默认自动创建 follow-up REQ/BUG；除非用户在当前命令中明确授权自动 capture，否则只输出标准 capture 文案，并明确“未自动创建 Issue”。
- 标准 capture 文案 MUST 分条包含：建议命令、类型倾向、标题、背景、影响范围、建议验收或复现要点、来源 Change/Sprint/命令；多个 follow-up 事项 MUST 逐条输出，且每条可独立用于后续 capture。
- 如用户明确授权并实际创建 follow-up Issue，MUST 按 `/req-capture`、`/bug-capture` 或 `/capture` 规则落盘，并运行对应 `req.capture` 或 `bug.capture` Workflow Sync。

- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接，不重复全量读取。
- 从 `releases/<version>/release.json` 和 `announcement.mdx` 开始，按 validator/gate 报告定位问题。
- 不为发布确认全量展开关联 Sprint、Issue、Change；只有门禁证据缺失时读取对应片段。
- 输出聚焦发布结论、公告位置、门禁结果和回滚提醒。

## Input

- `<version>`：必填，例如 `v0.1.0`。
- Flags：`--announcement-url <url>`、`--published-at <YYYY-MM-DD HH:mm:ss>`、`--dry-run`、`--force`（仅用户明确确认时可用）。

## Must Read

```text
AGENTS.md
rules/document-governance.md
rules/directory-structure.md
rules/release.md
rules/security.md
rules/agent-context-budget.md
releases/<version>/release.json
releases/<version>/announcement.mdx
README.md
```

## Gates

Publish MUST be blocked unless:

- `python scripts/validate-release.py --release-dir releases/<version> --stage publish` exits `0`.
- Every required gate is `pass` or correctly justified as `na`.
- Formal-scope Changes are archived.
- Public announcement is safe for external publication.
- Product version mismatch has explicit rationale, or `PRODUCT_VERSION` equals `<version>`.
- Usage docs are either generated with validated `usage_docs_preview=pass`, or explicitly skipped with `usage_docs_preview=na`; `pending_confirmation` blocks publish.
- If `image_required=true` or offline image delivery is in scope, `releases/<version>/image-manifest.json` validates, or approved external build evidence is present.
- Manifest version, image tag, source plan, input hashes, tarball path, sidecar sha256, and actual tarball sha256 still match current release inputs.
- If announcement or release stable inputs changed after `/image-build`, publish MUST block and rerun `/image-prepare <version>` plus `/image-build <version>` before confirmation.
- If release metadata declares an upgrade path as supported, a validated `releases/<version>/upgrade-plans/<from>-to-<version>.json` MUST exist; missing or failed upgrade validation blocks support claims.
- User has supplied or confirmed the final announcement location if there is an external URL.
- Ignored, untracked local env files may exist and MUST NOT block publish by existence alone. Publish blocks only when real env files are Git-tracked, outside approved local env paths, or their contents appear in release, Mintlify, archive evidence, AI Usage, logs or replies.

### Anti-loop Rule（MUST）

`/release-publish` MUST be a confirmation-only command after image evidence exists:

- MUST NOT edit `releases/<version>/announcement.mdx` after a valid `image-manifest.json` exists.
- MUST NOT write the final tarball sha256, manifest sha256, published timestamp, or publish confirmation into `announcement.mdx`.
- Announcement text MUST refer to `releases/<version>/image-manifest.json` and the tarball `.sha256` sidecar as the source of truth for final image checksums when image delivery is in scope.
- Publish confirmation MUST be written only to `releases/<version>/release.json` under `publish_confirmation` or other non-stable publish metadata fields.
- If announcement content is stale, missing, unsafe, or needs copy edits, BLOCK publish and instruct the operator to update the announcement first, then rerun `/image-prepare <version>` and `/image-build <version>`. Do not repair announcement copy inside `/release-publish`.
- `release.json` gate evidence, `known_issues`, `publish_confirmation`, and other publish bookkeeping MUST NOT be treated as image stable input; scripts must continue to hash only stable release scope and input files.

`--force` MUST NOT bypass public-safety failures, missing `release.json` / `announcement.mdx`, usage docs pending confirmation, generated usage docs manifest/navigation/safety failures, skipped usage docs without rationale, missing image manifest for image-required releases, or stale image input hashes.

## Steps

1. Validate release metadata and announcement safety.
   - Include `python scripts/validate-usage-docs.py --release-dir releases/<version>` when `usage_docs.status` is `generated` or `skipped`.
   - Include `python scripts/validate-mintlify-site.py` when generated usage docs have been projected to `mintlify/`.
2. Validate image manifest when `image_required=true`:
   - `python scripts/validate-image-build.py validate-manifest --release <version>`
   - Confirm manifest `version`, `image_tag`, `source_plan`, `input_hashes`, tarball path, `.sha256` sidecar and actual tarball sha256 match current inputs.
   - Run `shasum -a 256 -c <tarball>.sha256` from the tarball directory and record the final sha from `image-manifest.json`.
   - If external build evidence is used, confirm evidence source, platform, digest or tarball sha256, validation method, owner confirmation and risk statement.
3. Validate upgrade plan evidence when the release claims a supported deployment path:
   - `python scripts/validate-release-upgrade.py validate-plan --plan releases/<version>/upgrade-plans/<from>-to-<version>.json`
   - Cross-version paths with `cross-version-upgrade-requires-manual-review` must remain a manual review claim, not a supported claim.
4. Confirm publish-time fields:
   - `release_time` / published time in `YYYY-MM-DD HH:mm:ss`
   - final announcement path or URL
   - rollback and known issues are present
5. Update only `releases/<version>/release.json` with publish confirmation fields if the existing schema already contains them, or append a conservative `publish_confirmation` object. Do not update `announcement.mdx` in this step:

```json
{
  "published_at": "YYYY-MM-DD HH:mm:ss",
  "announcement_url": "releases/vX.Y.Z/announcement.mdx",
  "confirmed_by": "operator",
  "notes": "发布确认说明。最终镜像 sha256 以 image-manifest.json 和 .sha256 sidecar 为准。"
}
```

6. Re-run validation. If validation reports image input drift caused by announcement changes, STOP and report that `/image-prepare <version>` and `/image-build <version>` must be rerun before publish.

## Output

Report version, publish status, announcement file/URL, validation command result, gate summary, updated files, and rollback reminder.

## Final Step — AI Usage Post-command Hook (MUST)

After publish confirmation is recorded or publish is blocked with a documented reason, run:

```bash
python scripts/extract-ai-usage.py \
  --post-command-hook \
  --workflow-event release.publish \
  --release <version> \
  [--release-sprint <sprint-id>] \
  [--sprint <sprint-id>] \
  [--req <REQ-id>] \
  [--bug <BUG-id>] \
  [--change <change-id>] \
  --json
```

- Pass Sprint / REQ / BUG / Change ids from `releases/<version>/release.json`.
- Pass `--release <version>` so the hook writes `data/ai-usage/command-runs/releases/<version>/release.publish.json`.
- Pass each release-scope Sprint with repeated `--release-sprint <sprint-id>`.
- If no Sprint is associated, omit `--sprint`; Sprint snapshot output MUST be `skipped`.
- Print only the compact hook summary: `status`, `usage_mode`, `command_run_count`, `session_input`, `release_artifact`, `sprint_snapshot`, `warning_count`, and `recommended_action`.
- If local session input is unavailable, report `usage_mode: unavailable` and the recommended action; do not treat that as parent command failure.

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
