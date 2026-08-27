#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MINIAPP = ROOT / "src" / "miniapp"
ENV_TS = MINIAPP / "utils" / "env.ts"
ENV_JS = MINIAPP / "utils" / "env.js"
PROJECT_PRIVATE_CONFIG = MINIAPP / "project.private.config.json"
README = MINIAPP / "README.md"
PRODUCTION_BASE_URL = "https://example.invalid"
DEVELOPMENT_BASE_URL = "http://127.0.0.1:8010"
DEVELOPMENT_FALLBACKS = ["http://localhost:8010", "http://localhost:8000"]
DEFAULT_STRATEGY = "auto"
VALID_STRATEGIES = {"dev", "prod", "auto"}


@dataclass(frozen=True)
class StrategyTemplate:
    ts_body: str
    js_body: str
    marker: str


def _strategy_template(strategy: str) -> StrategyTemplate:
    if strategy not in VALID_STRATEGIES:
        raise ValueError(f"invalid strategy: {strategy}")

    if strategy == "dev":
        ts_resolver = "return 'development';"
        js_resolver = "return 'development';"
        marker = "return 'development'"
    elif strategy == "prod":
        ts_resolver = "return 'production';"
        js_resolver = "return 'production';"
        marker = "return 'production'"
    else:
        ts_resolver = (
            "try {\n"
            "    const accountInfo = wx.getAccountInfoSync();\n"
            "    return accountInfo.miniProgram.envVersion === 'develop' ? 'development' : 'production';\n"
            "  } catch (error) {\n"
            "    return 'development';\n"
            "  }"
        )
        js_resolver = (
            "try {\n"
            "    const accountInfo = wx.getAccountInfoSync();\n"
            "    return accountInfo.miniProgram.envVersion === 'develop' ? 'development' : 'production';\n"
            "  } catch (error) {\n"
            "    return 'development';\n"
            "  }"
        )
        marker = "envVersion === 'develop' ? 'development' : 'production'"

    return StrategyTemplate(
        ts_body=_render_ts(ts_resolver),
        js_body=_render_js(js_resolver),
        marker=marker,
    )


def _render_ts(resolver: str) -> str:
    fallback_values = ", ".join(f"'{item}'" for item in DEVELOPMENT_FALLBACKS)
    return f"""export type MiniappEnvironment = 'development' | 'production';

export type MiniappApiConfig = {{
  environment: MiniappEnvironment;
  apiBaseUrl: string;
  apiFallbackBaseUrls: string[];
}};

export const MINIAPP_API_CONFIGS: Record<MiniappEnvironment, MiniappApiConfig> = {{
  development: {{
    environment: 'development',
    apiBaseUrl: '{DEVELOPMENT_BASE_URL}',
    apiFallbackBaseUrls: [{fallback_values}],
  }},
  production: {{
    environment: 'production',
    apiBaseUrl: '{PRODUCTION_BASE_URL}',
    apiFallbackBaseUrls: [],
  }},
}};

export function resolveMiniappEnvironment(): MiniappEnvironment {{
  {resolver}
}}

export function resolveMiniappApiConfig(environment = resolveMiniappEnvironment()): MiniappApiConfig {{
  return MINIAPP_API_CONFIGS[environment];
}}

export const miniappApiConfig = resolveMiniappApiConfig();
"""


def _render_js(resolver: str) -> str:
    fallback_values = ", ".join(f"'{item}'" for item in DEVELOPMENT_FALLBACKS)
    return f"""const MINIAPP_API_CONFIGS = {{
  development: {{
    environment: 'development',
    apiBaseUrl: '{DEVELOPMENT_BASE_URL}',
    apiFallbackBaseUrls: [{fallback_values}],
  }},
  production: {{
    environment: 'production',
    apiBaseUrl: '{PRODUCTION_BASE_URL}',
    apiFallbackBaseUrls: [],
  }},
}};

function resolveMiniappEnvironment() {{
  {resolver}
}}

function resolveMiniappApiConfig(environment = resolveMiniappEnvironment()) {{
  return MINIAPP_API_CONFIGS[environment];
}}

const miniappApiConfig = resolveMiniappApiConfig();

module.exports = {{
  MINIAPP_API_CONFIGS,
  resolveMiniappEnvironment,
  resolveMiniappApiConfig,
  miniappApiConfig,
}};
"""


def detect_strategy() -> str:
    if not ENV_TS.exists() or not ENV_JS.exists():
        return "missing"
    ts = ENV_TS.read_text(encoding="utf-8")
    js = ENV_JS.read_text(encoding="utf-8")
    for strategy in ["auto", "prod", "dev"]:
        marker = _strategy_template(strategy).marker
        if marker in ts and marker in js:
            return strategy
    return "unknown"


def check_state(*, smoke: bool = False) -> dict[str, Any]:
    ts = ENV_TS.read_text(encoding="utf-8") if ENV_TS.exists() else ""
    js = ENV_JS.read_text(encoding="utf-8") if ENV_JS.exists() else ""
    strategy = detect_strategy()
    private_config = _read_project_private_config()
    result: dict[str, Any] = {
        "strategy": strategy,
        "files": {
            "ts_exists": ENV_TS.exists(),
            "js_exists": ENV_JS.exists(),
            "ts_js_strategy_match": strategy in VALID_STRATEGIES,
        },
        "devtools": {
            "private_config_exists": PROJECT_PRIVATE_CONFIG.exists(),
            "urlCheck": private_config.get("setting", {}).get("urlCheck"),
            "expected_urlCheck": True if strategy == "prod" else False,
            "urlCheck_matches_strategy": private_config.get("setting", {}).get("urlCheck") is (True if strategy == "prod" else False),
        },
        "development": {
            "apiBaseUrl": DEVELOPMENT_BASE_URL,
            "apiFallbackBaseUrls": DEVELOPMENT_FALLBACKS,
            "present_in_ts": DEVELOPMENT_BASE_URL in ts,
            "present_in_js": DEVELOPMENT_BASE_URL in js,
        },
        "production": {
            "apiBaseUrl": PRODUCTION_BASE_URL,
            "present_in_ts": PRODUCTION_BASE_URL in ts,
            "present_in_js": PRODUCTION_BASE_URL in js,
        },
        "smoke": [],
        "ok": strategy in VALID_STRATEGIES
        and PRODUCTION_BASE_URL in ts
        and PRODUCTION_BASE_URL in js
        and private_config.get("setting", {}).get("urlCheck") is (True if strategy == "prod" else False),
    }
    if smoke:
        smoke_results = [
            _smoke_url(f"{PRODUCTION_BASE_URL}/api/v1/miniapp/home"),
            _smoke_url(f"{PRODUCTION_BASE_URL}/api/v1/miniapp/brands?page=1&pageSize=2"),
        ]
        result["smoke"] = smoke_results
        result["ok"] = bool(result["ok"] and all(item["ok"] for item in smoke_results))
    return result


def _smoke_url(url: str) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            body = response.read().decode("utf-8")
            status = response.status
    except urllib.error.HTTPError as error:
        return {"url": url, "ok": False, "status": error.code, "error": str(error)}
    except urllib.error.URLError as error:
        return {"url": url, "ok": False, "status": None, "error": str(error)}

    payload_ok = False
    try:
        payload = json.loads(body)
        payload_ok = payload.get("code") == 0
    except json.JSONDecodeError:
        payload_ok = False
    return {"url": url, "ok": status == 200 and payload_ok, "status": status, "code_ok": payload_ok}


def set_strategy(strategy: str) -> dict[str, Any]:
    template = _strategy_template(strategy)
    ENV_TS.parent.mkdir(parents=True, exist_ok=True)
    ENV_TS.write_text(template.ts_body, encoding="utf-8")
    ENV_JS.write_text(template.js_body, encoding="utf-8")
    _set_devtools_url_check(strategy == "prod")
    return check_state(smoke=False)


def _read_project_private_config() -> dict[str, Any]:
    if not PROJECT_PRIVATE_CONFIG.exists():
        return {}
    try:
        payload = json.loads(PROJECT_PRIVATE_CONFIG.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _set_devtools_url_check(enabled: bool) -> None:
    payload = _read_project_private_config()
    payload.setdefault("setting", {})
    if not isinstance(payload["setting"], dict):
        payload["setting"] = {}
    payload["setting"]["urlCheck"] = enabled
    PROJECT_PRIVATE_CONFIG.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_static_tests() -> dict[str, Any]:
    command = ["uv", "run", "pytest", "tests/test_miniapp_static.py"]
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    return {
        "command": " ".join(command),
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "stdout_tail": "\n".join(completed.stdout.splitlines()[-8:]),
        "stderr_tail": "\n".join(completed.stderr.splitlines()[-8:]),
    }


def checklist() -> list[str]:
    return [
        "微信公众平台 request 合法域名包含 ProjectSoulKing 小程序生产域名",
        "微信开发者工具重新上传开发版本",
        "微信公众平台版本管理中将最新开发版本设为体验版",
        "手机删除旧体验版入口后重新扫码最新体验版二维码",
        "体验版首页、分类、品牌、证书、商品详情完成冒烟验证",
    ]


def command_set(args: argparse.Namespace) -> int:
    result = set_strategy(args.strategy)
    _print_json({"action": "set", **result})
    return 0 if result["ok"] else 1


def command_check(args: argparse.Namespace) -> int:
    result = check_state(smoke=args.smoke)
    _print_json({"action": "check", **result})
    return 0 if result["ok"] else 1


def command_prepare(args: argparse.Namespace) -> int:
    state = set_strategy("prod")
    tests = None if args.skip_tests else run_static_tests()
    smoke = check_state(smoke=True)
    ok = bool(state["ok"] and smoke["ok"] and (tests is None or tests["ok"]))
    _print_json(
        {
            "action": "prepare",
            "ok": ok,
            "strategy": "prod",
            "state": state,
            "tests": tests,
            "smoke": smoke["smoke"],
            "checklist": checklist(),
            "next": "/miniapp-confirm 或 /miniapp-restore",
        }
    )
    return 0 if ok else 1


def command_confirm(args: argparse.Namespace) -> int:
    result = {
        "action": "confirm",
        "ok": True,
        "channel": args.channel,
        "version": args.version,
        "result": args.result,
        "notes": args.notes,
        "safe_record": "请将此摘要复制到 release 或 Sprint 验收记录；不要记录微信会话密钥、Cookie、Authorization header 或 .env 内容。",
        "next": "/miniapp-restore",
    }
    _print_json(result)
    return 0


def command_restore(args: argparse.Namespace) -> int:
    result = set_strategy(args.strategy)
    _print_json({"action": "restore", **result})
    return 0 if result["ok"] else 1


def _print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage miniapp API environment strategy.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    set_parser = subparsers.add_parser("set")
    set_parser.add_argument("strategy", choices=sorted(VALID_STRATEGIES))
    set_parser.set_defaults(func=command_set)

    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("--smoke", action="store_true")
    check_parser.set_defaults(func=command_check)

    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("--skip-tests", action="store_true")
    prepare_parser.set_defaults(func=command_prepare)

    confirm_parser = subparsers.add_parser("confirm")
    confirm_parser.add_argument("--channel", choices=["trial", "release"], required=True)
    confirm_parser.add_argument("--version", required=True)
    confirm_parser.add_argument("--result", choices=["passed", "blocked", "follow_up"], default="passed")
    confirm_parser.add_argument("--notes", default="")
    confirm_parser.set_defaults(func=command_confirm)

    restore_parser = subparsers.add_parser("restore")
    restore_parser.add_argument("--strategy", choices=sorted(VALID_STRATEGIES), default=DEFAULT_STRATEGY)
    restore_parser.set_defaults(func=command_restore)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
