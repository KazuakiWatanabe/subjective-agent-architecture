"""ChurnStateMapper の state 語彙正規化を検証するテスト。"""

import pytest

from services.demo.churn_mapper import ChurnStateMapper


@pytest.fixture
def mapper():
    """テストで共通利用する ChurnStateMapper を返す。"""
    return ChurnStateMapper()


# P0B-1-AC-01: 既知の自然文 state が churn 語彙に正規化される
def test_maps_known_states_to_churn_terms(mapper):
    """既知 state がチャーン向け語彙へ正規化されることを確認する。"""
    result = mapper.map_states(["来店が減っている", "限定に反応", "忙しくて来れない"])

    assert result == ["来店頻度低下", "限定感志向", "多忙"]


# P0B-1-AC-02: 未知語は破棄されず保持される
def test_unknown_state_is_preserved(mapper):
    """未知語がそのまま保持されることを確認する。"""
    result = mapper.map_states(["完全に謎の状態"])

    assert result == ["完全に謎の状態"]


# P0B-1-AC-03: 同一入力に対して結果が常に同じ順序で返る
def test_mapping_is_stable(mapper):
    """同一入力に対して順序を含めて同じ結果が返ることを確認する。"""
    states = ["来店が減っている", "限定に反応", "忙しくて来れない"]

    first = mapper.map_states(states)
    second = mapper.map_states(states)

    assert first == second


# P0B-1-AC-04: 空リスト入力は空リストを返す（境界値）
def test_empty_input_returns_empty(mapper):
    """空入力時に空リストが返ることを確認する。"""
    assert mapper.map_states([]) == []


# P0B-1-AC-05: 既知語と未知語が混在する場合、双方が正しく処理される
def test_mixed_known_and_unknown_preserves_both(mapper):
    """既知語は正規化し、未知語は保持することを確認する。"""
    result = mapper.map_states(["来店が減っている", "謎の状態"])

    assert result == ["来店頻度低下", "謎の状態"]
