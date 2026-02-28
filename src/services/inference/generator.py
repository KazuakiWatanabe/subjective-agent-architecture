"""検証済み情報から最終JSONを生成する Generator を提供する。

入出力: payload/validation_result -> dict(JSON)。
制約:
    - validation_result.ok が False の場合は生成しない
    - スキーマ外フィールドは追加しない（trace_id/generated_at を除く）

Note:
    - trace_id は UUID で自動付与する
    - Phase 0 制約として action_bindings の dry_run は常に True に補正する
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import uuid
from typing import Any

from services.inference.validator import ValidationResult


class GeneratorError(Exception):
    """Generator処理の失敗を表す例外。"""


class Generator:
    """Validator通過後のデータを最終形式へ整形するクラス。"""

    def generate(
        self,
        payload: dict[str, Any],
        validation_result: ValidationResult,
    ) -> dict[str, Any]:
        """検証結果を確認し、最終レスポンスを生成する。

        Args:
            payload: 入力ペイロード
            validation_result: Validatorの検証結果

        Returns:
            dict[str, Any]: trace_id/generated_at付きの最終出力

        Raises:
            GeneratorError: 検証失敗時

        Note:
            - Phase 0では action_bindings の dry_run を強制的に True にする
        """
        if not validation_result.ok:
            joined_issues = ", ".join(validation_result.issues)
            raise GeneratorError(f"validation failed: {joined_issues}")

        output = deepcopy(payload)
        output["trace_id"] = str(uuid.uuid4())
        output["generated_at"] = datetime.now(timezone.utc).isoformat()

        bindings = output.get("action_bindings") or []
        normalized_bindings: list[dict[str, Any]] = []
        for binding in bindings:
            if not isinstance(binding, dict):
                continue
            normalized = dict(binding)
            normalized["dry_run"] = True
            normalized_bindings.append(normalized)
        output["action_bindings"] = normalized_bindings

        return output
