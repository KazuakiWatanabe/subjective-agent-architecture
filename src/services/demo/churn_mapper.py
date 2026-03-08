"""チャーン文脈の state 語彙へ正規化するマッパーを提供する。

概要:
    自然文の state 表現を、Phase 0B で定義したチャーン向け語彙へ写像する。
入出力:
    states -> list[str]。
制約:
    - 入力順を保持して決定論的に変換する
    - 未知語は破棄せずそのまま返す
    - Phase 0B では語彙拡張よりも既知語の安定変換を優先する
Note:
    - 1入力につき1語彙のみ返し、最初に一致した規則を採用する
    - 判定は部分一致ベースの簡易実装とし、後続タスクで拡張可能な形に留める
"""

from __future__ import annotations


class ChurnStateMapper:
    """state をチャーン向け語彙へ正規化するクラス。"""

    _RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("来店頻度低下", ("来店が減", "来店減", "来なくな", "足が遠の", "頻度が落", "頻度低下")),
        ("予算逼迫", ("予算", "金欠", "出費", "余裕がない", "節約", "家計が厳し")),
        ("多忙", ("忙しい", "忙しく", "多忙", "時間がない", "余裕がないほど忙", "来れない")),
        ("比較疲れ", ("比較", "迷って", "決めきれ", "検討疲れ", "選べない")),
        ("限定感志向", ("限定", "特別感", "今だけ", "先着", "希少", "レア")),
        ("価格感度高", ("高い", "値段", "価格", "安い", "値引", "割引", "コスパ")),
        ("接触希薄化", ("連絡がない", "反応がない", "接触", "音沙汰", "疎遠", "既読スルー")),
    )

    def map_states(self, states: list[str]) -> list[str]:
        """state のリストをチャーン向け語彙へ変換する。

        Args:
            states: 自然文または既存 state の文字列リスト

        Returns:
            チャーン向け語彙へ正規化した文字列リスト

        Note:
            - 空入力は空リストのまま返す
            - 入力要素は文字列前提とし、未知語のみ元の文字列を保持する
        """
        if not states:
            return []

        normalized_states: list[str] = []
        for state in states:
            normalized_states.append(self._map_single_state(state))
        return normalized_states

    def _map_single_state(self, state: str) -> str:
        """単一の state を最初に一致した語彙へ変換する。"""
        normalized_state = state.strip()
        if not normalized_state:
            return normalized_state

        for churn_term, keywords in self._RULES:
            # 規則の評価順を固定し、同一入力に対して常に同じ語彙へ寄せる。
            if any(keyword in normalized_state for keyword in keywords):
                return churn_term

        return normalized_state
