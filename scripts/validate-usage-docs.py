#!/usr/bin/env python3
"""Validate versioned product usage docs for a release."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RELEASES_DIR = ROOT / "releases"
MINTLIFY_DIR = ROOT / "mintlify"
TIME_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")
MARKDOWN_IMAGE_PATTERN = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
PROTOTYPE_SCREENSHOT_PATTERN = re.compile(r"(?:\bprototype\b|原型)", re.I)
ALLOWED_SCREENSHOT_SOURCE_TYPES = {
    "runtime_system",
    "qa_system",
    "accepted_system_evidence",
    "manual_system_capture",
}

SENSITIVE_PATTERNS = (
    re.compile(r"\bAPP_SECRET_KEY\s*=", re.I),
    re.compile(r"\bDATABASE_URL\s*=", re.I),
    re.compile(r"mysql(\+\w+)?://", re.I),
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
        errors.append(f"missing file: {path}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON {path}: {exc}")
        return {}
    if not isinstance(data, dict):
        errors.append(f"{path} must contain a JSON object")
        return {}
    return data


def release_dir(version: str) -> Path:
    return RELEASES_DIR / version


def nav_pages_from_config(path: Path) -> set[str]:
    errors: list[str] = []
    data = load_json(path, errors)
    pages: set[str] = set()

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                if key == "pages" and isinstance(nested, list):
                    for page in nested:
                        if isinstance(page, str):
                            pages.add(page)
                        else:
                            visit(page)
                else:
                    visit(nested)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    visit(data)
    return pages


def release_docs_pages(releases_dir: Path) -> set[str]:
    docs_path = releases_dir / "docs.json"
    if docs_path.exists():
        return nav_pages_from_config(docs_path)
    mint_path = releases_dir / "mint.json"
    if mint_path.exists():
        return nav_pages_from_config(mint_path)
    return set()


def mintlify_pages(site_root: Path | None = None) -> set[str]:
    site_root = site_root or MINTLIFY_DIR
    docs_path = site_root / "docs.json"
    if docs_path.exists():
        return nav_pages_from_config(docs_path)
    mint_path = site_root / "mint.json"
    if mint_path.exists():
        return nav_pages_from_config(mint_path)
    return set()


def scan_files(paths: list[Path], errors: list[str]) -> None:
    for path in paths:
        if not path.exists() or path.is_dir():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SENSITIVE_PATTERNS:
            if pattern.search(text):
                errors.append(f"public usage docs input contains sensitive pattern {pattern.pattern}: {path}")


def path_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repo_relative(path: Path, release_dir: Path | None = None) -> str:
    bases = [ROOT]
    if release_dir is not None:
        bases.append(release_dir.parent.parent)
    for base in bases:
        try:
            return str(path.relative_to(base)).replace("\\", "/")
        except ValueError:
            continue
    return str(path)


def validate_manual_overrides(manifest: dict[str, Any], errors: list[str]) -> None:
    overrides = manifest.get("manual_overrides", [])
    if not isinstance(overrides, list):
        errors.append("manifest.manual_overrides must be a list")
        return
    for index, item in enumerate(overrides):
        if not isinstance(item, dict):
            errors.append(f"manifest.manual_overrides[{index}] must be an object")
            continue
        if item.get("change_type") == "content_correction" and item.get("authorized") is not True:
            errors.append(f"manifest.manual_overrides[{index}] content_correction requires authorized=true")
        for key in ("reason", "confirmed_by", "confirmed_at", "files", "summary"):
            if item.get("change_type") == "content_correction" and not item.get(key):
                errors.append(f"manifest.manual_overrides[{index}] content_correction requires {key}")


def page_image_refs(page_path: Path, usage_dir: Path) -> list[str]:
    refs: list[str] = []
    text = page_path.read_text(encoding="utf-8", errors="ignore")
    for match in MARKDOWN_IMAGE_PATTERN.finditer(text):
        raw_ref = match.group(1).strip().split()[0].strip("<>")
        if raw_ref.startswith("//assets/screenshots/"):
            raw_ref = raw_ref[1:]
        if raw_ref.startswith(("http://", "https://", "data:")):
            refs.append(raw_ref)
            continue
        if raw_ref.startswith("/assets/screenshots/"):
            refs.append("mintlify" + raw_ref)
            continue
        resolved = (page_path.parent / raw_ref).resolve()
        try:
            refs.append(str(resolved.relative_to(usage_dir.resolve())).replace("\\", "/"))
        except ValueError:
            try:
                refs.append(str(resolved.relative_to(ROOT.resolve())).replace("\\", "/"))
            except ValueError:
                refs.append(raw_ref)
    return refs


def validate_screenshots(manifest: dict[str, Any], usage_dir: Path, pages: list[str], errors: list[str]) -> None:
    screenshots = manifest.get("screenshots")
    if not isinstance(screenshots, list) or not screenshots:
        errors.append("manifest.screenshots must be a non-empty list for generated usage docs")
        return

    declared_paths: set[str] = set()
    declared_pages: set[str] = set()
    for index, item in enumerate(screenshots):
        if not isinstance(item, dict):
            errors.append(f"manifest.screenshots[{index}] must be an object")
            continue
        path_value = str(item.get("path", "")).strip()
        if not path_value:
            errors.append(f"manifest.screenshots[{index}].path is required")
            continue
        source_type = str(item.get("source_type", "")).strip()
        if source_type not in ALLOWED_SCREENSHOT_SOURCE_TYPES:
            errors.append(
                f"manifest.screenshots[{index}].source_type must be one of "
                + ", ".join(sorted(ALLOWED_SCREENSHOT_SOURCE_TYPES))
            )
        source_value = str(item.get("source", "")).strip()
        if not source_value:
            errors.append(f"manifest.screenshots[{index}].source is required")
        for key, value in item.items():
            if isinstance(value, str) and PROTOTYPE_SCREENSHOT_PATTERN.search(value):
                errors.append(
                    f"manifest.screenshots[{index}].{key} must reference a real system screenshot, not a prototype"
                )
        site_asset = str(item.get("site_asset", "")).strip()
        if path_value.startswith(("http://", "https://", "data:")):
            errors.append(f"manifest.screenshots[{index}].path must be /assets/screenshots/<file> or a legacy usage-docs relative path: {path_value}")
            continue
        if path_value.startswith("/assets/screenshots/"):
            path_key = "mintlify" + path_value
            screenshot_path = ROOT / path_key
        else:
            path_key = path_value
            screenshot_path = usage_dir / path_value
            if path_value.startswith("assets/"):
                errors.append(
                    f"manifest.screenshots[{index}].path must use shared Mintlify asset, not release-local assets: {path_value}"
                )
        if not screenshot_path.exists() or screenshot_path.is_dir():
            errors.append(f"manifest.screenshots[{index}].path missing file: {path_value}")
        content_hash = str(item.get("content_hash", "")).strip()
        if content_hash and screenshot_path.exists() and not screenshot_path.is_dir() and path_sha256(screenshot_path) != content_hash:
            errors.append(f"manifest.screenshots[{index}].content_hash does not match file: {path_value}")
        if not site_asset:
            errors.append(f"manifest.screenshots[{index}].site_asset is required and must point to shared Mintlify screenshots")
        elif not site_asset.startswith("mintlify/assets/screenshots/"):
            errors.append(f"manifest.screenshots[{index}].site_asset must be under mintlify/assets/screenshots/: {site_asset}")
        else:
            asset_path = ROOT / site_asset
            if not asset_path.exists() or asset_path.is_dir():
                errors.append(f"manifest.screenshots[{index}].site_asset missing file: {site_asset}")
            elif content_hash and path_sha256(asset_path) != content_hash:
                errors.append(f"manifest.screenshots[{index}].site_asset hash does not match content_hash: {site_asset}")
            if path_value.startswith("/assets/screenshots/") and path_key != site_asset:
                errors.append(f"manifest.screenshots[{index}].path must match site_asset public path: {path_value}")
            for key in ("first_used_in", "used_by_versions", "covered_pages", "reuse_reason"):
                if key not in item:
                    errors.append(f"manifest.screenshots[{index}].{key} is required for shared screenshot assets")
        declared_paths.add(path_key)

        item_pages = item.get("pages")
        if not isinstance(item_pages, list) or not item_pages:
            errors.append(f"manifest.screenshots[{index}].pages must be a non-empty list")
        else:
            for page in item_pages:
                page_text = str(page)
                if page_text not in pages:
                    errors.append(f"manifest.screenshots[{index}].pages references unknown page: {page_text}")
                declared_pages.add(page_text)

    page_refs: dict[str, list[str]] = {}
    for page in pages:
        refs = page_image_refs(usage_dir / page, usage_dir)
        page_refs[page] = refs
        if not refs:
            errors.append(f"usage docs page must include at least one system screenshot: {page}")
        for ref in refs:
            if ref.startswith(("http://", "https://", "data:")):
                errors.append(f"usage docs screenshot must be a local release asset: {page} -> {ref}")
            elif ref not in declared_paths:
                errors.append(f"usage docs page references screenshot not declared in manifest: {page} -> {ref}")

    for page in pages:
        if page not in declared_pages:
            errors.append(f"manifest.screenshots must cover page: {page}")


def validate_site_projection(version: str, rdir: Path, usage_dir: Path, manifest: dict[str, Any], pages: list[str], errors: list[str]) -> None:
    projection = manifest.get("site_projection")
    if not isinstance(projection, dict):
        return
    if projection.get("status") != "synced":
        errors.append("manifest.site_projection.status must be synced when site_projection is present")
    for key in ("source_release", "source_manifest", "target_site_root", "latest_target", "synced_at", "mode", "content_hashes"):
        if key not in projection:
            errors.append(f"manifest.site_projection.{key} is required")
    if projection.get("source_release") != repo_relative(rdir, rdir):
        errors.append("manifest.site_projection.source_release must match release directory")
    if projection.get("source_manifest") != repo_relative(usage_dir / "manifest.json", rdir):
        errors.append("manifest.site_projection.source_manifest must match usage docs manifest")
    if not TIME_PATTERN.fullmatch(str(projection.get("synced_at", ""))):
        errors.append("manifest.site_projection.synced_at must be YYYY-MM-DD HH:mm:ss")
    target_root = ROOT / str(projection.get("target_site_root", ""))
    latest_root = ROOT / str(projection.get("latest_target", ""))
    latest_version = None
    site_manifest_path = MINTLIFY_DIR / "site-manifest.json"
    if site_manifest_path.exists():
        site_manifest = load_json(site_manifest_path, errors)
        latest_version = site_manifest.get("latest_version")
    for root_label, root_path in (("target_site_root", target_root), ("latest_target", latest_root)):
        if not root_path.exists() or not root_path.is_dir():
            errors.append(f"manifest.site_projection.{root_label} missing directory: {root_path}")
            continue
        actual_pages = sorted(str(path.relative_to(root_path)).replace("\\", "/") for path in root_path.rglob("*.mdx"))
        if root_label == "latest_target" and latest_version and latest_version != version:
            continue
        if sorted(pages) != actual_pages:
            errors.append(f"manifest.site_projection.{root_label} pages must match usage docs pages")
    content_hashes = projection.get("content_hashes")
    if not isinstance(content_hashes, dict):
        errors.append("manifest.site_projection.content_hashes must be an object")
    else:
        for page in pages:
            site_page = target_root / page
            expected = str(content_hashes.get(page, ""))
            if not expected:
                errors.append(f"manifest.site_projection.content_hashes missing page: {page}")
            elif site_page.exists() and hashlib.sha256(site_page.read_bytes()).hexdigest() != expected:
                errors.append(f"manifest.site_projection.content_hashes drift for page: {page}")

    site_nav_pages = mintlify_pages()
    missing_site_nav = [f"docs/{version}/{page.removesuffix('.mdx')}" for page in pages if f"docs/{version}/{page.removesuffix('.mdx')}" not in site_nav_pages]
    if missing_site_nav:
        errors.append("Mintlify site navigation missing projected pages: " + ", ".join(missing_site_nav))
    if pages and "docs/latest/overview" not in site_nav_pages:
        errors.append("Mintlify site navigation missing latest overview: docs/latest/overview")
    announcement = MINTLIFY_DIR / "releases" / version / "announcement.mdx"
    if not announcement.exists():
        errors.append(f"Mintlify release announcement projection missing: {announcement}")


def validate_generated_usage_docs(release_path: Path, release_data: dict[str, Any], usage_docs: dict[str, Any], errors: list[str]) -> None:
    rdir = release_path.parent
    version = str(release_data.get("version", ""))
    root_name = str(usage_docs.get("root") or "usage-docs")
    manifest_name = str(usage_docs.get("manifest") or f"{root_name}/manifest.json")
    usage_dir = rdir / root_name
    manifest_path = rdir / manifest_name
    if not usage_dir.exists():
        errors.append(f"usage_docs.status generated requires directory: {usage_dir}")
        return
    if (usage_dir / "assets").exists():
        errors.append("usage docs release snapshot must not contain usage-docs/assets; use mintlify/assets/screenshots and manifest.site_asset")

    manifest = load_json(manifest_path, errors)
    if not manifest:
        return
    for key in ("version", "generated_at", "source_release", "input_files", "pages", "coverage", "screenshots", "manual_overrides", "automation_policy"):
        if key not in manifest:
            errors.append(f"manifest.{key} is required")
    if manifest.get("version") != version:
        errors.append("manifest.version must match release version")
    if not TIME_PATTERN.fullmatch(str(manifest.get("generated_at", ""))):
        errors.append("manifest.generated_at must be YYYY-MM-DD HH:mm:ss")
    if not isinstance(manifest.get("input_files"), list):
        errors.append("manifest.input_files must be a list")
    pages = manifest.get("pages")
    if not isinstance(pages, list) or not pages:
        errors.append("manifest.pages must be a non-empty list")
        pages = []
    source_version = str(manifest.get("source_version", "") or "")
    if source_version and source_version != version:
        previous_manifest_path = RELEASES_DIR / source_version / "usage-docs" / "manifest.json"
        if previous_manifest_path.exists():
            previous_manifest = load_json(previous_manifest_path, errors)
            previous_pages = previous_manifest.get("pages", [])
            if isinstance(previous_pages, list):
                missing_previous_pages = sorted(str(page) for page in previous_pages if str(page) not in pages)
                if missing_previous_pages:
                    errors.append(
                        "current usage docs must include all previous-version pages from "
                        f"{source_version}: " + ", ".join(missing_previous_pages)
                    )
    actual_pages = sorted(str(path.relative_to(usage_dir)).replace("\\", "/") for path in usage_dir.rglob("*.mdx"))
    if sorted(pages) != actual_pages:
        errors.append("manifest.pages must match actual usage-docs .mdx files")
    validate_screenshots(manifest, usage_dir, [str(page) for page in pages], errors)
    validate_site_projection(version, rdir, usage_dir, manifest, [str(page) for page in pages], errors)

    nav_pages = release_docs_pages(rdir.parent)
    missing_nav = []
    for page in pages:
        page_ref = f"{version}/{root_name}/{str(page).removesuffix('.mdx')}"
        if page_ref not in nav_pages:
            missing_nav.append(page_ref)
    if missing_nav:
        errors.append("Mintlify navigation missing usage docs pages: " + ", ".join(missing_nav))

    coverage = manifest.get("coverage")
    if not isinstance(coverage, dict):
        errors.append("manifest.coverage must be an object")
    else:
        for key in ("web_public", "web_admin", "media", "release_impact_scope"):
            if key not in coverage:
                errors.append(f"manifest.coverage.{key} is required")

    policy = manifest.get("automation_policy")
    if not isinstance(policy, dict):
        errors.append("manifest.automation_policy must be an object")
    elif policy.get("content_corrections_require_authorization") is not True:
        errors.append("manifest.automation_policy.content_corrections_require_authorization must be true")
    validate_manual_overrides(manifest, errors)

    files_to_scan = [
        release_path,
        rdir / str(release_data.get("announcement", "announcement.mdx")),
        rdir.parent / "docs.json",
        MINTLIFY_DIR / "docs.json",
        MINTLIFY_DIR / "site-manifest.json",
        manifest_path,
    ]
    files_to_scan.extend(usage_dir.rglob("*.mdx"))
    if MINTLIFY_DIR.exists():
        files_to_scan.extend(MINTLIFY_DIR.rglob("*.mdx"))
    scan_files(files_to_scan, errors)


def validate_skipped_usage_docs(release_path: Path, usage_docs: dict[str, Any], errors: list[str]) -> None:
    rdir = release_path.parent
    root_name = str(usage_docs.get("root") or "usage-docs")
    if (rdir / root_name).exists():
        errors.append("usage_docs.status skipped must not create an empty usage-docs directory")
    decision = usage_docs.get("generation_decision")
    if not isinstance(decision, dict):
        errors.append("usage_docs.generation_decision is required when skipped")
        return
    if decision.get("required") is not False:
        errors.append("usage_docs.generation_decision.required must be false when skipped")
    for key in ("confirmed_at", "confirmed_by", "rationale"):
        if not decision.get(key):
            errors.append(f"usage_docs.generation_decision.{key} is required when skipped")
    if not TIME_PATTERN.fullmatch(str(decision.get("confirmed_at", ""))):
        errors.append("usage_docs.generation_decision.confirmed_at must be YYYY-MM-DD HH:mm:ss")


def validate_release_usage_docs(release_path: Path) -> list[str]:
    errors: list[str] = []
    release_data = load_json(release_path, errors)
    if errors:
        return errors
    usage_docs = release_data.get("usage_docs")
    if not isinstance(usage_docs, dict):
        return ["usage_docs object is required for usage-docs governed releases"]
    status = str(usage_docs.get("status", "")).lower()
    gates = release_data.get("gates")
    gate = gates.get("usage_docs_preview") if isinstance(gates, dict) else None
    if not isinstance(gate, dict):
        errors.append("gate usage_docs_preview is required")

    if status == "generated":
        if isinstance(gate, dict) and str(gate.get("status", "")).lower() != "pass":
            errors.append("usage_docs.status generated requires gate usage_docs_preview status pass")
        if isinstance(gate, dict) and not gate.get("evidence"):
            errors.append("gate usage_docs_preview pass requires evidence")
        validate_generated_usage_docs(release_path, release_data, usage_docs, errors)
    elif status == "skipped":
        if isinstance(gate, dict) and str(gate.get("status", "")).lower() != "na":
            errors.append("usage_docs.status skipped requires gate usage_docs_preview status na")
        if isinstance(gate, dict) and not gate.get("rationale"):
            errors.append("gate usage_docs_preview na requires rationale")
        validate_skipped_usage_docs(release_path, usage_docs, errors)
    elif status == "pending_confirmation":
        version = str(release_data.get("version", "<version>"))
        errors.append(
            "usage_docs.status pending_confirmation blocks release readiness; "
            "confirm whether current-version usage docs are required. "
            f"If needed, set usage_docs.generation_decision.required=true and run "
            f"`python scripts/generate-usage-docs.py {version}`; "
            f"if not needed, run "
            f"`python scripts/generate-usage-docs.py {version} --skip --confirmed-by operator "
            f"--rationale \"<why usage docs are not needed for this release>\"`."
        )
    else:
        errors.append("usage_docs.status must be generated, skipped, or pending_confirmation")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate versioned product usage docs.")
    parser.add_argument("--release-dir", required=True, help="Release directory such as releases/v0.3.2")
    args = parser.parse_args()
    release_path = Path(args.release_dir).resolve() / "release.json"
    errors = validate_release_usage_docs(release_path)
    if errors:
        print("Usage docs validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"Usage docs validation passed: {release_path.parent}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
