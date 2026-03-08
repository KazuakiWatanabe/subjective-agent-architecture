"""business_primitives schema と primitive 仕様ドキュメントの契約を検証するテスト。"""

import json
from pathlib import Path

import jsonschema
import pytest

SCHEMA_PATH = Path(__file__).parent.parent.parent / "src/contracts/business_primitives.schema.json"
DOC_PATH = Path(__file__).parent.parent.parent / "docs/specs/business_primitives.md"
PRIMITIVES = [
    "segment_customers",
    "send_line_message",
    "reserve_offer",
    "cancel_offer",
    "create_followup_task",
]
REQUIRED_FIELDS = ["name", "input", "output", "dry_run_behavior", "rollback_hint", "audit_fields"]


@pytest.fixture
def schema():
    """検証対象の business_primitives schema を読み込む。"""
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture
def valid_primitive():
    """正常系で用いる primitive 定義を返す。"""
    return {
        "name": "send_line_message",
        "input": {"segment_id": "string", "message": "string"},
        "output": {"execution_id": "string", "status": "string"},
        "dry_run_behavior": "副作用なしでシミュレート",
        "rollback_hint": "送信済みは取消不可。フォローアップで補償",
        "audit_fields": ["execution_id", "timestamp", "dry_run"],
    }


# P1-1-AC-01
def test_schema_is_valid_draft7(schema):
    """schema が Draft7 妥当であることを確認する。"""
    jsonschema.Draft7Validator.check_schema(schema)


# P1-1-AC-02: 必須フィールドが required に含まれる
@pytest.mark.parametrize("field", REQUIRED_FIELDS)
def test_primitive_required_fields(schema, field):
    """primitive 定義の required に必須フィールドが含まれることを確認する。"""
    assert field in schema["definitions"]["primitive"]["required"]


# P1-1-AC-03: rollback_hint 欠落はエラー（異常系）
def test_missing_rollback_hint_fails(schema, valid_primitive):
    """rollback_hint 欠落時に ValidationError となることを確認する。"""
    del valid_primitive["rollback_hint"]

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(valid_primitive, schema["definitions"]["primitive"])


# P1-1-AC-04: dry_run_behavior 欠落はエラー（異常系）
def test_missing_dry_run_behavior_fails(schema, valid_primitive):
    """dry_run_behavior 欠落時に ValidationError となることを確認する。"""
    del valid_primitive["dry_run_behavior"]

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(valid_primitive, schema["definitions"]["primitive"])


# P1-1-AC-05: 5種 primitive が docs に記載されている
@pytest.mark.parametrize("primitive", PRIMITIVES)
def test_all_primitives_documented(primitive):
    """primitive ドキュメントが 5 種すべてを含むことを確認する。"""
    assert primitive in DOC_PATH.read_text(encoding="utf-8")
