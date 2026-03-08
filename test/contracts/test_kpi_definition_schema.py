"""kpi_definition schema と KPI ドキュメントの契約を検証するテスト。"""

import json
from pathlib import Path

import jsonschema
import pytest

SCHEMA_PATH = Path(__file__).parent.parent.parent / "src/contracts/kpi_definition.schema.json"
DOC_PATH = Path(__file__).parent.parent.parent / "docs/specs/kpi_definition.md"
KPI_NAMES = ["再来店率", "30日継続率", "施策反応率", "誤配信率", "Meta 蓄積速度"]


@pytest.fixture
def schema():
    """検証対象の KPI schema を読み込む。"""
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture
def valid_kpi():
    """正常系の KPI ペイロードを返す。"""
    return {
        "kpis": [
            {
                "name": "30日継続率",
                "definition": "配信後30日以内に再来店した割合",
                "numerator": "30日以内再来店顧客数",
                "denominator": "対象配信顧客数",
                "frequency": "monthly",
                "owner": "pm",
                "status": "hypothesis",
            }
        ]
    }


# P0B-4-AC-01
def test_kpi_schema_is_valid_draft7(schema):
    """KPI schema が Draft7 妥当であることを確認する。"""
    jsonschema.Draft7Validator.check_schema(schema)


# P0B-4-AC-02
def test_valid_kpi_payload_passes(schema, valid_kpi):
    """正常な KPI ペイロードが schema を通過することを確認する。"""
    jsonschema.validate(valid_kpi, schema)


# P0B-4-AC-03: status は hypothesis/confirmed のみ許可（異常系）
def test_invalid_status_fails(schema, valid_kpi):
    """status が許可値外なら ValidationError となることを確認する。"""
    valid_kpi["kpis"][0]["status"] = "draft"

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(valid_kpi, schema)


# P0B-4-AC-04: 必須フィールド欠落はエラー（異常系）
def test_missing_name_fails(schema, valid_kpi):
    """必須フィールド name 欠落時に ValidationError となることを確認する。"""
    del valid_kpi["kpis"][0]["name"]

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(valid_kpi, schema)


# P0B-4-AC-05: 5種の KPI が docs に記載されている
@pytest.mark.parametrize("kpi_name", KPI_NAMES)
def test_kpi_doc_covers_all_kpis(kpi_name):
    """KPI ドキュメントが 5 種の KPI 名をすべて含むことを確認する。"""
    text = DOC_PATH.read_text(encoding="utf-8")

    assert kpi_name in text
