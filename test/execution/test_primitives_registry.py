"""PrimitivesRegistry のアクション解決契約を検証するテスト。"""

import pytest

from services.execution.primitives_registry import PrimitivesRegistry

PRIMITIVES = [
    "segment_customers",
    "send_line_message",
    "reserve_offer",
    "cancel_offer",
    "create_followup_task",
]


@pytest.fixture
def registry():
    """テストで共通利用する PrimitivesRegistry を返す。"""
    return PrimitivesRegistry()


# P0B-3-AC-01: 自然文アクションから対応する primitive 名が返る
def test_maps_actions_to_primitives(registry):
    """自然文アクションが既知 primitive へ変換されることを確認する。"""
    result = registry.resolve(["LINEで限定オファーを配信", "フォロータスクを作成"])
    names = [resolved["primitive"] for resolved in result]

    assert "send_line_message" in names
    assert "create_followup_task" in names


# P0B-3-AC-02: 非対応アクションは manual_review_required=True で返る
def test_unknown_action_requires_manual_review(registry):
    """未知アクションが manual review 扱いになることを確認する。"""
    result = registry.resolve(["スタッフに感覚で判断してもらう"])

    assert result[0]["manual_review_required"] is True


# P0B-3-AC-03: 空リスト入力は空リストを返す（境界値）
def test_empty_input_returns_empty(registry):
    """空入力時に空リストを返すことを確認する。"""
    assert registry.resolve([]) == []


# P0B-3-AC-04: 複数の未知アクションがすべて manual_review_required=True になる
def test_multiple_unknown_actions_all_flagged(registry):
    """複数の未知アクションが全件 manual review になることを確認する。"""
    result = registry.resolve(["謎の行動1", "謎の行動2"])

    assert all(resolved["manual_review_required"] is True for resolved in result)
    assert len(result) == 2


# P0B-3-AC-05: 5種の primitive がすべて解決可能である
@pytest.mark.parametrize("primitive", PRIMITIVES)
def test_all_primitives_are_resolvable(registry, primitive):
    """定義した 5 種の primitive が名前解決できることを確認する。"""
    result = registry.resolve_by_name(primitive)

    assert result is not None
