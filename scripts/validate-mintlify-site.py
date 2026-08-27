#!/usr/bin/env python3
"""Validate the public Mintlify documentation site projection."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MINTLIFY_DIR = ROOT / "mintlify"
MARKDOWN_LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
MARKDOWN_IMAGE_PATTERN = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
MDX_HREF_PATTERN = re.compile(r"\bhref=[\"']([^\"']+)[\"']")
TIME_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")
FORBIDDEN_NAMES = {
    ".DS_Store",
    ".env",
    ".env.local",
    ".mintlify",
    "build",
    "dist",
    "node_modules",
    ".next",
    "coverage",
}
FORBIDDEN_NAME_PATTERNS = (
    re.compile(r"^\.env(?:\..+)?$"),
)
FORBIDDEN_SUFFIXES = {
    ".sqlite",
    ".sqlite3",
    ".db",
    ".log",
}
SENSITIVE_PATTERNS = (
    re.compile(r"\bAPP_SECRET_KEY\s*=", re.I),
    re.compile(r"\bDATABASE_URL\s*=", re.I),
    re.compile(r"sqlite:////", re.I),
    re.compile(r"mysql(\+\w+)?://", re.I),
    re.compile(r"\bS3_(?:ACCESS|SECRET)_KEY\s*=", re.I),
    re.compile(r"\bMINIO_(?:ACCESS|SECRET)_KEY\s*=", re.I),
    re.compile(r"\bAuthorization\s*:", re.I),
    re.compile(r"\bBearer\s+[A-Za-z0-9._-]+", re.I),
    re.compile(r"\bCookie\s*:", re.I),
    re.compile(r"\bpassword\s*=", re.I),
)


def load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing file: {path.relative_to(ROOT)}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON {path.relative_to(ROOT)}: {exc}")
        return {}
    if not isinstance(data, dict):
        errors.append(f"{path.relative_to(ROOT)} must contain a JSON object")
        return {}
    return data


def site_page_ref(path: Path) -> str:
    return str(path.relative_to(MINTLIFY_DIR).with_suffix("")).replace("\\", "/")


def page_path_from_ref(ref: str) -> Path:
    return MINTLIFY_DIR / f"{ref.removeprefix('/').removesuffix('/')}.mdx"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collect_navigation_pages(config: dict[str, Any]) -> list[str]:
    pages: list[str] = []

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                if key == "pages" and isinstance(nested, list):
                    for page in nested:
                        if isinstance(page, str):
                            pages.append(page)
                        else:
                            visit(page)
                else:
                    visit(nested)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    visit(config.get("navigation", []))
    return pages


def normalize_ref(raw_ref: str) -> str:
    ref = raw_ref.strip().split()[0].strip("<>")
    ref = ref.split("#", 1)[0]
    ref = ref.split("?", 1)[0]
    return ref


def validate_navigation(errors: list[str]) -> tuple[dict[str, Any], list[str], set[str]]:
    if (MINTLIFY_DIR / "mint.json").exists():
        errors.append("Mintlify source must use docs.json as the unique main config; remove mintlify/mint.json")
    config = load_json(MINTLIFY_DIR / "docs.json", errors)
    if config.get("$schema") != "https://mintlify.com/docs.json":
        errors.append('Mintlify docs.json $schema must be "https://mintlify.com/docs.json"')
    if config.get("theme") != "mint":
        errors.append('Mintlify config theme must be "mint"')
    colors = config.get("colors")
    if not isinstance(colors, dict) or not all(colors.get(key) for key in ("primary", "light", "dark")):
        errors.append("Mintlify docs.json colors.primary/light/dark are required")
    site_manifest_path = MINTLIFY_DIR / "site-manifest.json"
    site_manifest = load_json(site_manifest_path, errors) if site_manifest_path.exists() else {}
    latest_value = site_manifest.get("latest_version")
    has_latest_projection = isinstance(latest_value, str) and bool(latest_value.strip())
    navigation = config.get("navigation")
    versions = navigation.get("versions") if isinstance(navigation, dict) else None
    if not isinstance(versions, list) or not versions:
        errors.append("Mintlify docs.json navigation.versions must be a non-empty list")
    else:
        tabs = versions[0].get("tabs") if isinstance(versions[0], dict) else None
        tab_names = [str(tab.get("tab")) for tab in tabs if isinstance(tab, dict)] if isinstance(tabs, list) else []
        required_tabs = ["用户指南", "版本与公告", "文档治理"]
        if has_latest_projection:
            required_tabs.append("当前版本")
        for required_tab in required_tabs:
            if required_tab not in tab_names:
                errors.append(f"Mintlify docs.json navigation missing tab: {required_tab}")
    nav_pages = collect_navigation_pages(config)
    seen: set[str] = set()
    for page in nav_pages:
        if page in seen:
            errors.append(f"Mintlify navigation duplicates page: {page}")
        seen.add(page)
        if not page_path_from_ref(page).exists():
            errors.append(f"Mintlify navigation references missing page: {page}")
    required_pages = {
        "index",
        "guides/getting-started",
        "roles/admin",
        "roles/listener",
        "roles/operator",
        "tasks/music-library",
        "tasks/media-and-lyrics",
        "versions/index",
        "governance/public-boundary",
        "governance/site-governance",
    }
    if has_latest_projection:
        required_pages.update(
            {
                "docs/latest/overview",
                "docs/latest/web/index",
                "docs/latest/admin/index",
                "docs/latest/faq",
            }
        )
    missing_required = sorted(required_pages - set(nav_pages))
    if missing_required:
        errors.append("Mintlify navigation missing current-version pages: " + ", ".join(missing_required))
    return config, nav_pages, seen


def validate_links_and_images(nav_pages: set[str], errors: list[str]) -> None:
    all_pages = {site_page_ref(path): path for path in MINTLIFY_DIR.rglob("*.mdx")}
    for ref, path in all_pages.items():
        text = path.read_text(encoding="utf-8", errors="ignore")
        if ref.startswith("docs/latest/") and ref not in nav_pages:
            errors.append(f"latest page is not mounted in navigation: {ref}")
        for pattern in SENSITIVE_PATTERNS:
            if pattern.search(text):
                errors.append(f"Mintlify public file contains sensitive pattern {pattern.pattern}: {path.relative_to(ROOT)}")
        refs = [*MARKDOWN_LINK_PATTERN.findall(text), *MARKDOWN_IMAGE_PATTERN.findall(text), *MDX_HREF_PATTERN.findall(text)]
        for raw_ref in refs:
            target = normalize_ref(raw_ref)
            if not target or target.startswith(("http://", "https://", "mailto:", "tel:", "data:")):
                continue
            if target.startswith("/assets/screenshots/"):
                asset = MINTLIFY_DIR / target.removeprefix("/")
                if not asset.exists() or asset.is_dir():
                    errors.append(f"Mintlify page references missing image: {ref} -> {target}")
                continue
            if target.startswith("/"):
                target_path = page_path_from_ref(target)
            else:
                target_path = (path.parent / target).resolve()
                if target_path.suffix != ".mdx":
                    target_path = target_path.with_suffix(".mdx")
            try:
                target_path.relative_to(MINTLIFY_DIR.resolve())
            except ValueError:
                errors.append(f"Mintlify page references outside site root: {ref} -> {raw_ref}")
                continue
            if not target_path.exists():
                errors.append(f"Mintlify page has broken link: {ref} -> {raw_ref}")


def validate_site_manifest(errors: list[str]) -> None:
    manifest = load_json(MINTLIFY_DIR / "site-manifest.json", errors)
    latest_value = manifest.get("latest_version")
    latest_version = latest_value.strip() if isinstance(latest_value, str) else ""
    if not latest_version:
        versions = manifest.get("versions")
        projections = manifest.get("projections")
        if versions not in ([], None) or projections not in ([], None):
            errors.append("site-manifest.latest_version is required when versions or projections are present")
        return
    if not TIME_PATTERN.fullmatch(str(manifest.get("updated_at", ""))):
        errors.append("site-manifest.updated_at must be YYYY-MM-DD HH:mm:ss")
    versions = manifest.get("versions")
    if not isinstance(versions, list) or latest_version not in versions:
        errors.append("site-manifest.versions must include latest_version")
    latest_root = MINTLIFY_DIR / "docs" / "latest"
    version_root = MINTLIFY_DIR / "docs" / latest_version
    if not latest_root.exists() or not version_root.exists():
        errors.append("latest_version must have docs/latest and docs/<latest_version> directories")
        return
    latest_pages = sorted(path.relative_to(latest_root) for path in latest_root.rglob("*.mdx"))
    version_pages = sorted(path.relative_to(version_root) for path in version_root.rglob("*.mdx"))
    if latest_pages != version_pages:
        errors.append("docs/latest pages must match docs/<latest_version> pages")
    projections = manifest.get("projections")
    if not isinstance(projections, list) or not projections:
        errors.append("site-manifest.projections must be a non-empty list")
        return
    latest_projection = next(
        (item for item in projections if isinstance(item, dict) and item.get("source_release") == f"releases/{latest_version}"),
        None,
    )
    if not latest_projection:
        errors.append("site-manifest.projections must include latest_version projection")
        return
    if latest_projection.get("target_site_root") != f"mintlify/docs/{latest_version}":
        errors.append("latest projection target_site_root must match latest_version")
    if latest_projection.get("latest_target") != "mintlify/docs/latest":
        errors.append("latest projection latest_target must be mintlify/docs/latest")
    content_hashes = latest_projection.get("content_hashes")
    if not isinstance(content_hashes, dict):
        errors.append("latest projection content_hashes must be an object")
        return
    for page in version_pages:
        page_key = str(page).replace("\\", "/")
        expected = str(content_hashes.get(page_key, ""))
        if not expected:
            errors.append(f"latest projection content_hashes missing page: {page_key}")
            continue
        actual = file_sha256(version_root / page)
        if expected != actual:
            errors.append(f"latest projection content_hashes drift for page: {page_key}")


def validate_forbidden_files(errors: list[str]) -> None:
    for path in MINTLIFY_DIR.rglob("*"):
        if path.name in FORBIDDEN_NAMES or any(pattern.fullmatch(path.name) for pattern in FORBIDDEN_NAME_PATTERNS):
            errors.append(f"Mintlify contains forbidden file or build output: {path.relative_to(ROOT)}")
        if path.is_file():
            if path.suffix in FORBIDDEN_SUFFIXES:
                errors.append(f"Mintlify contains forbidden runtime file: {path.relative_to(ROOT)}")
            if path.stat().st_size > 5 * 1024 * 1024:
                errors.append(f"Mintlify file exceeds 5MB; use shared screenshots or external public assets: {path.relative_to(ROOT)}")


def validate_mintlify_site() -> list[str]:
    errors: list[str] = []
    if not MINTLIFY_DIR.exists():
        return ["missing directory: mintlify"]
    _, _, nav_page_set = validate_navigation(errors)
    validate_links_and_images(nav_page_set, errors)
    validate_site_manifest(errors)
    validate_forbidden_files(errors)
    return errors


def main() -> int:
    errors = validate_mintlify_site()
    if errors:
        print("Mintlify site validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("Mintlify site validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
