"""churn demo JSON Schema の契約を検証するテスト。"""

import json
from pathlib import Path

import jsonschema
import pytest

SCHEMA_PATH = Path(__file__).parent.parent.parent / "src/contracts/churn_demo.schema.json"
REQUIRED_FIELDS = [
    "trait",
    "state",
    "meta",
    "intent",
    "recommended_primitives",
    "kpi_hypothesis",
    "confidence",
    "trace_id",
]


@pytest.fixture
def schema():
    """検証対象の churn demo schema を読み込む。"""
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture
def valid_payload():
    """契約確認に使う正常ペイロードを返す。"""
    return {
        "trait": ["限定感志向"],
        "state": ["来店頻度低下"],
        "meta": ["前回クーポン反応なし"],
        "intent": "再来店動機付け",
        "recommended_primitives": ["send_line_message"],
        "kpi_hypothesis": ["30日継続率改善"],
        "confidence": 0.8,
        "trace_id": "demo-001",
    }


# P0B-2-AC-01: JSON Schema として Draft7 妥当である
def test_schema_is_valid_draft7(schema):
    """JSON Schema として Draft7 妥当であることを確認する。"""
    jsonschema.Draft7Validator.check_schema(schema)


# P0B-2-AC-02: 8つの必須フィールドが required に含まれる
@pytest.mark.parametrize("field", REQUIRED_FIELDS)
def test_required_fields_exist(schema, field):
    """required に全必須フィールドが含まれることを確認する。"""
    assert field in schema["required"]


# P0B-2-AC-03: 正常ペイロードがバリデーションを通過する
def test_valid_payload_passes(schema, valid_payload):
    """正常ペイロードが schema 検証を通過することを確認する。"""
    jsonschema.validate(valid_payload, schema)


# P0B-2-AC-04: 必須フィールド欠落はバリデーションエラーになる
def test_missing_trace_id_fails(schema, valid_payload):
    """必須フィールド欠落時に ValidationError となることを確認する。"""
    del valid_payload["trace_id"]

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(valid_payload, schema)


# P0B-2-AC-05: confidence > 1.0 はバリデーションエラーになる
def test_confidence_over_1_fails(schema, valid_payload):
    """confidence 上限超過時に ValidationError となることを確認する。"""
    valid_payload["confidence"] = 1.1

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(valid_payload, schema)


# P0B-2-AC-06: recommended_primitives が空配列はバリデーションエラーになる
def test_empty_primitives_fails(schema, valid_payload):
    """recommended_primitives が空配列なら ValidationError となることを確認する。"""
    valid_payload["recommended_primitives"] = []

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(valid_payload, schema)
