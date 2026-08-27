#!/usr/bin/env python3
"""Generate and validate ProjectSoulKing release upgrade plans."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RELEASES_DIR = ROOT / "releases"

SUPPORT_LEVELS = {
    "fresh-install-supported",
    "adjacent-upgrade-supported",
    "cross-version-upgrade-supported",
    "cross-version-upgrade-requires-manual-review",
    "unsupported",
}
SOURCE_CONFIDENCE = {"fresh", "verified", "reconstructed", "partial"}
NO_IMPACT_VALUES = {"", "none", "na", "n/a", "not_applicable", "not applicable", "无", "不涉及"}
ENV_EXAMPLE_PATTERNS = (
    ".env.example",
    "deploy/**/*.env.example",
    "scripts/build-images.env.example",
)
PRODUCTION_REQUIRED_KEYS = {
    "APP_ENV",
    "ADMIN_PASSWORD",
    "DATABASE_URL",
    "S3_ENDPOINT_URL",
    "S3_PUBLIC_ENDPOINT_URL",
    "S3_ACCESS_KEY_ID",
    "S3_SECRET_ACCESS_KEY",
    "S3_BUCKET_MUSIC",
    "SOULKING_IMAGE_TAG",
}
UNSAFE_VALUE_TOKENS = (
    "change-me",
    "replace-with",
    "example.com",
    "minioadmin",
    "admin123",
)
SENSITIVE_PATTERNS = (
    re.compile(r"\bAPP_SECRET_KEY\s*=", re.I),
    re.compile(r"\bDATABASE_URL\s*=\s*(?!<)", re.I),
    re.compile(r"\b(?:S3|MINIO)_(?:SECRET|ACCESS).*=\s*(?!<)", re.I),
    re.compile(r"\bAuthorization\s*:", re.I),
    re.compile(r"\bBearer\s+[A-Za-z0-9._-]+", re.I),
    re.compile(r"\bCookie\s*:", re.I),
    re.compile(r"/Users/[^\\s\"']+", re.I),
)


class UpgradePlanError(ValueError):
    """User-facing upgrade plan error."""


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def rel_path(path: Path, *, root: Path = ROOT) -> str:
    return os.path.relpath(path.resolve(), root)


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise UpgradePlanError(f"missing file: {path}") from None
    except json.JSONDecodeError as exc:
        raise UpgradePlanError(f"invalid JSON {path}: {exc}") from None
    if not isinstance(data, dict):
        raise UpgradePlanError(f"{path} must contain a JSON object")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def semver_key(version: str) -> tuple[int, int, int]:
    match = re.fullmatch(r"v(\d+)\.(\d+)\.(\d+)", version)
    if not match:
        raise UpgradePlanError(f"unsupported version format: {version}")
    return tuple(int(part) for part in match.groups())


def release_versions(root: Path = ROOT) -> list[str]:
    releases_dir = root / "releases"
    if not releases_dir.exists():
        return []
    versions = [
        path.name
        for path in releases_dir.iterdir()
        if path.is_dir() and re.fullmatch(r"v\d+\.\d+\.\d+", path.name)
    ]
    return sorted(versions, key=semver_key)


def previous_version(to_version: str, root: Path = ROOT) -> str | None:
    versions = [version for version in release_versions(root) if semver_key(version) < semver_key(to_version)]
    return versions[-1] if versions else None


def versions_between(from_version: str, to_version: str, root: Path = ROOT) -> list[str]:
    start = semver_key(from_version)
    end = semver_key(to_version)
    return [version for version in release_versions(root) if start < semver_key(version) <= end]


def release_dir(version: str, root: Path = ROOT) -> Path:
    return root / "releases" / version


def release_fact(version: str, root: Path = ROOT) -> dict[str, Any] | None:
    path = release_dir(version, root) / "release.json"
    return read_json(path) if path.exists() else None


def path_exists_summary(path: Path, root: Path = ROOT) -> dict[str, Any]:
    return {"path": rel_path(path, root=root), "exists": path.exists()}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_env_text(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip("'\"")
    return values


def env_example_files(root: Path = ROOT) -> list[Path]:
    files: list[Path] = []
    for pattern in ENV_EXAMPLE_PATTERNS:
        files.extend(path for path in root.glob(pattern) if path.is_file())
    return sorted(set(files), key=lambda path: rel_path(path, root=root))


def env_snapshot(root: Path = ROOT) -> dict[str, dict[str, str]]:
    return {rel_path(path, root=root): parse_env_text(path.read_text(encoding="utf-8")) for path in env_example_files(root)}


def diff_env_snapshots(source: dict[str, dict[str, str]], target: dict[str, dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    diff: dict[str, list[dict[str, str]]] = {
        "added": [],
        "removed": [],
        "changed_default": [],
        "required_in_production": [],
        "unsafe_example_value": [],
        "manual_review": [],
    }
    for path in sorted(set(source) | set(target)):
        before = source.get(path, {})
        after = target.get(path, {})
        for key in sorted(set(after) - set(before)):
            diff["added"].append({"path": path, "key": key, "recommendation": "确认目标环境是否需要显式配置"})
        for key in sorted(set(before) - set(after)):
            diff["removed"].append({"path": path, "key": key, "recommendation": "确认目标环境是否仍残留废弃变量"})
        for key in sorted(set(before) & set(after)):
            if before[key] != after[key]:
                diff["changed_default"].append({"path": path, "key": key, "recommendation": "复核示例默认值变化是否影响部署"})
        for key, value in sorted(after.items()):
            if key in PRODUCTION_REQUIRED_KEYS:
                diff["required_in_production"].append({"path": path, "key": key, "recommendation": "生产环境必须显式配置，不得依赖示例值"})
            if any(token in value.lower() for token in UNSAFE_VALUE_TOKENS):
                diff["unsafe_example_value"].append({"path": path, "key": key, "recommendation": "生产环境不得使用该示例值"})
    if not source:
        diff["manual_review"].append({"path": "release-history", "key": "*", "recommendation": "缺少历史 env 示例快照时，跨版本 env diff 需人工复核"})
    return diff


def current_env_diff(root: Path = ROOT) -> dict[str, Any]:
    return {
        "status": "manual_review",
        "source": "current-env-examples",
        "summary": diff_env_snapshots({}, env_snapshot(root)),
        "notes": [
            "当前仓库默认不保存历史版本 env 示例快照；跨版本 env diff 需结合 Git tag、release 归档或人工快照复核。",
            "输出仅包含变量名、分类和建议，不包含真实 env 值。",
        ],
    }


def impact_requires(release_data: dict[str, Any] | None, key: str) -> bool:
    if not isinstance(release_data, dict):
        return False
    impact = release_data.get("impact_scope")
    if not isinstance(impact, dict):
        return False
    return str(impact.get(key, "")).strip().lower() not in NO_IMPACT_VALUES


def source_confidence_for(version: str, root: Path = ROOT) -> str:
    if version == "fresh":
        return "fresh"
    data = release_fact(version, root)
    if not data:
        return "partial"
    return "verified" if data.get("version") == version else "reconstructed"


def manifest_exists(version: str, root: Path = ROOT) -> bool:
    data = release_fact(version, root)
    manifest_name = str(data.get("image_manifest", "image-manifest.json")) if data else "image-manifest.json"
    return (release_dir(version, root) / manifest_name).exists()


def classify_support(from_version: str, to_version: str, root: Path, blockers: list[str], warnings: list[str]) -> str:
    if blockers:
        return "unsupported"
    if from_version == "fresh":
        return "fresh-install-supported"
    previous = previous_version(to_version, root)
    if from_version == previous:
        return "adjacent-upgrade-supported"
    between = versions_between(from_version, to_version, root)
    if not between:
        return "unsupported"
    missing_release = [version for version in between if release_fact(version, root) is None]
    missing_manifest = [version for version in between if not manifest_exists(version, root)]
    if missing_release or missing_manifest:
        warnings.append(
            "跨版本路径缺少完整 release 或 image manifest 证据，需人工复核："
            f"missing_release={missing_release}, missing_manifest={missing_manifest}"
        )
    warnings.append("跨版本路径必须补充 SQLite 备份/恢复、env diff、MinIO 影响和升级/回滚 smoke 证据后才能标记 supported。")
    return "cross-version-upgrade-requires-manual-review"


def safe_plan_name(from_version: str, to_version: str) -> str:
    source = "fresh" if from_version == "fresh" else from_version
    return f"{source}-to-{to_version}.json"


def upgrade_steps(from_version: str, to_version: str, previous: str | None) -> list[str]:
    if from_version == "fresh":
        return [
            f"确认 releases/{to_version}/release.json 与目标 image-manifest.json 状态。",
            "准备生产 env，显式配置 APP_ENV、DATABASE_URL、对象存储变量和 SOULKING_IMAGE_TAG。",
            "执行 Docker Compose config 或部署矩阵 env 校验。",
            "在空 SQLite 数据目录启动应用并确认管理员登录、曲库空态、对象存储连接和产品手册站按需可用。",
            "完成 health、login、歌曲导入、播放/下载、头像或封面访问 smoke。",
        ]
    if previous == from_version:
        return [
            f"确认来源版本 {from_version} 与目标版本 {to_version} 的 release 事实源。",
            "备份 SQLite 数据目录、对象存储影响摘要和当前 env 变量名摘要。",
            f"加载或拉取目标镜像，将 SOULKING_IMAGE_TAG 更新为 {to_version}。",
            "执行 Compose/env 校验并重启服务。",
            "完成升级后 health、login、曲库、播放/下载、歌词、头像/封面和对象存储 smoke。",
        ]
    return [
        f"聚合 {from_version} 到 {to_version} 所有中间版本的 release、SQLite、env、Docker、API、对象存储和维护任务影响。",
        "先完成 dry-run、备份确认和人工复核；必要时拆为多个相邻版本升级。",
        f"加载或拉取目标镜像，将 SOULKING_IMAGE_TAG 更新为 {to_version}。",
        "执行升级后 smoke；缺少演练证据时不得标记为 cross-version-upgrade-supported。",
    ]


def rollback_steps(from_version: str, to_version: str, database_impact: bool, object_storage_impact: bool) -> dict[str, Any]:
    previous_label = "人工确认的上一稳定版本" if from_version == "fresh" else from_version
    return {
        "previous_image": previous_label,
        "target_image": to_version,
        "env_snapshot": "旧 env 变量名摘要、hash 或负责人确认；不得记录真实值",
        "database_backup": "required" if database_impact or from_version != "fresh" else "recommended",
        "object_storage_backup": "required" if object_storage_impact else "manual_review",
        "rollback_steps": [
            f"回退 SOULKING_IMAGE_TAG 或镜像包到 {previous_label}。",
            "恢复旧 env 摘要对应的真实 env，由运维在目标环境执行。",
            "如 SQLite 数据已写入变更，根据升级前备份恢复或已验证反向迁移执行。",
            "如对象存储执行过写入型维护，根据备份、对象 key 审计或人工方案处理。",
            "完成回滚后 health、login、曲库、播放/下载和媒体访问 smoke。",
        ],
        "post_rollback_smoke": "pending",
    }


def assert_public_safe(data: Any, *, artifact: str) -> None:
    text = json.dumps(data, ensure_ascii=False)
    matches = [pattern.pattern for pattern in SENSITIVE_PATTERNS if pattern.search(text)]
    if matches:
        raise UpgradePlanError(f"{artifact} contains sensitive pattern(s): {', '.join(matches)}")


def build_plan(from_version: str, to_version: str, root: Path = ROOT) -> dict[str, Any]:
    target_release = release_fact(to_version, root)
    source_release = None if from_version == "fresh" else release_fact(from_version, root)
    blockers: list[str] = []
    warnings: list[str] = []

    if from_version != "fresh":
        semver_key(from_version)
    semver_key(to_version)
    if target_release is None:
        blockers.append(f"target release missing: releases/{to_version}/release.json")
    elif target_release.get("version") != to_version:
        blockers.append(f"target release version mismatch: expected {to_version}")
    if from_version != "fresh" and source_release is None:
        warnings.append(f"source release fact missing or partial: releases/{from_version}/release.json")
    if target_release and target_release.get("image_required") is True and not manifest_exists(to_version, root):
        blockers.append(f"target image manifest missing: releases/{to_version}/image-manifest.json")

    previous = previous_version(to_version, root)
    database_impact = impact_requires(target_release, "database")
    object_storage_impact = impact_requires(target_release, "object_storage")
    if database_impact:
        warnings.append("目标版本声明数据库影响，必须补充 SQLite 备份、迁移兼容和升级后读写 smoke 证据。")
    if object_storage_impact:
        warnings.append("目标版本声明对象存储影响，必须补充 MinIO 对象 key、访问和回滚边界证据。")

    support_level = classify_support(from_version, to_version, root, blockers, warnings)
    target_dir = release_dir(to_version, root)
    plan = {
        "schema_version": 1,
        "generated_at": now_text(),
        "from_version": from_version,
        "to_version": to_version,
        "support_level": support_level,
        "source_confidence": source_confidence_for(from_version, root),
        "version_facts": {
            "target_release": path_exists_summary(target_dir / "release.json", root),
            "target_image_manifest": path_exists_summary(target_dir / "image-manifest.json", root),
            "deployment_image_tag": {"key": "SOULKING_IMAGE_TAG", "expected": to_version, "value": "<redacted-or-operator-confirmed>"},
            "git_ref": {"status": "manual_review", "recommendation": "使用发布 tag 或 commit 补充源码快照锚点"},
        },
        "impact_summary": {
            "database": "requires_sqlite_backup_and_migration_smoke" if database_impact else "backup_recommended",
            "environment": "manual_review",
            "docker": "target image manifest required when image_required=true",
            "api": "manual_review_for_cross_version" if from_version != "fresh" else "none",
            "object_storage": "requires_minio_evidence" if object_storage_impact else "manual_review",
            "maintenance_jobs": "dry_run_required_if_write_tasks_exist",
        },
        "env_diff": current_env_diff(root),
        "required_checks": [
            f"python scripts/validate-release-upgrade.py validate-plan --plan releases/{to_version}/upgrade-plans/{safe_plan_name(from_version, to_version)}",
            f"python scripts/validate-image-build.py validate-manifest --release {to_version}",
            "docker compose config --quiet 或 deploy/scripts/validate-env.py 对应环境校验",
            "升级前备份 SQLite 数据目录；升级后执行 health/login/song import/playback/download/media smoke",
            "对象存储影响非 none 时执行 MinIO 对象 key、presigned URL 或流式访问 smoke",
        ],
        "steps": upgrade_steps(from_version, to_version, previous),
        "rollback": rollback_steps(from_version, to_version, database_impact, object_storage_impact),
        "blockers": blockers,
        "warnings": warnings,
        "evidence": {
            "release": path_exists_summary(target_dir / "release.json", root),
            "image_manifest": path_exists_summary(target_dir / "image-manifest.json", root),
            "database": "pending_sqlite_backup_or_smoke",
            "object_storage": "manual_review",
            "post_upgrade_smoke": "pending",
            "post_rollback_smoke": "pending",
            "env_examples_hash": sha256_text(json.dumps(env_snapshot(root), ensure_ascii=False, sort_keys=True)),
        },
    }
    assert_public_safe(plan, artifact="upgrade plan")
    return plan


def validate_plan_data(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = (
        "from_version",
        "to_version",
        "support_level",
        "source_confidence",
        "impact_summary",
        "env_diff",
        "required_checks",
        "steps",
        "rollback",
        "blockers",
        "warnings",
        "evidence",
    )
    for key in required:
        if key not in data:
            errors.append(f"missing required field: {key}")
    if data.get("support_level") not in SUPPORT_LEVELS:
        errors.append(f"invalid support_level: {data.get('support_level')}")
    if data.get("source_confidence") not in SOURCE_CONFIDENCE:
        errors.append(f"invalid source_confidence: {data.get('source_confidence')}")
    rollback = data.get("rollback")
    if not isinstance(rollback, dict):
        errors.append("rollback must be an object")
    else:
        for key in ("previous_image", "target_image", "env_snapshot", "database_backup", "object_storage_backup", "rollback_steps", "post_rollback_smoke"):
            if key not in rollback:
                errors.append(f"rollback missing field: {key}")
    try:
        assert_public_safe(data, artifact="upgrade plan")
    except UpgradePlanError as exc:
        errors.append(str(exc))
    return errors


def write_plan(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    plan = build_plan(args.from_version, args.to_version, root)
    output = args.output or root / "releases" / args.to_version / "upgrade-plans" / safe_plan_name(args.from_version, args.to_version)
    write_json(output, plan)
    print("升级计划已生成：")
    print(f"- path: {rel_path(output, root=root)}")
    print(f"- support_level: {plan['support_level']}")
    print(f"- blockers: {len(plan['blockers'])}")
    print(f"- warnings: {len(plan['warnings'])}")
    return 0


def validate_plan(args: argparse.Namespace) -> int:
    data = read_json(args.plan)
    errors = validate_plan_data(data)
    if errors:
        print("升级计划校验失败：")
        for error in errors:
            print(f"- {error}")
        return 1
    print("升级计划校验通过：")
    print(f"- plan: {args.plan}")
    print(f"- support_level: {data.get('support_level')}")
    print(f"- blockers: {len(data.get('blockers') or [])}")
    print(f"- warnings: {len(data.get('warnings') or [])}")
    return 0


def print_env_diff(args: argparse.Namespace) -> int:
    source = env_snapshot(args.from_dir.resolve()) if args.from_dir else {}
    target = env_snapshot(args.to_dir.resolve()) if args.to_dir else env_snapshot(args.root.resolve())
    print(json.dumps(diff_env_snapshots(source, target), ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    sub = parser.add_subparsers(dest="command", required=True)

    plan_parser = sub.add_parser("plan", help="Generate an upgrade plan")
    plan_parser.add_argument("--from", dest="from_version", required=True)
    plan_parser.add_argument("--to", dest="to_version", required=True)
    plan_parser.add_argument("--output", type=Path)
    plan_parser.set_defaults(func=write_plan)

    validate_parser = sub.add_parser("validate-plan", help="Validate an upgrade plan")
    validate_parser.add_argument("--plan", required=True, type=Path)
    validate_parser.set_defaults(func=validate_plan)

    env_parser = sub.add_parser("env-diff", help="Diff env example files")
    env_parser.add_argument("--from-dir", type=Path)
    env_parser.add_argument("--to-dir", type=Path)
    env_parser.set_defaults(func=print_env_diff)

    args = parser.parse_args()
    try:
        return int(args.func(args))
    except UpgradePlanError as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
