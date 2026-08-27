---
name: "usage-docs-generate"
description: "确认需要后生成当前版本产品使用文档和 manifest"
---

# usage-docs-generate

Use this skill when the user asks `/usage-docs-generate <version>` or wants to generate product usage docs for a release version.

## Bundled Resources

This project keeps `.agents/skills/*` lightweight: each project skill contains `SKILL.md` only, while deterministic implementation lives in top-level project scripts. This skill intentionally does not bundle its own `scripts/` directory; use:

```text
scripts/generate-usage-docs.py
scripts/validate-usage-docs.py
scripts/validate-release.py
```

## Input

- `<version>`：必填，例如 `v0.3.2`。
- Flags：`--force` 仅用于当前版本已确认需要重新生成时覆盖当前版本 `usage-docs/`。

## Must Read

```text
AGENTS.md
rules/document-governance.md
rules/directory-structure.md
rules/release.md
rules/security.md
releases/<version>/release.json
releases/templates/usage-docs/
```

## Gate

Before running generation, confirm `releases/<version>/release.json` contains:

```json
{
  "usage_docs": {
    "generation_decision": {
      "required": true,
      "confirmed_at": "YYYY-MM-DD HH:mm:ss",
      "confirmed_by": "operator",
      "rationale": "..."
    }
  }
}
```

If confirmation is missing, BLOCKED. Ask the user whether this release needs usage docs generation or update. Do not infer confirmation from user-visible changes alone.

## Steps

1. Validate release directory exists.
2. Confirm generation decision is explicit and timestamped.
3. Run:

```bash
python scripts/generate-usage-docs.py <version>
```

Generation MUST inherit the full page set from the previous generated usage-docs version when one exists. Treat template-only generation as valid only for the first version with usage docs, or when the user explicitly authorizes a page-set reset/removal.

Use `--force` only when regenerating current-version usage docs after explicit confirmation:

```bash
python scripts/generate-usage-docs.py <version> --force
```

4. Confirm `scripts/generate-usage-docs.py` projected the inherited full page set into `mintlify/docs/<version>/`, refreshed `mintlify/docs/latest/`, and updated `mintlify/docs.json`.
5. Add system screenshots before validation:
   - every generated `usage-docs/**/*.mdx` page MUST include at least one local screenshot;
   - screenshots MUST live under `mintlify/assets/screenshots/` using content-hash filenames, with release manifest references;
   - `releases/<version>/usage-docs/assets/` MUST NOT exist;
   - update `usage-docs/manifest.json screenshots[]` with `path=/assets/screenshots/<file>`, `site_asset`, covered pages, caption, source, source_type, content_hash, first_used_in, used_by_versions, covered_pages, and reuse_reason;
   - source_type MUST be `runtime_system`, `qa_system`, `accepted_system_evidence`, or `manual_system_capture`;
   - screenshots MUST come from the real running system, QA/acceptance real screenshots, or current-system manual captures;
   - BLOCKED if only product prototypes, design drafts, wireframes, Figma/HTML prototypes, or other non-system screenshots are available.
6. Run:

```bash
python scripts/validate-usage-docs.py --release-dir releases/<version>
python scripts/validate-release.py --release-dir releases/<version> --stage prepare
```

## Safety

- MUST NOT generate docs for old versions unless the user explicitly confirms current-version regeneration or authorized old-version maintenance.
- MUST NOT write secrets, real `.env` content, database connection strings, Authorization headers, Cookies, object storage credentials, production private domains, local absolute paths, or real customer data.
- MUST NOT create `usage-docs/` when user confirms docs are not needed; use `usage-docs-update` or skipped flow only as appropriate.
- MUST NOT leave generated usage docs as text-only pages; validation requires screenshot coverage for Web/Admin/media-facing pages.
- MUST NOT use product prototype images as usage-doc screenshots.
- MUST NOT use `mintlify/` as the only source of truth; release usage docs manifest remains the version fact source.

## Output

Report version, generated files, manifest path, release gate status, validation commands, blockers, and next release command.

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
