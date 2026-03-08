"""LINE 配信向けの Mock Adapter を提供する。

概要:
    send_line_message primitive を dry_run 前提で検証できるインメモリ adapter を実装する。
入出力:
    payload -> validation/result、execution_id -> rollback/audit result。
制約:
    - dry_run=True の場合は外部副作用を発生させない
    - execution_id は adapter 内で一意に採番する
    - 監査情報はメモリ上にのみ保持する
Note:
    - Phase 1 の mock 実装であり、本番 API 呼び出しは行わない
    - validate は segment_id と message の存在を必須条件とする
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class MockLineAdapter:
    """LINE 配信を模した mock adapter。"""

    def __init__(self) -> None:
        """監査情報と副作用記録を初期化する。"""
        self._execution_count = 0
        self._audit_records: dict[str, dict[str, Any]] = {}
        self._sent_messages: list[dict[str, Any]] = []

    def validate(self, payload: dict[str, Any]) -> dict[str, Any]:
        """入力 payload の必須項目を検証する。

        Args:
            payload: 実行前に検証する入力

        Returns:
            検証結果の辞書
        """
        missing_fields = [
            field for field in ("segment_id", "message") if field not in payload or payload[field] in (None, "")
        ]
        return {"ok": not missing_fields, "issues": missing_fields}

    def execute(self, primitive_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        """primitive 実行を模した結果を返す。

        Args:
            primitive_name: 実行対象の primitive 名
            payload: 実行入力

        Returns:
            実行結果の辞書

        Note:
            - dry_run=True の場合は _sent_messages を更新しない
            - 実行結果は audit 参照用にメモリへ保存する
        """
        validation = self.validate(payload)
        if not validation["ok"]:
            return {"ok": False, "issues": validation["issues"], "dry_run": bool(payload.get("dry_run", False))}

        self._execution_count += 1
        execution_id = f"line-exec-{self._execution_count:03d}"
        dry_run = bool(payload.get("dry_run", False))

        if not dry_run:
            # dry_run 以外のケースだけ副作用記録を残す。
            self._sent_messages.append({"primitive": primitive_name, "payload": payload.copy()})

        record = {
            "ok": True,
            "execution_id": execution_id,
            "primitive": primitive_name,
            "dry_run": dry_run,
            "status": "simulated" if dry_run else "executed",
            "timestamp": datetime.now(UTC).isoformat(),
        }
        self._audit_records[execution_id] = record
        return record

    def rollback(self, execution_id: str) -> dict[str, Any]:
        """rollback を模した成功結果を返す。"""
        return {"ok": True, "execution_id": execution_id}

    def audit(self, execution_id: str) -> dict[str, Any]:
        """execution_id に紐づく監査情報を返す。"""
        return self._audit_records.get(execution_id, {"execution_id": execution_id, "found": False})
