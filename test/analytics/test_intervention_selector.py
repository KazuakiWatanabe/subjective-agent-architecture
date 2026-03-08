"""InterventionSelector の施策差分ロジックを検証するテスト。"""

import pytest

from services.analytics.intervention_selector import InterventionSelector


@pytest.fixture
def selector():
    """テスト対象の InterventionSelector を返す。"""
    return InterventionSelector()


# P2-2-AC-01
def test_different_trait_yields_different_intervention(selector):
    """trait が異なると返る施策が異なることを確認する。"""
    a = selector.select(trait=["価格感度高"], state=["来店頻度低下"])
    b = selector.select(trait=["限定感志向"], state=["来店頻度低下"])

    assert a != b


# P2-2-AC-02
def test_at_least_one_intervention_returned(selector):
    """常に 1 件以上の施策が返ることを確認する。"""
    assert len(selector.select(trait=["限定感志向"], state=["来店頻度低下"])) >= 1


# P2-2-AC-03: 空 trait（境界値）
def test_empty_trait_returns_default(selector):
    """空 trait でもデフォルト施策が返ることを確認する。"""
    assert len(selector.select(trait=[], state=["来店頻度低下"])) >= 1


# P2-2-AC-04: 空 state（境界値）
def test_empty_state_returns_default(selector):
    """空 state でもデフォルト施策が返ることを確認する。"""
    assert len(selector.select(trait=["限定感志向"], state=[])) >= 1


# P2-2-AC-05: 冪等性
def test_repeated_call_is_stable(selector):
    """同一入力で結果が安定することを確認する。"""
    a = selector.select(trait=["限定感志向"], state=["来店頻度低下"])
    b = selector.select(trait=["限定感志向"], state=["来店頻度低下"])

    assert a == b
