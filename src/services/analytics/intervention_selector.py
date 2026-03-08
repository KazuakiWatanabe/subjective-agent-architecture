"""Trait × State に応じた施策候補を選択する selector を提供する。

概要:
    チャーン文脈の state と trait を受け取り、決定論的な施策候補リストを返す。
入出力:
    trait / state -> list[str]。
制約:
    - 同一入力に対して常に同じ順序・同じ内容を返す
    - trait または state が空でも 1 件以上のデフォルト施策を返す
    - trait 差分は state のデフォルト施策に対する上書きとして扱う
Note:
    - Phase 2 の最小実装としてメモリ上の固定ルールのみを扱う
    - 施策の妥当性は後続タスクで KPI / Meta を使って見直す
"""

from __future__ import annotations


class InterventionSelector:
    """Trait × State から施策候補を決定論的に選択する。"""

    _DEFAULT_INTERVENTIONS: tuple[str, ...] = (
        "最近の状況ヒアリングを行い、次回接点を明確にする",
    )

    _STATE_INTERVENTIONS: dict[str, tuple[str, ...]] = {
        "来店頻度低下": (
            "来店理由を再提示するメッセージを配信する",
            "再来店導線を短くしたオファーを提示する",
        ),
        "予算逼迫": (
            "低負担プランと費用対効果を整理して提示する",
        ),
        "多忙": (
            "短時間で完了する来店導線を提示する",
        ),
        "比較疲れ": (
            "選択肢を絞った比較提案を行う",
        ),
        "限定感志向": (
            "期間限定の訴求を含む案内を送る",
        ),
        "価格感度高": (
            "価格条件を明確にしたオファーを出す",
        ),
        "接触希薄化": (
            "反応しやすいチャネルへ接触頻度を再設計する",
        ),
    }

    _TRAIT_STATE_OVERRIDES: dict[str, dict[str, tuple[str, ...]]] = {
        "価格感度高": {
            "来店頻度低下": (
                "再来店の価格ハードルを下げた限定クーポンを提示する",
                "次回利用時の負担が小さい価格帯メニューを案内する",
            ),
        },
        "限定感志向": {
            "来店頻度低下": (
                "先着または期間限定の再来店特典を訴求する",
                "今だけ感のあるメッセージで来店優先度を上げる",
            ),
        },
    }

    _TRAIT_DEFAULT_OVERRIDES: dict[str, tuple[str, ...]] = {
        "価格感度高": (
            "価格条件を明確にした再接触施策を優先する",
        ),
        "限定感志向": (
            "希少性を感じる限定訴求を優先する",
        ),
    }

    def select(self, trait: list[str], state: list[str]) -> list[str]:
        """trait / state に応じた施策候補を返す。

        Args:
            trait: 顧客 trait の文字列リスト
            state: churn state の文字列リスト

        Returns:
            優先度順の施策候補リスト

        Note:
            - 施策の重複は順序を保ったまま除去する
            - 最初に解決できる trait / state を優先して差分を作る
        """
        normalized_traits = self._normalize_values(trait)
        normalized_states = self._normalize_values(state)

        primary_state = normalized_states[0] if normalized_states else ""
        interventions: list[str] = []

        if primary_state:
            interventions.extend(self._STATE_INTERVENTIONS.get(primary_state, self._DEFAULT_INTERVENTIONS))
        else:
            interventions.extend(self._DEFAULT_INTERVENTIONS)

        for current_trait in normalized_traits:
            overrides = self._TRAIT_STATE_OVERRIDES.get(current_trait, {})
            if primary_state and primary_state in overrides:
                interventions = list(overrides[primary_state]) + interventions
                break

        if not normalized_states:
            for current_trait in normalized_traits:
                if current_trait in self._TRAIT_DEFAULT_OVERRIDES:
                    interventions = list(self._TRAIT_DEFAULT_OVERRIDES[current_trait]) + interventions
                    break

        if not normalized_traits and not normalized_states:
            interventions = list(self._DEFAULT_INTERVENTIONS)

        return self._deduplicate(interventions)

    def _normalize_values(self, values: list[str]) -> list[str]:
        """空文字を除外した正規化済みリストを返す。"""
        normalized: list[str] = []
        for value in values:
            stripped = value.strip()
            if stripped:
                normalized.append(stripped)
        return normalized

    def _deduplicate(self, values: list[str]) -> list[str]:
        """順序を保持して重複を除去する。"""
        deduplicated: list[str] = []
        for value in values:
            if value not in deduplicated:
                deduplicated.append(value)
        return deduplicated or list(self._DEFAULT_INTERVENTIONS)
