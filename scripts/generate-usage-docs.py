#!/usr/bin/env python3
"""Generate or record skipped versioned usage docs for a release."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RELEASES_DIR = ROOT / "releases"
MINTLIFY_DIR = ROOT / "mintlify"
TEMPLATE_DIR = RELEASES_DIR / "templates" / "usage-docs"
TIME_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")
VERSION_PATTERN = re.compile(r"v(\d+)\.(\d+)\.(\d+)(?:[-.]([A-Za-z0-9.]+))?")


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"missing file: {path}") from None
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON {path}: {exc}") from None
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repo_relative(path: Path) -> str:
    for base in (ROOT, RELEASES_DIR.parent):
        try:
            return str(path.relative_to(base)).replace("\\", "/")
        except ValueError:
            continue
    return str(path)


def release_dir(version: str) -> Path:
    if not VERSION_PATTERN.fullmatch(version):
        raise ValueError(f"version must be SemVer-like, got {version}")
    return RELEASES_DIR / version


def parse_semver(version: str) -> tuple[int, int, int, tuple[int, str, str]] | None:
    match = VERSION_PATTERN.fullmatch(version)
    if not match:
        return None
    suffix = match.group(4) or ""
    suffix_rank = (1, "", "") if not suffix else (0, suffix.lower(), suffix)
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)), suffix_rank)


def previous_usage_docs_version(version: str) -> str | None:
    current = parse_semver(version)
    if current is None:
        raise ValueError(f"version must be SemVer-like, got {version}")
    candidates: list[tuple[tuple[int, int, int, tuple[int, str, str]], str]] = []
    for path in RELEASES_DIR.iterdir() if RELEASES_DIR.exists() else []:
        if path.name == version or not path.is_dir():
            continue
        parsed = parse_semver(path.name)
        if parsed is None or parsed >= current:
            continue
        if (path / "usage-docs" / "manifest.json").exists():
            candidates.append((parsed, path.name))
    return max(candidates)[1] if candidates else None


def ensure_generation_confirmed(data: dict[str, Any]) -> dict[str, Any]:
    usage_docs = data.get("usage_docs")
    if not isinstance(usage_docs, dict):
        raise ValueError("release.json usage_docs object is required before generating usage docs")
    decision = usage_docs.get("generation_decision")
    if not isinstance(decision, dict):
        raise ValueError("usage_docs.generation_decision object is required")
    if decision.get("required") is not True:
        raise ValueError("usage_docs.generation_decision.required must be true before generating usage docs")
    for key in ("confirmed_at", "confirmed_by", "rationale"):
        if not decision.get(key):
            raise ValueError(f"usage_docs.generation_decision.{key} is required before generating usage docs")
    if not TIME_PATTERN.fullmatch(str(decision.get("confirmed_at", ""))):
        raise ValueError("usage_docs.generation_decision.confirmed_at must be YYYY-MM-DD HH:mm:ss")
    return usage_docs


def template_context(version: str, generated_at: str, source_version: str | None) -> dict[str, str]:
    return {
        "VERSION": version,
        "GENERATED_AT": generated_at,
        "SOURCE_VERSION": source_version or "null",
    }


def render_template(text: str, context: dict[str, str]) -> str:
    for key, value in context.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def copy_usage_doc_templates(target_dir: Path, context: dict[str, str]) -> list[str]:
    if not TEMPLATE_DIR.exists():
        raise ValueError(f"missing usage docs template directory: {TEMPLATE_DIR}")
    pages: list[str] = []
    for src in sorted(TEMPLATE_DIR.rglob("*")):
        rel = src.relative_to(TEMPLATE_DIR)
        if src.is_dir():
            (target_dir / rel).mkdir(parents=True, exist_ok=True)
            continue
        if rel.name == "manifest.json":
            continue
        target = target_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_template(src.read_text(encoding="utf-8"), context), encoding="utf-8")
        if target.suffix == ".mdx":
            pages.append(str(rel).replace("\\", "/"))
    return pages


def copy_previous_usage_docs(version: str, target_dir: Path, previous_version: str) -> tuple[list[str], dict[str, Any] | None]:
    previous_dir = release_dir(previous_version) / "usage-docs"
    previous_manifest_path = previous_dir / "manifest.json"
    if not previous_dir.exists() or not previous_manifest_path.exists():
        return [], None

    for src in sorted(previous_dir.rglob("*")):
        rel = src.relative_to(previous_dir)
        if rel.parts and rel.parts[0] == "assets":
            continue
        target = target_dir / rel
        if src.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        text = src.read_text(encoding="utf-8")
        if src.suffix == ".mdx":
            text = text.replace(previous_version, version)
        target.write_text(text, encoding="utf-8")

    previous_manifest = load_json(previous_manifest_path)
    pages = [str(page) for page in previous_manifest.get("pages", []) if isinstance(page, str)]
    return pages, previous_manifest


def build_manifest(
    version: str,
    release_path: Path,
    pages: list[str],
    generated_at: str,
    source_version: str | None,
    previous_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    input_files = [
        "release.json",
        "../../mintlify/docs.json",
        "../../app/static/index.html",
        "../../app/static/admin.html",
        "../../app/static/app.js",
        "../../app/static/admin.js",
        "../../app/main.py",
    ]
    manifest = {
        "version": version,
        "generated_at": generated_at,
        "source_version": source_version,
        "source_release": {
            "path": "release.json",
            "sha256": file_sha256(release_path),
        },
        "input_files": input_files,
        "pages": pages,
        "site_projection": {
            "status": "pending",
            "source_release": f"releases/{version}",
            "source_manifest": f"releases/{version}/usage-docs/manifest.json",
            "target_site_root": f"mintlify/docs/{version}",
            "latest_target": "mintlify/docs/latest",
            "synced_at": None,
            "mode": "copy",
            "content_hashes": {},
            "manual_overrides": [],
        },
        "screenshots": [],
        "coverage": {
            "web_public": {"status": "draft", "notes": "由模板生成；发布前需人工确认前台曲库、播放、歌单和用户入口覆盖。"},
            "web_admin": {"status": "draft", "notes": "由模板生成；发布前需人工确认后台音乐、参考数据、用户和存储入口覆盖。"},
            "media": {"status": "draft", "notes": "由模板生成；发布前需人工确认音频、歌词、封面和对象存储行为覆盖。"},
            "release_impact_scope": {"status": "draft", "notes": "以 release.json impact_scope 为事实源补齐。"},
        },
        "manual_overrides": [],
        "automation_policy": {
            "current_version": "generated files may be updated by automation after explicit generation decision",
            "old_versions": "content is locked by default; non-content maintenance and public-safety fixes are allowed with trace",
            "content_corrections_require_authorization": True,
        },
    }
    if previous_manifest:
        inherited_screenshots = []
        for item in previous_manifest.get("screenshots", []):
            if not isinstance(item, dict):
                continue
            copied = dict(item)
            used_versions = list(copied.get("used_by_versions", []))
            if version not in used_versions:
                used_versions.append(version)
            copied["used_by_versions"] = used_versions
            copied["reuse_reason"] = (
                f"{version} 继承 {source_version} 完整使用文档基线；截图对应页面语义未变化，继续复用共享真实系统截图。"
            )
            inherited_screenshots.append(copied)
        manifest["screenshots"] = inherited_screenshots
        manifest["coverage"] = previous_manifest.get("coverage", manifest["coverage"])
        manifest["manual_overrides"] = [
            {
                "change_type": "current_version_inherit_previous_usage_docs",
                "authorized": True,
                "reason": f"{version} 使用文档必须包含前一版本 {source_version} 的完整内容。",
                "confirmed_by": "automation",
                "confirmed_at": generated_at,
                "files": ["usage-docs/**", "usage-docs/manifest.json", "mintlify/docs/**"],
                "summary": f"从 {source_version} 复制完整 usage docs 基线，并将页面版本号更新为 {version}。",
            }
        ]
        input_files.append(f"../{source_version}/usage-docs/manifest.json")
    return manifest


def rewrite_site_links(text: str, version: str) -> str:
    text = text.replace(f"{version}/usage-docs/", f"/docs/{version}/")
    text = text.replace("usage-docs/", f"/docs/{version}/")
    text = text.replace("../mint.json", "/docs.json")
    text = text.replace("../docs.json", "/docs.json")
    return text


def ensure_mintlify_base() -> None:
    for path in (
        MINTLIFY_DIR / "docs",
        MINTLIFY_DIR / "releases",
        MINTLIFY_DIR / "assets" / "screenshots",
    ):
        path.mkdir(parents=True, exist_ok=True)
    docs_path = MINTLIFY_DIR / "docs.json"
    if not docs_path.exists():
        write_json(
            docs_path,
            {
                "$schema": "https://mintlify.com/docs.json",
                "name": "ProjectSoulKing 产品手册",
                "theme": "mint",
                "navigation": {"versions": [{"version": "简体中文", "tabs": []}]},
            },
        )


def copy_release_announcement(version: str, rdir: Path) -> str | None:
    src = rdir / "announcement.mdx"
    if not src.exists():
        return None
    target = MINTLIFY_DIR / "releases" / version / "announcement.mdx"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    return repo_relative(target)


def copy_shared_screenshots(manifest: dict[str, Any], usage_dir: Path, version: str) -> list[dict[str, Any]]:
    projected: list[dict[str, Any]] = []
    for item in manifest.get("screenshots", []):
        if not isinstance(item, dict):
            continue
        raw_path = str(item.get("path", "")).strip()
        site_asset = str(item.get("site_asset", "")).strip()
        if site_asset.startswith("mintlify/assets/screenshots/"):
            item["path"] = "/" + site_asset.removeprefix("mintlify/")
            item.setdefault("first_used_in", version)
            item.setdefault("used_by_versions", [version])
            item.setdefault("covered_pages", item.get("pages", []))
            item.setdefault("reuse_reason", "当前版本复用共享真实系统截图资产")
            projected.append(item)
            continue
        if not raw_path or raw_path.startswith(("http://", "https://", "data:", "/", "../")):
            continue
        source = usage_dir / raw_path
        if not source.exists() or source.is_dir():
            continue
        digest = file_sha256(source)
        semantic_name = re.sub(r"[^A-Za-z0-9._-]+", "-", source.stem).strip("-") or "screenshot"
        target = MINTLIFY_DIR / "assets" / "screenshots" / f"sha256-{digest[:16]}-{semantic_name}{source.suffix.lower()}"
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copy2(source, target)
        item["content_hash"] = digest
        item["site_asset"] = repo_relative(target)
        item["path"] = "/" + item["site_asset"].removeprefix("mintlify/")
        item.setdefault("first_used_in", version)
        item.setdefault("used_by_versions", [version])
        item.setdefault("covered_pages", item.get("pages", []))
        item.setdefault("reuse_reason", "当前版本首次投影或界面语义未变化")
        projected.append(item)
    return projected


def update_mintlify_navigation(version: str, pages: list[str], *, has_usage_docs: bool) -> None:
    page_set = {page.removesuffix(".mdx") for page in pages}

    def refs(prefix: str, candidates: list[str]) -> list[str]:
        return [f"{prefix}/{page}" for page in candidates if page in page_set]

    latest_pages = refs("docs/latest", ["overview", "faq"])
    latest_web_pages = refs("docs/latest", ["web/index"])
    latest_admin_pages = refs("docs/latest", ["admin/index"])
    version_pages = refs(
        f"docs/{version}",
        [
            "overview",
            "web/index",
            "admin/index",
            "faq",
        ],
    )
    docs_navigation = {
        "versions": [
            {
                "version": "简体中文",
                "tabs": [
                    {
                        "tab": "用户指南",
                        "groups": [
                            {"group": "入门", "pages": ["index", "guides/getting-started", *latest_pages]},
                            {"group": "产品入口", "pages": ["roles/admin", "roles/listener", "roles/operator"]},
                            {"group": "常用任务", "pages": ["tasks/music-library", "tasks/media-and-lyrics"]},
                        ],
                    }
                ],
            }
        ]
    }
    if has_usage_docs:
        docs_navigation["versions"][0]["tabs"].extend(
            [
                {
                    "tab": "当前版本",
                    "groups": [
                        {"group": "前台 Web", "pages": latest_web_pages},
                        {"group": "后台管理", "pages": latest_admin_pages},
                    ],
                },
                {
                    "tab": "版本与公告",
                    "groups": [
                        {"group": "版本索引", "pages": ["versions/index", *version_pages]},
                        {"group": "发布公告", "pages": [f"releases/{version}/announcement"]},
                    ],
                },
                {
                    "tab": "文档治理",
                    "groups": [
                        {"group": "公开边界", "pages": ["governance/public-boundary", "governance/site-governance"]},
                    ],
                },
            ]
        )
    write_json(
        MINTLIFY_DIR / "docs.json",
        {
            "$schema": "https://mintlify.com/docs.json",
            "name": "ProjectSoulKing 产品手册",
            "theme": "mint",
            "colors": {
                "primary": "#6A4C93",
                "light": "#8F79B8",
                "dark": "#3F2D59",
            },
            "favicon": "/favicon.svg",
            "navigation": docs_navigation,
        },
    )


def project_usage_docs_to_mintlify(version: str, rdir: Path, usage_dir: Path, manifest: dict[str, Any], generated_at: str) -> None:
    ensure_mintlify_base()
    pages = [str(page) for page in manifest.get("pages", []) if isinstance(page, str)]
    target_root = MINTLIFY_DIR / "docs" / version
    latest_root = MINTLIFY_DIR / "docs" / "latest"
    for target in (target_root, latest_root):
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True, exist_ok=True)
    content_hashes: dict[str, str] = {}
    for page in pages:
        src = usage_dir / page
        if not src.exists():
            continue
        rendered = rewrite_site_links(src.read_text(encoding="utf-8"), version)
        for target in (target_root / page, latest_root / page):
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(rendered, encoding="utf-8")
        content_hashes[page] = hashlib.sha256(rendered.encode("utf-8")).hexdigest()
    copy_release_announcement(version, rdir)
    projected_screenshots = copy_shared_screenshots(manifest, usage_dir, version)
    projection = {
        "status": "synced",
        "source_release": repo_relative(rdir),
        "source_manifest": repo_relative(usage_dir / "manifest.json"),
        "target_site_root": repo_relative(target_root),
        "latest_target": repo_relative(latest_root),
        "synced_at": generated_at,
        "mode": "copy",
        "content_hashes": content_hashes,
        "manual_overrides": [],
    }
    manifest["site_projection"] = projection
    manifest["screenshots"] = projected_screenshots or manifest.get("screenshots", [])
    write_json(usage_dir / "manifest.json", manifest)
    write_json(
        MINTLIFY_DIR / "site-manifest.json",
        {
            "updated_at": generated_at,
            "latest_version": version,
            "versions": [version],
            "assets": projected_screenshots,
            "projections": [projection],
        },
    )
    update_mintlify_navigation(version, pages, has_usage_docs=True)


def generate_usage_docs(version: str, *, force: bool = False) -> Path:
    rdir = release_dir(version)
    release_path = rdir / "release.json"
    data = load_json(release_path)
    usage_docs = ensure_generation_confirmed(data)
    target_dir = rdir / str(usage_docs.get("root") or "usage-docs")
    if target_dir.exists() and not force:
        raise ValueError(f"{target_dir} already exists; rerun with --force to overwrite current-version generated docs")
    if target_dir.exists():
        shutil.rmtree(target_dir)

    generated_at = now_text()
    source_version = str(usage_docs.get("source_version") or "") or previous_usage_docs_version(version)
    previous_manifest = None
    pages: list[str] = []
    if source_version and source_version != version:
        pages, previous_manifest = copy_previous_usage_docs(version, target_dir, source_version)
    if not pages:
        pages = copy_usage_doc_templates(target_dir, template_context(version, generated_at, source_version))
    manifest = build_manifest(version, release_path, pages, generated_at, source_version, previous_manifest)
    write_json(target_dir / "manifest.json", manifest)
    project_usage_docs_to_mintlify(version, rdir, target_dir, manifest, generated_at)

    usage_docs.update(
        {
            "status": "generated",
            "root": str(usage_docs.get("root") or "usage-docs"),
            "manifest": str(usage_docs.get("manifest") or "usage-docs/manifest.json"),
            "source_version": source_version,
            "manual_overrides_allowed": True,
            "overwrite_policy": "current-version-only-by-default",
        }
    )
    data["usage_docs"] = usage_docs
    gates = data.setdefault("gates", {})
    gates["usage_docs_preview"] = {
        "status": "blocked",
        "evidence": (
            f"{generated_at}: scripts/generate-usage-docs.py generated {target_dir.relative_to(rdir)} with {len(pages)} pages. "
            "Add real system screenshots to mintlify/assets/screenshots, populate manifest.screenshots[] with "
            "path=/assets/screenshots/<file>, site_asset, pages, caption, source and source_type, "
            "then run scripts/validate-usage-docs.py before publish. Site projection was prepared under mintlify/."
        ),
    }
    write_json(release_path, data)
    return target_dir


def project_existing_usage_docs(version: str) -> Path:
    rdir = release_dir(version)
    release_path = rdir / "release.json"
    data = load_json(release_path)
    usage_docs = data.get("usage_docs")
    if not isinstance(usage_docs, dict) or str(usage_docs.get("status", "")).lower() != "generated":
        raise ValueError(f"{version} usage_docs.status must be generated before projection")
    root_name = str(usage_docs.get("root") or "usage-docs")
    manifest_name = str(usage_docs.get("manifest") or f"{root_name}/manifest.json")
    usage_dir = rdir / root_name
    manifest_path = rdir / manifest_name
    if not usage_dir.exists():
        raise ValueError(f"usage docs directory missing: {usage_dir}")
    manifest = load_json(manifest_path)
    projected_at = now_text()
    project_usage_docs_to_mintlify(version, rdir, usage_dir, manifest, projected_at)
    gates = data.setdefault("gates", {})
    gate = gates.setdefault("usage_docs_preview", {})
    evidence = str(gate.get("evidence", "")).strip()
    append = (
        f"{projected_at}: scripts/generate-usage-docs.py --project-existing {version} "
        f"projected release usage docs to mintlify/docs/{version}, mintlify/docs/latest, "
        "mintlify/releases and shared screenshot assets."
    )
    gate["status"] = gate.get("status") or "blocked"
    gate["evidence"] = f"{evidence} {append}".strip()
    write_json(release_path, data)
    return MINTLIFY_DIR / "docs" / version


def mark_skipped(version: str, *, confirmed_by: str, rationale: str, confirmed_at: str | None = None) -> None:
    if not rationale.strip():
        raise ValueError("--rationale is required when marking usage docs skipped")
    if not confirmed_by.strip():
        raise ValueError("--confirmed-by is required when marking usage docs skipped")
    rdir = release_dir(version)
    release_path = rdir / "release.json"
    data = load_json(release_path)
    root_name = str(data.get("usage_docs", {}).get("root", "usage-docs")) if isinstance(data.get("usage_docs"), dict) else "usage-docs"
    target_dir = rdir / root_name
    if target_dir.exists():
        raise ValueError(f"refusing to mark skipped because usage docs directory exists: {target_dir}")

    confirmed_at = confirmed_at or now_text()
    if not TIME_PATTERN.fullmatch(confirmed_at):
        raise ValueError("--confirmed-at must be YYYY-MM-DD HH:mm:ss")
    data["usage_docs"] = {
        "status": "skipped",
        "root": root_name,
        "manifest": f"{root_name}/manifest.json",
        "source_version": None,
        "manual_overrides_allowed": True,
        "overwrite_policy": "current-version-only-by-default",
        "generation_decision": {
            "required": False,
            "confirmed_at": confirmed_at,
            "confirmed_by": confirmed_by,
            "rationale": rationale,
        },
    }
    gates = data.setdefault("gates", {})
    gates["usage_docs_preview"] = {
        "status": "na",
        "rationale": f"{confirmed_at}: usage docs skipped by {confirmed_by}; {rationale}",
    }
    write_json(release_path, data)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate or skip versioned product usage docs.")
    parser.add_argument("version", help="Release version such as v0.3.2")
    parser.add_argument("--force", action="store_true", help="Overwrite current-version usage docs when already present")
    parser.add_argument("--skip", action="store_true", help="Record confirmed non-generation instead of generating files")
    parser.add_argument("--project-existing", action="store_true", help="Project existing generated release usage docs into mintlify/")
    parser.add_argument("--confirmed-by", default="operator", help="Confirmation source for --skip")
    parser.add_argument("--confirmed-at", help="Confirmation time for --skip, YYYY-MM-DD HH:mm:ss")
    parser.add_argument("--rationale", default="", help="Required rationale for --skip")
    args = parser.parse_args()

    try:
        if args.skip:
            mark_skipped(args.version, confirmed_by=args.confirmed_by, rationale=args.rationale, confirmed_at=args.confirmed_at)
            print(f"Usage docs skipped for {args.version}; release.json updated.")
        elif args.project_existing:
            target = project_existing_usage_docs(args.version)
            print(f"Existing usage docs projected to Mintlify: {target}")
        else:
            target = generate_usage_docs(args.version, force=args.force)
            print(f"Usage docs generated: {target}")
            print(
                "Next: add real system screenshots under mintlify/assets/screenshots/, "
                "populate manifest.screenshots[] with shared site_asset entries, then run scripts/validate-usage-docs.py."
            )
    except ValueError as exc:
        print(f"Usage docs generation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(main())
