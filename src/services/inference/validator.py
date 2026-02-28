"""state_intent ペイロードを検証する Validator を提供する。

入出力: payload(dict) -> ValidationResult。
制約:
    - Phase 0 スキーマに必要な最低限の項目のみを検証する
    - 判定結果は ValidationResult(ok, issues) に集約する

Note:
    - エラーは例外ではなく issues に蓄積して返却する
    - Orchestrator の retry 判定に使うため決定論的に評価する
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ValidationResult:
    """バリデーション結果を表すデータ。"""

    ok: bool
    issues: list[str]


class Validator:
    """state_intentペイロードの最低限検証を行うクラス。"""

    def validate(self, payload: dict[str, Any]) -> ValidationResult:
        """入力ペイロードを検証し、結果を返す。

        Args:
            payload: 検証対象の辞書データ

        Returns:
            ValidationResult: 検証可否と問題一覧

        Note:
            - Phase 0の契約項目に対して最低限の整合性を確認する
            - 追加の厳密検証は後続タスクで拡張可能な構造にする
        """
        issues: list[str] = []

        if not isinstance(payload, dict) or not payload:
            return ValidationResult(ok=False, issues=["payload is empty"])

        state = payload.get("state")
        if not isinstance(state, list) or len(state) < 3:
            issues.append("state must contain at least 3 items")
        elif len(set(state)) != len(state):
            issues.append("state に重複があります")

        if not isinstance(payload.get("intent"), str):
            issues.append("intent is required")

        next_actions = payload.get("next_actions")
        if not isinstance(next_actions, list) or len(next_actions) < 3:
            issues.append("next_actions must contain at least 3 items")

        confidence = payload.get("confidence")
        if not isinstance(confidence, (int, float)) or not (0 <= float(confidence) <= 1):
            issues.append("confidence must be between 0 and 1")

        action_bindings = payload.get("action_bindings")
        if not isinstance(action_bindings, list) or len(action_bindings) < 1:
            issues.append("action_bindings must contain at least 1 item")

        return ValidationResult(ok=not issues, issues=issues)
