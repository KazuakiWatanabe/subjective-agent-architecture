"""POST /convert の E2E 挙動を検証するテストを提供する。

入出力: POST /convert({"text": ...}) -> schema準拠JSON。
制約:
    - 空入力は 400 を返す
    - 成功時は rollback_plan を含む schema 準拠JSONを返す

Note:
    - DEMO_URL がある場合は実URLに対して実行する
    - DEMO_URL 未指定時は TestClient でローカル実行する
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import jsonschema
import requests
from fastapi.testclient import TestClient

from services.api.main import app

BASE_URL = os.environ.get("DEMO_URL", "").strip()
SCHEMA_PATH = Path(__file__).parent.parent.parent / "src/contracts/state_intent.schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

PRESET_INPUT = "最近来店が減っている。値引きには反応しないが、限定感には反応する。"


def _post_convert(payload: dict[str, Any]) -> Any:
    """環境に応じて /convert へPOSTしレスポンスを返す。"""
    if BASE_URL:
        return requests.post(f"{BASE_URL}/convert", json=payload, timeout=10)

    client = TestClient(app)
    return client.post("/convert", json=payload)


def test_convert_returns_200():
    """通常入力で /convert が 200 を返すことを確認する。"""
    resp = _post_convert({"text": PRESET_INPUT})
    assert resp.status_code == 200


def test_convert_output_passes_schema():
    """通常入力で schema 検証を通過することを確認する。"""
    resp = _post_convert({"text": PRESET_INPUT})
    jsonschema.validate(resp.json(), SCHEMA)


def test_convert_state_has_three_or_more_items():
    """state が3件以上で返ることを確認する。"""
    resp = _post_convert({"text": PRESET_INPUT})
    assert len(resp.json()["state"]) >= 3


def test_convert_output_has_trace_id():
    """trace_id を含むことを確認する。"""
    resp = _post_convert({"text": PRESET_INPUT})
    assert "trace_id" in resp.json()


def test_convert_output_has_rollback_plan():
    """rollback_plan を含むことを確認する。"""
    resp = _post_convert({"text": PRESET_INPUT})
    assert "rollback_plan" in resp.json()


def test_convert_output_has_action_bindings():
    """action_bindings を含み、1件以上あることを確認する。"""
    resp = _post_convert({"text": PRESET_INPUT})
    body = resp.json()
    assert "action_bindings" in body
    assert len(body["action_bindings"]) >= 1


def test_convert_action_bindings_all_dry_run():
    """Phase 0 制約として全 binding が dry_run=true であることを確認する。"""
    resp = _post_convert({"text": PRESET_INPUT})
    for binding in resp.json()["action_bindings"]:
        assert binding["dry_run"] is True


def test_convert_empty_input_returns_400():
    """空入力時は 400 を返すことを確認する。"""
    resp = _post_convert({"text": ""})
    assert resp.status_code == 400


def test_convert_stable_output_10_times():
    """10回実行して8回以上 schema を通過することを確認する。"""
    pass_count = 0
    for _ in range(10):
        resp = _post_convert({"text": PRESET_INPUT})
        try:
            jsonschema.validate(resp.json(), SCHEMA)
            pass_count += 1
        except Exception:
            pass

    assert pass_count >= 8, f"安定率不足: {pass_count}/10"
