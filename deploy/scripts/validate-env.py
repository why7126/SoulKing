#!/usr/bin/env python3
"""Validate ProjectSoulKing deployment env files."""

from __future__ import annotations

import argparse
from pathlib import Path

EXAMPLE_TOKENS = ("change-me", "replace-with", "example.com")


def parse_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def looks_like_example(value: str) -> bool:
    lowered = value.lower()
    return any(token in lowered for token in EXAMPLE_TOKENS)


def validate(domain: str, environment: str, env_file: Path, profiles: set[str]) -> list[str]:
    errors: list[str] = []
    values = parse_env(env_file)
    expected_id = f"{domain}-{environment}"
    require(errors, values.get("SOULKING_DEPLOY_ENV_ID") == expected_id, f"SOULKING_DEPLOY_ENV_ID must be {expected_id}")

    for key in ("DATABASE_URL", "S3_ENDPOINT_URL", "S3_PUBLIC_ENDPOINT_URL", "S3_ACCESS_KEY_ID", "S3_SECRET_ACCESS_KEY", "S3_BUCKET_MUSIC"):
        require(errors, bool(values.get(key)), f"{key} is required")

    database_url = values.get("DATABASE_URL", "")
    require(errors, database_url.startswith("sqlite:///"), "ProjectSoulKing deploy matrix currently supports SQLite DATABASE_URL only")

    if environment == "sqlite-minio-managed":
        require(errors, "self-hosted-storage" in profiles, "sqlite-minio-managed requires self-hosted-storage profile")
        require(errors, values.get("S3_ENDPOINT_URL", "").startswith("http://soulking-minio:9000"), "managed MinIO must use http://soulking-minio:9000")
    else:
        require(errors, "self-hosted-storage" not in profiles, f"{environment} must not enable self-hosted-storage profile")

    if domain == "prod":
        require(errors, values.get("APP_ENV") == "production", "production APP_ENV must be production")
        require(errors, values.get("APP_DEBUG", "").lower() == "false", "production APP_DEBUG must be false")
        for key in ("ADMIN_PASSWORD", "S3_ENDPOINT_URL", "S3_PUBLIC_ENDPOINT_URL", "S3_ACCESS_KEY_ID", "S3_SECRET_ACCESS_KEY"):
            value = values.get(key, "")
            require(errors, bool(value) and not looks_like_example(value), f"production {key} must be replaced with a real value")
        require(errors, values.get("S3_SECURE", "").lower() == "true", "production S3_SECURE must be true")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate ProjectSoulKing deploy env.")
    parser.add_argument("--domain", required=True, choices=("local", "prod"))
    parser.add_argument("--environment", required=True)
    parser.add_argument("--env-file", required=True)
    parser.add_argument("--profile", action="append", default=[])
    args = parser.parse_args()

    env_file = Path(args.env_file)
    if not env_file.exists():
        print(f"Deploy env validation failed:\n  - missing env file: {env_file}")
        return 1

    errors = validate(args.domain, args.environment, env_file, set(args.profile))
    if errors:
        print("Deploy env validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"Deploy env validation passed: {env_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
