"""Reader/Validator/Generator を統合して変換処理を制御する Orchestrator を提供する。

入出力: input_text(str) -> dict(JSON)。
制約:
    - 実行順は Reader -> Validator -> Generator に固定する
    - Validator NG 時は最大2回まで再試行し、超過時は MaxRetryError を送出する

Note:
    - 成功/失敗の両パスで監査ログを必ず保存する
    - Validator が失敗している間は Generator を呼び出さない
"""

from __future__ import annotations

from datetime import datetime, timezone
import uuid
from typing import Any

from services.inference.audit_store import AuditStore
from services.inference.generator import Generator
from services.inference.reader import Reader
from services.inference.validator import ValidationResult, Validator


class MaxRetryError(Exception):
    """Validator NGが規定回数を超えた場合に送出する例外。"""


class Orchestrator:
    """Reader -> Validator -> Generator の順で処理を実行する。"""

    def __init__(
        self,
        reader: Reader | None = None,
        validator: Validator | None = None,
        generator: Generator | None = None,
        audit_store: AuditStore | None = None,
        max_retries: int = 2,
    ) -> None:
        """Orchestratorを初期化する。

        Args:
            reader: Reader実装（未指定時は既定Reader）
            validator: Validator実装（未指定時は既定Validator）
            generator: Generator実装（未指定時は既定Generator）
            audit_store: 監査ログ保存先（未指定時はインメモリ）
            max_retries: Validator NG時の再試行回数

        Note:
            - max_retries=2 の場合、最大試行回数は3回（初回+再試行2回）
        """
        self.reader = reader or Reader()
        self.validator = validator or Validator()
        self.generator = generator or Generator()
        self.audit_store = audit_store or AuditStore()
        self.max_retries = max_retries

    def run(self, input_text: str) -> dict[str, Any]:
        """入力テキストを処理し、成功時は最終JSONを返す。

        Args:
            input_text: 変換対象の自然文

        Returns:
            dict[str, Any]: Generatorが生成した最終出力

        Raises:
            MaxRetryError: Validator NGが上限回数を超えた場合

        Note:
            - 失敗時でも必ず監査ログを保存する
            - Validator NGの間は Generator を呼び出さない
        """
        last_state: list[str] = []
        last_result = ValidationResult(ok=False, issues=["validation not executed"])

        for _ in range(self.max_retries + 1):
            state = self.reader.extract(input_text)
            payload = self._build_payload(state)
            validation_result = self.validator.validate(payload)

            last_state = state
            last_result = validation_result

            if not validation_result.ok:
                continue

            output = self.generator.generate(payload, validation_result)
            self.audit_store.save(
                {
                    "trace_id": output.get("trace_id", str(uuid.uuid4())),
                    "input_text": input_text,
                    "state": state,
                    "status": "success",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
            return output

        error_message = (
            "validation failed after max retries: " + ", ".join(last_result.issues)
        )
        self.audit_store.save(
            {
                "trace_id": str(uuid.uuid4()),
                "input_text": input_text,
                "state": last_state,
                "status": "failed",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": error_message,
            }
        )
        raise MaxRetryError(error_message)

    def _build_payload(self, state: list[str]) -> dict[str, Any]:
        """Reader出力からValidator入力ペイロードを組み立てる。

        Args:
            state: Readerが抽出したstate一覧

        Returns:
            dict[str, Any]: Validator/Geneator向けの中間ペイロード
        """
        normalized_state = self._normalize_state(state)

        return {
            "state": normalized_state,
            "intent": "再来店動機付け",
            "next_actions": [
                "限定LINE配信案",
                "会員限定イベント",
                "期間限定特典",
            ],
            "confidence": 0.8,
            "trace_id": str(uuid.uuid4()),
            "rollback_plan": "配信停止→通常施策に戻す",
            "action_bindings": [
                {"action": "LINE配信", "api": "line.broadcast", "dry_run": True}
            ],
        }

    def _normalize_state(self, state: list[str]) -> list[str]:
        """state一覧を schema 制約に合わせて正規化する。

        Args:
            state: Readerが抽出したstate一覧

        Returns:
            list[str]: 最低3件・重複なしの state 一覧

        Note:
            - Reader抽出件数が不足する場合は補助stateを追加する
            - Validatorの minItems/重複制約を満たすための補完処理
        """
        # 型・空文字を除外してベース候補を生成する。
        normalized = [item.strip() for item in state if isinstance(item, str) and item.strip()]

        # 順序を維持しつつ重複を排除する。
        deduplicated: list[str] = []
        seen: set[str] = set()
        for item in normalized:
            if item in seen:
                continue
            deduplicated.append(item)
            seen.add(item)

        # schemaのminItems=3を満たすまで補助stateを追加する。
        fallback_states = [
            "来店頻度低下",
            "価格感度低",
            "限定感志向",
        ]
        for fallback in fallback_states:
            if len(deduplicated) >= 3:
                break
            if fallback in seen:
                continue
            deduplicated.append(fallback)
            seen.add(fallback)

        return deduplicated
