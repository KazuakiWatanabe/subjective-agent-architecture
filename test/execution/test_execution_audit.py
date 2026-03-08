"""Applier の execution audit 拡張を検証するテスト。

概要:
    Applier.apply 実行後に audit_store へ必要項目が記録されることを確認する。
入出力:
    dry_run plan -> audit record。
制約:
    - 監査対象は trace_id / selected_primitives / dry_run / timestamp とする
    - trace_id 未指定時も audit record が作成されることを確認する
Note:
    - P1-4 の受け入れ条件に対応する最小契約テストのみを扱う
"""

import pytest

from services.execution.applier import Applier


@pytest.fixture
def applier():
    """テスト対象の Applier を返す。"""
    return Applier()


@pytest.fixture
def dry_run_plan():
    """dry_run 前提の単一 step plan を返す。"""
    return {
        "trace_id": "trace-001",
        "steps": [
            {
                "primitive": "send_line_message",
                "params": {"segment_id": "s1", "message": "hi", "dry_run": True},
            }
        ],
    }


# P1-4-AC-01
def test_audit_contains_trace_id(applier, dry_run_plan):
    """audit に trace_id が記録されることを確認する。"""
    applier.apply(dry_run_plan)

    assert applier.audit_store.last()["trace_id"] == "trace-001"


# P1-4-AC-02
def test_audit_contains_selected_primitives(applier, dry_run_plan):
    """audit に selected_primitives が記録されることを確認する。"""
    applier.apply(dry_run_plan)

    assert "send_line_message" in applier.audit_store.last()["selected_primitives"]


# P1-4-AC-03
def test_audit_contains_dry_run_flag(applier, dry_run_plan):
    """audit に dry_run が記録されることを確認する。"""
    applier.apply(dry_run_plan)

    assert applier.audit_store.last()["dry_run"] is True


# P1-4-AC-04
def test_audit_contains_timestamp(applier, dry_run_plan):
    """audit に timestamp が記録されることを確認する。"""
    applier.apply(dry_run_plan)
    audit = applier.audit_store.last()

    assert "timestamp" in audit and audit["timestamp"] is not None


# P1-4-AC-05: trace_id 未指定でも audit が作成される（境界値）
def test_audit_created_without_trace_id(applier):
    """trace_id 未指定でも audit record が作成されることを確認する。"""
    plan = {
        "steps": [
            {
                "primitive": "send_line_message",
                "params": {"segment_id": "s1", "message": "hi", "dry_run": True},
            }
        ]
    }

    applier.apply(plan)

    assert applier.audit_store.last() is not None
