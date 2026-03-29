"""调用 Dify 工作流（blocking）并规范化输出的歌曲元数据建议。"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from typing import Any

_NAME_SPLIT = re.compile(r"[/、，,|；;]+")


def _post_json(url: str, headers: dict[str, str], body: dict, *, timeout: int = 120) -> dict[str, Any]:
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            detail = json.loads(raw)
            msg = detail.get("message") or detail.get("error") or raw[:800]
        except json.JSONDecodeError:
            msg = raw[:800] or str(e)
        raise ValueError(f"Dify API 返回错误（HTTP {e.code}）: {msg}") from e


def run_dify_workflow(*, api_url: str, api_key: str, inputs: dict[str, Any]) -> dict[str, Any]:
    body = {
        "inputs": inputs,
        "response_mode": "blocking",
        "user": "music-admin-metadata",
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    return _post_json(api_url.strip(), headers, body)


def extract_workflow_outputs(resp: dict[str, Any]) -> dict[str, Any]:
    """从 Dify blocking 响应中取出 outputs 字典。"""
    data = resp.get("data")
    if isinstance(data, dict):
        status = (data.get("status") or "").lower()
        if status == "failed":
            err = data.get("error") or data.get("message") or "unknown"
            raise ValueError(f"工作流执行失败: {err}")
        outs = data.get("outputs")
        if isinstance(outs, dict):
            return outs
    outs = resp.get("outputs")
    if isinstance(outs, dict):
        return outs
    return {}


def split_name_list(val: Any) -> list[str]:
    if val is None:
        return []
    if isinstance(val, bool):
        return []
    if isinstance(val, int):
        return [str(val)]
    if isinstance(val, float):
        return [str(int(val))] if val.is_integer() else [str(val)]
    if isinstance(val, list):
        out: list[str] = []
        for x in val:
            out.extend(split_name_list(x))
        return [s for s in (t.strip() for t in out) if s]
    s = str(val).strip()
    if not s:
        return []
    return [p.strip() for p in _NAME_SPLIT.split(s) if p.strip()]


def _maybe_parse_json_object(s: str) -> dict[str, Any] | None:
    s = s.strip()
    if not s or s[0] not in "{[":
        return None
    try:
        parsed: Any = json.loads(s)
    except json.JSONDecodeError:
        return None
    if isinstance(parsed, dict):
        return parsed
    return None


def _collect_dict_blobs(raw: dict[str, Any]) -> list[dict[str, Any]]:
    blobs: list[dict[str, Any]] = []
    for v in raw.values():
        if isinstance(v, dict):
            blobs.append(v)
        elif isinstance(v, str):
            obj = _maybe_parse_json_object(v)
            if obj is not None:
                blobs.append(obj)
    return blobs


def canonicalize_suggestions(merged: dict[str, Any]) -> dict[str, Any]:
    """统一为前端使用的键：lyricists, composers, languages, genres, tags, album, film_tv, release_date, duration_ms。"""
    out: dict[str, Any] = {}

    if "lyricists" in merged or "lyricist" in merged:
        names = split_name_list(merged.get("lyricists", merged.get("lyricist")))
        if names:
            out["lyricists"] = names
    if "composers" in merged or "composer" in merged:
        names = split_name_list(merged.get("composers", merged.get("composer")))
        if names:
            out["composers"] = names

    langs = merged.get("languages")
    if langs is None:
        langs = merged.get("language")
    if langs is not None:
        names = split_name_list(langs)
        if names:
            out["languages"] = names

    genres = merged.get("genres")
    if genres is None:
        genres = merged.get("genre")
    if genres is not None:
        names = split_name_list(genres)
        if names:
            out["genres"] = names

    if merged.get("tags") is not None:
        names = split_name_list(merged["tags"])
        if names:
            out["tags"] = names

    for k in ("album", "film_tv", "release_date"):
        v = merged.get(k)
        if v is None:
            continue
        t = str(v).strip()
        if t:
            out[k] = t

    if merged.get("duration_ms") is not None:
        try:
            dm = int(merged["duration_ms"])
            if dm >= 0:
                out["duration_ms"] = dm
        except (TypeError, ValueError):
            pass

    return out


def normalize_suggestions(raw_outputs: dict[str, Any]) -> dict[str, Any]:
    """合并 outputs 中的 JSON 对象与顶层字段，再规范化。"""
    merged: dict[str, Any] = {}
    for blob in _collect_dict_blobs(raw_outputs):
        merged.update(blob)
    known = (
        "lyricists",
        "lyricist",
        "composers",
        "composer",
        "languages",
        "language",
        "genres",
        "genre",
        "tags",
        "album",
        "film_tv",
        "release_date",
        "duration_ms",
    )
    for k in known:
        if k in raw_outputs and k not in merged:
            merged[k] = raw_outputs[k]
    return canonicalize_suggestions(merged)
