"""state-to-churn hypothesis table の存在と内容を検証するテスト。

概要:
    Phase 2 で使う state と churn 仮説の対応表が所定の列と state を含むことを確認する。
入出力:
    hypothesis table file -> assertion result。
制約:
    - P0B-1 で定義した 7 種の churn state をすべて含む
    - 必須カラムが Markdown テーブルに含まれる
Note:
    - P2-1 の受け入れ条件に対応する最小テストのみを含む
"""

from pathlib import Path

import pytest

TABLE_PATH = Path(__file__).parent.parent.parent / "docs/hypotheses/state_to_churn_table.md"
CHURN_STATES = ["来店頻度低下", "予算逼迫", "多忙", "比較疲れ", "限定感志向", "価格感度高", "接触希薄化"]
REQUIRED_COLUMNS = ["churn_risk_hypothesis", "assumed_signal", "recommended_intervention", "evidence_level"]


# P2-1-AC-01
def test_hypothesis_table_exists():
    """state-to-churn hypothesis table が存在することを確認する。"""
    assert TABLE_PATH.exists()


# P2-1-AC-02: 7種の churn state が全て記載されている
@pytest.mark.parametrize("state", CHURN_STATES)
def test_all_churn_states_covered(state):
    """7 種の churn state が表に含まれることを確認する。"""
    assert state in TABLE_PATH.read_text(encoding="utf-8")


# P2-1-AC-03: 必須カラムが存在する
@pytest.mark.parametrize("col", REQUIRED_COLUMNS)
def test_required_columns_exist(col):
    """必須カラム名が表に含まれることを確認する。"""
    assert col in TABLE_PATH.read_text(encoding="utf-8")
