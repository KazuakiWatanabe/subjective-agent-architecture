"""RollbackManager の最小 rollback 契約を検証するテスト。

概要:
    RollbackManager.rollback が既知 adapter と未知 adapter を安全に扱うことを確認する。
入出力:
    rollback request -> rollback result。
制約:
    - 正常系では status を返す
    - 未知 adapter と空 execution_id は安全側で扱う
Note:
    - P1-5 の受け入れ条件に対応する最小テストのみを含む
"""

import pytest

from services.execution.rollback_manager import RollbackManager


@pytest.fixture
def manager():
    """テスト対象の RollbackManager を返す。"""
    return RollbackManager()


# P1-5-AC-01
def test_rollback_returns_status_for_known_adapter(manager):
    """既知 adapter の rollback が status を返すことを確認する。"""
    result = manager.rollback({"execution_id": "exec-001", "adapter": "mock_line"})

    assert "status" in result


# P1-5-AC-02: 未知 adapter（異常系）
def test_unknown_adapter_requires_manual_intervention(manager):
    """未知 adapter が manual_intervention_required=True になることを確認する。"""
    result = manager.rollback({"execution_id": "exec-001", "adapter": "unknown_adapter"})

    assert result["manual_intervention_required"] is True


# P1-5-AC-03: dry_run に対しても記録が残る
def test_rollback_record_for_dry_run(manager):
    """dry_run rollback でも status を返すことを確認する。"""
    result = manager.rollback({"execution_id": "exec-dry-001", "adapter": "mock_line", "dry_run": True})

    assert "status" in result


# P1-5-AC-04: 空 execution_id（境界値）
def test_empty_execution_id_handled_safely(manager):
    """空 execution_id が error または manual intervention 扱いになることを確認する。"""
    result = manager.rollback({"execution_id": "", "adapter": "mock_line"})

    assert result.get("status") == "error" or result.get("manual_intervention_required") is True
