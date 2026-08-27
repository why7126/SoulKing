#!/usr/bin/env python3
"""Validate ProjectSoulKing harness directory structure."""

from fnmatch import fnmatch
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

IGNORED_LOCAL_ENV_FILE_PATTERNS = {
    ".env",
    ".env.*",
    "deploy/local/*.env",
    "deploy/prod/*.env",
    "scripts/build-images.env",
}

GITIGNORE_REQUIRED_PATTERNS = {
    ".env",
    ".env.*",
    "scripts/build-images.env",
    "deploy/local/*.env",
    "deploy/prod/*.env",
}

EXPECTED_AGENT_SKILLS = {
    "bug-capture",
    "bug-complete",
    "bug-explore",
    "bug-generate",
    "bug-opsx",
    "bug-review",
    "build-api-standard",
    "build-design-system",
    "build-test-framework",
    "capture",
    "explore",
    "git-check",
    "image-build",
    "image-prepare",
    "initialize-project",
    "miniapp-check",
    "miniapp-confirm",
    "miniapp-env",
    "miniapp-prepare",
    "miniapp-restore",
    "openspec-apply-change",
    "openspec-archive-change",
    "openspec-explore",
    "openspec-propose",
    "opsx-apply",
    "opsx-archive",
    "opsx-explore",
    "opsx-modify",
    "opsx-propose",
    "release-prepare",
    "release-propose",
    "release-publish",
    "req-capture",
    "req-complete",
    "req-explore",
    "req-generate",
    "req-opsx",
    "req-review",
    "spec-opt",
    "spec-study",
    "sprint-apply",
    "sprint-archive",
    "sprint-explore",
    "sprint-exps",
    "sprint-propose",
    "upgrade-plan",
    "upgrade-validate",
    "usage-docs-generate",
    "usage-docs-update",
    "usage-docs-validate",
    "workflow-sync",
}

REQUIRED_PATHS = [
    "AGENTS.md",
    "README.md",
    "project.yaml",
    "DOCUMENT_METADATA_INDEX.md",
    ".env.example",
    "Dockerfile",
    "docker-compose.yml",
    "package.json",
    "requirements.txt",
    "ui-design.md",
    "rules/global.md",
    "rules/language.md",
    "rules/agent-context-budget.md",
    "rules/directory-structure.md",
    "rules/issues-lifecycle.md",
    "rules/iterations-lifecycle.md",
    "rules/testing.md",
    "issues/requirements/_registry.yaml",
    "issues/bugs/_registry.yaml",
    "docs/README.md",
    "docs/00-product-overview.md",
    "docs/01-architecture.md",
    "docs/02-deployment.md",
    "docs/03-api-index.md",
    "docs/04-database-design.md",
    "docs/05-compatibility-matrix.md",
    "docs/07-object-storage-strategy.md",
    "deploy/README.md",
    "deploy/local/README.md",
    "deploy/local/compose.yml",
    "deploy/local/sqlite-minio-external.env.example",
    "deploy/local/sqlite-minio-managed.env.example",
    "deploy/prod/README.md",
    "deploy/prod/compose.sqlite-minio-external.yml",
    "deploy/prod/sqlite-minio-external.env.example",
    "deploy/scripts/up.sh",
    "deploy/scripts/down.sh",
    "deploy/scripts/validate-env.py",
    "deploy/scripts/docs-site-static-server.mjs",
    "docs/knowledge-base/README.md",
    "openspec/project.md",
    "openspec/config.yaml",
    "openspec/testing-mapping.md",
    ".agents/skills/capture/SKILL.md",
    ".agents/skills/explore/SKILL.md",
    ".agents/skills/git-check/SKILL.md",
    ".agents/skills/req-capture/SKILL.md",
    ".agents/skills/bug-capture/SKILL.md",
    ".agents/skills/sprint-propose/SKILL.md",
    ".agents/skills/opsx-propose/SKILL.md",
    ".agents/skills/opsx-modify/SKILL.md",
    ".agents/skills/spec-opt/SKILL.md",
    ".agents/skills/spec-study/SKILL.md",
    ".agents/skills/upgrade-plan/SKILL.md",
    ".agents/skills/upgrade-validate/SKILL.md",
    ".agents/skills/usage-docs-generate/SKILL.md",
    ".agents/skills/usage-docs-update/SKILL.md",
    ".agents/skills/usage-docs-validate/SKILL.md",
    "scripts/promote-issue-stage.py",
    "scripts/promote-issues-for-archive.py",
    "scripts/sync-workflow-status.py",
    "scripts/ai_usage.py",
    "scripts/extract-ai-usage.py",
    "scripts/archive-change.sh",
    "scripts/archive_evidence.py",
    "scripts/add-sprint-scope-item.py",
    "scripts/generate-sprint-fact-sheet.py",
    "scripts/docker-up.sh",
    "scripts/docker-down.sh",
    "scripts/validate-agent-context-budget.py",
    "scripts/validate-api-standard.py",
    "scripts/validate-archive-evidence.py",
    "scripts/validate-design-system.py",
    "scripts/validate-openspec-language.py",
    "scripts/validate-openspec.sh",
    "scripts/validate-sprint-archive-readiness.py",
    "scripts/validate-sprint-scope.py",
    "scripts/check-sprint-close-stale-scan.py",
    "scripts/sprint_close_stale_scan.py",
    "scripts/validate-test-framework.py",
    "releases/README.md",
    "releases/templates/release.json",
    "releases/templates/announcement.mdx",
    "releases/templates/usage-docs/overview.mdx",
    "releases/templates/usage-docs/web/index.mdx",
    "releases/templates/usage-docs/admin/index.mdx",
    "releases/templates/usage-docs/faq.mdx",
    "mintlify/README.md",
    "mintlify/docs.json",
    "mintlify/site-manifest.json",
    "scripts/generate-usage-docs.py",
    "scripts/validate-usage-docs.py",
    "scripts/validate-mintlify-site.py",
    "scripts/validate-directory-structure.py",
    "scripts/validate-generated-docs.py",
    "scripts/validate-doc-governance.py",
    "scripts/validate-release-upgrade.py",
    "scripts/validate-root-cause-evidence.py",
]

REQUIRED_DIRS = [
    ".agents",
    ".agents/skills",
    "app",
    "app/static",
    "rules",
    "docs",
    "docs/standards",
    "docs/knowledge-base",
    "docs/knowledge-base/best-practices",
    "docs/knowledge-base/incidents",
    "docs/knowledge-base/sprints",
    "docs/spec-logs",
    "compatibility",
    "compatibility/database",
    "compatibility/devices",
    "compatibility/object-storage",
    "openspec",
    "openspec/specs",
    "openspec/changes",
    "openspec/archive",
    "issues",
    "issues/requirements",
    "issues/requirements/plan",
    "issues/requirements/review",
    "issues/requirements/archive",
    "issues/bugs",
    "issues/bugs/plan",
    "issues/bugs/review",
    "issues/bugs/archive",
    "iterations",
    "iterations/change",
    "iterations/archive",
    "scripts",
    "tests",
    "tests/unit",
    "tests/integration",
    "tests/integration/api",
    "tests/e2e",
    "tests/compatibility",
    "data",
    "import",
    "packaging",
    "releases",
    "releases/templates",
    "releases/templates/usage-docs",
    "releases/templates/usage-docs/web",
    "releases/templates/usage-docs/admin",
    "deploy",
    "deploy/local",
    "deploy/prod",
    "deploy/scripts",
    "mintlify",
    "mintlify/docs",
    "mintlify/releases",
    "mintlify/assets",
    "mintlify/assets/screenshots",
    "models",
]

ALLOWED_ROOT_FILES = {
    ".DS_Store",
    ".env",
    ".env.example",
    ".gitignore",
    "AGENTS.md",
    "DOCUMENT_METADATA_INDEX.md",
    "Dockerfile",
    "README.md",
    "docker-compose.yml",
    "loc_start.md",
    "package-lock.json",
    "package.json",
    "project.yaml",
    "requirements.txt",
    "start.md",
    "ui-design.md",
}

ALLOWED_ROOT_DIRS = {
    ".agents",
    ".git",
    "app",
    "compatibility",
    "data",
    "deploy",
    "dist",
    "docs",
    "import",
    "issues",
    "iterations",
    "models",
    "mintlify",
    "node_modules",
    "openspec",
    "packaging",
    "releases",
    "rules",
    "scripts",
    "tests",
}

FORBIDDEN_DIRS = {
    ".cursor": "Agent 技能入口已迁移到 .agents/skills/",
    ".agent": "请使用 .agents/skills/，不要使用单数 .agent/",
    "openspec/changes/archive": "OpenSpec 归档目录必须使用 openspec/archive/",
}

DEPLOY_ALLOWED_TOP_LEVEL = {"README.md", ".gitkeep", "local", "prod", "scripts"}
DEPLOY_FORBIDDEN_DIR_NAMES = {"__pycache__", "data", "minio", "runtime", "uploads", "images"}
DEPLOY_FORBIDDEN_EXTENSIONS = {".db", ".sqlite", ".sqlite3", ".tar"}
DEPLOY_FORBIDDEN_SUFFIXES = (".tar.gz", ".env", ".env.local", ".env.prod")

MINTLIFY_ALLOWED_TOP_LEVEL = {
    "README.md",
    "index.mdx",
    "docs.json",
    "site-manifest.json",
    "assets",
    "docs",
    "governance",
    "guides",
    "releases",
    "roles",
    "tasks",
    "versions",
}
MINTLIFY_FORBIDDEN_NAMES = {
    ".env",
    ".env.local",
    ".mintlify",
    "build",
    "dist",
    "node_modules",
    ".next",
    "coverage",
}
MINTLIFY_FORBIDDEN_SUFFIXES = {".sqlite", ".sqlite3", ".db", ".log"}
MINTLIFY_SENSITIVE_PATTERNS = (
    re.compile(r"\bAPP_SECRET_KEY\s*=", re.I),
    re.compile(r"\bDATABASE_URL\s*=", re.I),
    re.compile(r"sqlite:////", re.I),
    re.compile(r"\bS3_(?:ACCESS|SECRET)_KEY\s*=", re.I),
    re.compile(r"\bMINIO_(?:ACCESS|SECRET)_KEY\s*=", re.I),
    re.compile(r"\bAuthorization\s*:", re.I),
    re.compile(r"\bBearer\s+[A-Za-z0-9._-]+", re.I),
    re.compile(r"\bCookie\s*:", re.I),
)


def rel_posix(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def is_allowed_ignored_local_env_file(path: Path) -> bool:
    rel_path = rel_posix(path)
    if rel_path.endswith(".env.example") or rel_path == ".env.example":
        return False
    return any(fnmatch(rel_path, pattern) for pattern in IGNORED_LOCAL_ENV_FILE_PATTERNS)


def tracked_files() -> set[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return set()
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def validate_deploy_dir(tracked: set[str]) -> list[str]:
    errors: list[str] = []
    deploy_root = ROOT / "deploy"
    if not deploy_root.exists():
        return errors
    if not deploy_root.is_dir():
        return ["deploy 不是目录: deploy"]

    for child in sorted(deploy_root.iterdir()):
        if child.name not in DEPLOY_ALLOWED_TOP_LEVEL:
            errors.append(f"deploy 存在未登记一级路径: {rel_posix(child)}")

    for path in sorted(deploy_root.rglob("*")):
        rel = rel_posix(path)
        if path.is_dir():
            if path.name in DEPLOY_FORBIDDEN_DIR_NAMES:
                errors.append(f"deploy 存在禁止运行时目录: {rel}")
            continue
        if path.name == ".env" or any(path.name.endswith(suffix) for suffix in DEPLOY_FORBIDDEN_SUFFIXES):
            if not path.name.endswith(".env.example") and rel in tracked:
                errors.append(f"deploy 存在被 Git 跟踪的真实 env 文件: {rel}")
        if path.suffix in DEPLOY_FORBIDDEN_EXTENSIONS or path.name.endswith(".tar.gz"):
            errors.append(f"deploy 存在禁止提交的运行时或镜像文件: {rel}")
    return errors


def validate_mintlify_dir() -> list[str]:
    errors: list[str] = []
    site_root = ROOT / "mintlify"
    if not site_root.exists():
        return errors
    if not site_root.is_dir():
        return ["mintlify 不是目录: mintlify"]

    for child in sorted(site_root.iterdir()):
        if child.name not in MINTLIFY_ALLOWED_TOP_LEVEL:
            errors.append(f"mintlify/ 存在未登记路径: {rel_posix(child)}")

    for path in sorted(site_root.rglob("*")):
        rel = rel_posix(path)
        if path.name in MINTLIFY_FORBIDDEN_NAMES or re.fullmatch(r"\.env(?:\..+)?", path.name):
            errors.append(f"mintlify/ 存在禁止提交的构建产物或环境文件: {rel}")
        if path.is_dir():
            continue
        if path.suffix in MINTLIFY_FORBIDDEN_SUFFIXES:
            errors.append(f"mintlify/ 存在禁止提交的运行时文件: {rel}")
        if path.stat().st_size > 5 * 1024 * 1024:
            errors.append(f"mintlify/ 单文件超过 5MB，请改用共享截图去重或外部公开资产: {rel}")
        if path.suffix.lower() in {".md", ".mdx", ".json", ".txt", ".yml", ".yaml"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in MINTLIFY_SENSITIVE_PATTERNS:
                if pattern.search(text):
                    errors.append(f"mintlify/ 公开站点文件包含敏感模式 {pattern.pattern}: {rel}")
                    break
    return errors


def main() -> int:
    errors: list[str] = []

    for item in REQUIRED_PATHS:
        if not (ROOT / item).exists():
            errors.append(f"缺少必需路径: {item}")

    for item in REQUIRED_DIRS:
        if not (ROOT / item).is_dir():
            errors.append(f"缺少必需目录: {item}")

    for item, reason in FORBIDDEN_DIRS.items():
        if (ROOT / item).exists():
            errors.append(f"禁止目录存在: {item}（{reason}）")

    skill_root = ROOT / ".agents" / "skills"
    if skill_root.is_dir():
        actual_skills = {
            child.name
            for child in skill_root.iterdir()
            if child.is_dir() and (child / "SKILL.md").exists()
        }
        missing = sorted(EXPECTED_AGENT_SKILLS - actual_skills)
        extra = sorted(actual_skills - EXPECTED_AGENT_SKILLS)
        for name in missing:
            errors.append(f"缺少 Agent Skill: .agents/skills/{name}/SKILL.md")
        for name in extra:
            errors.append(f"未登记 Agent Skill: .agents/skills/{name}/SKILL.md")

    for child in ROOT.iterdir():
        if (
            child.is_file()
            and child.name not in ALLOWED_ROOT_FILES
            and not is_allowed_ignored_local_env_file(child)
        ):
            errors.append(f"根目录存在未登记文件: {child.name}")
        if child.is_dir() and child.name not in ALLOWED_ROOT_DIRS:
            errors.append(f"根目录存在未登记目录: {child.name}")

    gitignore = ROOT / ".gitignore"
    if gitignore.exists():
        ignored_patterns = {
            line.strip()
            for line in gitignore.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        }
        for pattern in sorted(GITIGNORE_REQUIRED_PATTERNS - ignored_patterns):
            errors.append(f".gitignore 缺少本地 env 忽略规则: {pattern}")

    tracked = tracked_files()
    for item in sorted(tracked):
        path = ROOT / item
        if path.exists() and is_allowed_ignored_local_env_file(path):
            errors.append(f"真实本地 env 文件不应被 Git 跟踪: {item}")

    errors.extend(validate_deploy_dir(tracked))
    errors.extend(validate_mintlify_dir())

    if errors:
        print("目录结构校验失败：")
        for err in errors:
            print(f"- {err}")
        return 1

    print("目录结构校验通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
