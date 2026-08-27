---
name: "image-prepare"
description: "生成或校验发布镜像构建计划"
created_at: "2026-07-29 15:51:41"
updated_at: "2026-07-31 16:30:00"
---

# image-prepare

Use this skill when the user asks `/image-prepare <version>` or wants to prepare image build inputs for a release.

## ProjectSoulKing Adapter（MUST）

- ProjectSoulKing 当前为单 FastAPI 服务 + 静态 `app/static/`，镜像事实源为 `Dockerfile`、`docker-compose.yml`、`.env.example`、`app/`、`requirements.txt`。
- 本项目不存在其他项目的前后端双镜像、独立 Web Nginx 镜像或 MySQL schema 双栈；读取非 SoulKing 路径前 MUST 先判断是否存在，不存在时记录为 not applicable。
- 如果 `releases/<version>/release.json` 不存在，MUST stop as BLOCKED，并建议先运行 `/release-propose <version>`。

## Context Budget Guardrails（MUST）

### Force-proceed Follow-up Guardrails（MUST）

- `force-proceed` 仅允许继续当前命令的非阻断部分，MUST NOT 默认自动创建 follow-up REQ/BUG；除非用户在当前命令中明确授权自动 capture，否则只输出标准 capture 文案，并明确“未自动创建 Issue”。
- 标准 capture 文案 MUST 分条包含：建议命令、类型倾向、标题、背景、影响范围、建议验收或复现要点、来源 Change/Sprint/命令；多个 follow-up 事项 MUST 逐条输出，且每条可独立用于后续 capture。
- 如用户明确授权并实际创建 follow-up Issue，MUST 按 `/req-capture`、`/bug-capture` 或 `/capture` 规则落盘，并运行对应 `req.capture` 或 `bug.capture` Workflow Sync。

- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接。
- 从 `releases/<version>/release.json` 开始，只读取该版本关联的发布对象、构建输入和 validator 报告。
- MUST NOT 默认读取所有 `releases/**`、`openspec/archive/**`、generated OpenAPI client、完整 Docker logs 或 raw env 文件。
- 只读取 `scripts/build-images.env.example` 与安全摘要；真实 `scripts/build-images.env` 可作为本地构建输入存在，允许脚本维护安全白名单变量，但不得把敏感内容写入 plan 或回复。

## Input

- `<version>`：必填，例如 `v0.2.0`。
- Optional：`--env-file <path>` 指定本地构建 env；默认 `scripts/build-images.env`。

## Must Read

```text
AGENTS.md
rules/release.md
rules/security.md
rules/environment.md
rules/document-governance.md
rules/agent-context-budget.md
releases/<version>/release.json
scripts/build-images.env.example
scripts/validate-image-build.py
```

按 validator 报告分段读取：

```text
Dockerfile
docker-compose.yml
docker-compose.prod.yml
docker-compose.prod.external.yml
.env.example
app/models.py
app/database.py
docs/04-database-design.md
docs/08-production-image-release.md
```

## Gates

`/image-prepare` MUST:

- 读取 `releases/<version>/release.json`，缺失时阻断。
- 判断 `image_required`，或在发布对象缺少显式值时按 backend、database、docker、object storage 影响推断。
- 校验 `PRODUCT_VERSION`（如启用）、`SOULKING_IMAGE_TAG`、`IMAGE_BUILD_TAG`、Compose image 引用和构建 env 示例；默认构建 env 缺失或 `IMAGE_BUILD_TAG` 与发布版本不一致时，可以只自动创建/更新安全白名单变量并记录 `auto_actions`。
- 将 release 的稳定输入字段（版本、scope、impact、image 配置）、公告、Dockerfile、Compose、构建脚本、构建 env 示例、SQLAlchemy 模型/启动兼容迁移和数据库文档纳入 input hash；release gate evidence / prepare status 等可变发布元数据不得造成 plan hash drift。
- 生成或更新 `releases/<version>/image-build-plan.json`。
- Compose 中 `${SOULKING_IMAGE_TAG:-...}` 的 fallback 默认值不要求随每个 release 改动；当 fallback 与当前版本不同但实际发布 env 必须显式设置 `SOULKING_IMAGE_TAG=<version>` 时，记录 warning 而不是 blocker。
- Docker 不可用、网络不可用、构建 env 示例异常、自动修正后仍版本不一致或真实构建前置条件不满足时记录 blocker；不得伪造 pass 证据。
- 不写入真实 `.env` 内容、密钥、数据库连接串、Authorization header、Cookie、真实客户数据或本机绝对路径。
- 真实本地 env 文件的存在不构成 prepare blocker；只有 Git-tracked env、未登记路径 env 或 env 内容泄露才阻断。

## Command

```bash
python scripts/validate-image-build.py prepare --release <version>
python scripts/validate-image-build.py validate-plan --release <version>
```

## Output

Report compact summary only:

- version
- image_required
- plan path
- auto action count
- warning count
- blocker count
- key blockers
- next command: `/image-build <version>` when plan is unblocked and image delivery is required

## AI Usage Post-command Hook（MUST）

After the command completes or records blockers, run:

```bash
python scripts/extract-ai-usage.py \
  --post-command-hook \
  --workflow-event image.prepare \
  --release <version> \
  --json
```

Print only the compact hook summary.

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
