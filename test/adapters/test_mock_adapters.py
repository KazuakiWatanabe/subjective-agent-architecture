"""Mock Adapter 実装の契約を検証するテスト。"""

import pytest

from adapters.mock_crm_adapter import MockCrmAdapter
from adapters.mock_line_adapter import MockLineAdapter
from adapters.mock_task_adapter import MockTaskAdapter

ADAPTER_CLASSES = [MockLineAdapter, MockCrmAdapter, MockTaskAdapter]
REQUIRED_METHODS = ["validate", "execute", "rollback", "audit"]


@pytest.fixture
def adapter():
    """テスト対象の MockLineAdapter を返す。"""
    return MockLineAdapter()


@pytest.fixture
def valid_input():
    """MockLineAdapter の正常入力を返す。"""
    return {"segment_id": "seg-001", "message": "hello"}


# P1-2-AC-01
def test_validate_returns_ok(adapter, valid_input):
    """正常入力で validate が ok=True を返すことを確認する。"""
    assert adapter.validate(valid_input)["ok"] is True


# P1-2-AC-02: 必須欠落は ok=False（異常系）
def test_validate_fails_on_missing_field(adapter):
    """必須フィールド欠落時に validate が ok=False を返すことを確認する。"""
    assert adapter.validate({"message": "hello"})["ok"] is False


# P1-2-AC-03: dry_run=True で execution_id が返る
def test_execute_dry_run(adapter, valid_input):
    """dry_run 実行で execution_id が返り、副作用なしで完了することを確認する。"""
    result = adapter.execute("send_line_message", {**valid_input, "dry_run": True})

    assert result["dry_run"] is True
    assert "execution_id" in result


# P1-2-AC-04
def test_rollback_returns_ok(adapter):
    """rollback が ok=True を返すことを確認する。"""
    assert adapter.rollback("exec-001")["ok"] is True


# P1-2-AC-05
def test_audit_returns_record(adapter, valid_input):
    """execute 後に audit が execution_id 対応の記録を返すことを確認する。"""
    result = adapter.execute("send_line_message", {**valid_input, "dry_run": True})
    audit = adapter.audit(result["execution_id"])

    assert audit["execution_id"] == result["execution_id"]


# P1-2-AC-06: 全 Adapter が共通 interface を持つ
@pytest.mark.parametrize("adapter_cls", ADAPTER_CLASSES)
@pytest.mark.parametrize("method", REQUIRED_METHODS)
def test_all_adapters_have_interface(adapter_cls, method):
    """全 Adapter が共通 interface を持つことを確認する。"""
    assert hasattr(adapter_cls(), method)
