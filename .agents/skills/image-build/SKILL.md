---
name: "image-build"
description: "基于发布镜像构建计划执行镜像构建并生成 manifest"
---

# image-build

Use this skill when the user asks `/image-build <version>` or wants to build release images and write image manifest evidence.

## ProjectSoulKing Adapter（MUST）

- ProjectSoulKing 当前为单 FastAPI 服务 + 静态 `app/static/`，默认镜像事实源为 `Dockerfile`、`docker-compose.yml`、`.env.example`、`app/`、`requirements.txt`。
- 如果 `releases/<version>/image-build-plan.json` 不存在或仍引用其他项目的双镜像路径、镜像 tag 变量或仓库名，MUST stop as BLOCKED，并要求先运行 `/image-prepare <version>` 生成 ProjectSoulKing 计划。
- 真实 `scripts/build-images.env` 可作为本地构建输入存在；不得复制或读取其内容到回复或 manifest。

## Context Budget Guardrails（MUST）

### Force-proceed Follow-up Guardrails（MUST）

- `force-proceed` 仅允许继续当前命令的非阻断部分，MUST NOT 默认自动创建 follow-up REQ/BUG；除非用户在当前命令中明确授权自动 capture，否则只输出标准 capture 文案，并明确“未自动创建 Issue”。
- 标准 capture 文案 MUST 分条包含：建议命令、类型倾向、标题、背景、影响范围、建议验收或复现要点、来源 Change/Sprint/命令；多个 follow-up 事项 MUST 逐条输出，且每条可独立用于后续 capture。
- 如用户明确授权并实际创建 follow-up Issue，MUST 按 `/req-capture`、`/bug-capture` 或 `/capture` 规则落盘，并运行对应 `req.capture` 或 `bug.capture` Workflow Sync。

- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接。
- 从 `releases/<version>/image-build-plan.json` 开始，只按 plan 的 `input_files` 定位必要上下文。
- MUST NOT 从本地 shell 环境猜测 release version、image tag、build args、release dir 或 tar name。
- MUST NOT 默认打印完整 Docker build logs、完整 tarball 内容、完整 manifest JSON、raw env 文件或 secrets。

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
releases/<version>/image-build-plan.json
scripts/build-images.sh
scripts/validate-image-build.py
```

## Gates

`/image-build` MUST:

- 读取有效 `releases/<version>/image-build-plan.json`。
- 缺少 plan、plan blocked、版本不匹配、input hash 漂移时拒绝构建。
- 复用 `scripts/build-images.sh` 执行单应用镜像构建、平台验证、应用依赖验证、tar 导出和 sha256 生成。
- 构建成功后生成或更新 `releases/<version>/image-manifest.json`。
- Docker、buildx、网络、基础镜像源、依赖安装、镜像验证、tar 导出或 checksum 失败时记录 blocker，不写成功 manifest。
- 不写入真实 `.env` 内容、密钥、数据库连接串、Authorization header、Cookie、真实客户数据或本机绝对路径。
- 真实本地 env 文件的存在不构成 build blocker；只有 Git-tracked env、未登记路径 env 或 env 内容泄露才阻断。

## Command

```bash
python scripts/validate-image-build.py validate-plan --release <version>
python scripts/validate-image-build.py build --release <version>
python scripts/validate-image-build.py validate-manifest --release <version>
```

## Output

Report compact summary only:

- version
- image_required
- plan path
- manifest path
- image tag
- tarball path
- blocker count
- validation summary
- next command: `/release-publish <version>` when release gates are ready

If the release will be installed or upgraded in an environment, also point to `/upgrade-plan --from <fresh|version> --to <version>` before publish support claims are finalized.

## AI Usage Post-command Hook（MUST）

After the command completes or records blockers, run:

```bash
python scripts/extract-ai-usage.py \
  --post-command-hook \
  --workflow-event image.build \
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
