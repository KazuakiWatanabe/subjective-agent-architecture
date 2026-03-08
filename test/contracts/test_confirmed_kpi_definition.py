"""確定版 KPI ドキュメントの追加項目を検証するテスト。"""

from pathlib import Path

import pytest

DOC_PATH = Path(__file__).parent.parent.parent / "docs/specs/kpi_definition.md"
NEW_FIELDS = ["baseline", "comparison_method", "data_source", "measurement_window"]


@pytest.mark.parametrize("field", NEW_FIELDS)
def test_confirmed_fields_exist(field):
    """確定版 KPI ドキュメントに追加フィールドが含まれることを確認する。"""
    assert field in DOC_PATH.read_text(encoding="utf-8")


def test_at_least_one_confirmed_kpi():
    """status が confirmed の KPI が 1 件以上あることを確認する。"""
    assert "confirmed" in DOC_PATH.read_text(encoding="utf-8")
