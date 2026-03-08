"""Planner / Applier の最小 plan-apply フロー契約を検証するテスト。"""

import pytest

from services.execution.applier import Applier
from services.execution.planner import Planner


@pytest.fixture
def planner():
    """テスト対象の Planner を返す。"""
    return Planner()


@pytest.fixture
def applier():
    """テスト対象の Applier を返す。"""
    return Applier()


# P1-3-AC-01
def test_planner_generates_steps(planner):
    """recommended_primitives から steps が生成されることを確認する。"""
    plan = planner.build({"state": ["来店頻度低下"], "recommended_primitives": ["send_line_message"]})

    assert len(plan["steps"]) >= 1


# P1-3-AC-02
def test_applier_completes_dry_run(applier):
    """dry_run plan が dry_run_completed で完了することを確認する。"""
    plan = {
        "steps": [
            {"primitive": "send_line_message", "params": {"segment_id": "s1", "message": "hi", "dry_run": True}}
        ]
    }

    assert applier.apply(plan)["status"] == "dry_run_completed"


# P1-3-AC-03: 空 plan（境界値）
def test_applier_handles_empty_plan(applier):
    """空 plan を no_steps / skipped / error のいずれかで返すことを確認する。"""
    assert applier.apply({"steps": []})["status"] in ["no_steps", "skipped", "error"]


# P1-3-AC-04: 未知 primitive フラグ（異常系）
def test_planner_flags_unknown_primitive(planner):
    """未知 primitive を含む step に manual_review_required が立つことを確認する。"""
    plan = planner.build({"state": ["来店頻度低下"], "recommended_primitives": ["unknown_primitive"]})

    assert any(step.get("manual_review_required") for step in plan["steps"])


# P1-3-AC-05: validate 失敗の step は apply されない（異常系）
def test_applier_skips_invalid_step(applier):
    """validate 失敗の step が apply されずスキップされることを確認する。"""
    plan = {
        "steps": [
            {"primitive": "send_line_message", "params": {"message": "hi", "dry_run": True}}
        ]  # segment_id 欠落
    }

    result = applier.apply(plan)

    assert result.get("skipped_count", 0) >= 1 or result["status"] in ["error", "partial"]
