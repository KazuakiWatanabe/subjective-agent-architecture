"""ヘルスチェックエンドポイントの疎通を検証するテストを提供する。

入出力: GET /health -> HTTPレスポンス。
制約:
    - ステータスコードは 200
    - レスポンスJSONは {"status":"ok"} を含む

Note:
    - DEMO_URL がある場合は実URLを検証する
    - DEMO_URL 未指定時は TestClient でローカル検証する
"""

from __future__ import annotations

import os
from typing import Any

import requests
from fastapi.testclient import TestClient

from services.api.main import app

BASE_URL = os.environ.get("DEMO_URL", "").strip()


def _get_health_response() -> Any:
    """環境に応じて /health のレスポンスを取得する。

    Returns:
        Any: requests.Response または TestClient のレスポンス
    """
    if BASE_URL:
        return requests.get(f"{BASE_URL}/health", timeout=10)

    client = TestClient(app)
    return client.get("/health")


def test_health_endpoint_returns_200():
    """GET /health が 200 を返すことを確認する。"""
    resp = _get_health_response()
    assert resp.status_code == 200


def test_health_response_has_status_ok():
    """GET /health のJSONが status=ok を返すことを確認する。"""
    resp = _get_health_response()
    assert resp.json().get("status") == "ok"
