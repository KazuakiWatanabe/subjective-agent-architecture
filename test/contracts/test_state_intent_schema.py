"""state_intent スキーマの契約テスト。

観点:
    - JSON Schema(Draft7) としての妥当性
    - 必須項目と各種制約(minItems/range)の固定
    - 正常/異常ペイロードでの検証動作
"""

import json
from pathlib import Path

import jsonschema
import pytest

SCHEMA_PATH = Path(__file__).parent.parent.parent / "src/contracts/state_intent.schema.json"


@pytest.fixture
def schema():
    """検証対象の JSON Schema を読み込む。"""
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_schema_file_exists():
    """スキーマファイルが存在することを確認する。"""
    assert SCHEMA_PATH.exists()


def test_schema_is_valid_json_schema(schema):
    """JSON Schema として正しい構造であることを確認する。"""
    jsonschema.Draft7Validator.check_schema(schema)


def test_required_fields_defined(schema):
    """必須フィールドが定義されていることを確認する。"""
    # required の固定セットを契約として維持する。
    required = schema.get("required", [])
    for field in [
        "state",
        "intent",
        "next_actions",
        "confidence",
        "trace_id",
        "rollback_plan",
        "action_bindings",
    ]:
        assert field in required


def test_state_min_items(schema):
    """state に最小件数制約があることを確認する。"""
    assert schema["properties"]["state"]["minItems"] == 3


def test_next_actions_min_items(schema):
    """next_actions に最小件数制約があることを確認する。"""
    assert schema["properties"]["next_actions"]["minItems"] == 3


def test_confidence_range(schema):
    """confidence の範囲制約を確認する。"""
    conf = schema["properties"]["confidence"]
    assert conf["minimum"] == 0
    assert conf["maximum"] == 1


def test_action_bindings_min_items(schema):
    """action_bindings に最小件数制約があることを確認する。"""
    assert schema["properties"]["action_bindings"]["minItems"] == 1


def test_action_bindings_item_required_fields(schema):
    """action_bindings要素の必須項目を確認する。"""
    item_required = schema["properties"]["action_bindings"]["items"]["required"]
    for field in ["action", "api", "dry_run"]:
        assert field in item_required


def test_valid_payload_passes(schema):
    """正常なペイロードが検証を通過することを確認する。"""
    # Phase 0 想定の代表入力でスキーマ通過を検証する。
    payload = {
        "state": ["来店頻度低下", "価格感度低", "限定感志向"],
        "intent": "再来店動機付け",
        "next_actions": ["限定LINE配信案", "会員限定イベント", "期間限定特典"],
        "confidence": 0.82,
        "trace_id": "00000000-0000-0000-0000-000000000001",
        "rollback_plan": "配信停止→通常施策に戻す",
        "action_bindings": [
            {"action": "LINE配信", "api": "line.broadcast", "dry_run": True}
        ],
    }
    jsonschema.validate(payload, schema)


def test_invalid_payload_missing_intent_fails(schema):
    """intent 欠落時にバリデーションエラーとなることを確認する。"""
    payload = {
        "state": ["来店頻度低下", "価格感度低", "限定感志向"],
        "next_actions": ["A", "B", "C"],
        "confidence": 0.5,
        "trace_id": "00000000-0000-0000-0000-000000000001",
        "rollback_plan": "戻す",
        "action_bindings": [{"action": "A", "api": "a.b", "dry_run": True}],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, schema)


def test_invalid_state_too_few_items_fails(schema):
    """state 件数不足時にバリデーションエラーとなることを確認する。"""
    payload = {
        "state": ["来店頻度低下"],
        "intent": "再来店",
        "next_actions": ["A", "B", "C"],
        "confidence": 0.5,
        "trace_id": "00000000-0000-0000-0000-000000000001",
        "rollback_plan": "戻す",
        "action_bindings": [{"action": "A", "api": "a.b", "dry_run": True}],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, schema)


def test_invalid_action_bindings_missing_dry_run_fails(schema):
    """action_bindings 要素で dry_run 欠落時に失敗することを確認する。"""
    payload = {
        "state": ["来店頻度低下", "価格感度低", "限定感志向"],
        "intent": "再来店動機付け",
        "next_actions": ["A", "B", "C"],
        "confidence": 0.5,
        "trace_id": "00000000-0000-0000-0000-000000000001",
        "rollback_plan": "戻す",
        "action_bindings": [{"action": "LINE配信", "api": "line.broadcast"}],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, schema)
