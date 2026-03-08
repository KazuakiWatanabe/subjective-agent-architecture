"""CRM 向けの Mock Adapter を提供する。

概要:
    segment_customers / reserve_offer / cancel_offer を模したインメモリ adapter を実装する。
入出力:
    payload -> validation/result、execution_id -> rollback/audit result。
制約:
    - dry_run=True の場合は外部副作用を発生させない
    - execution_id は adapter 内で一意に採番する
    - 監査情報はメモリ上にのみ保持する
Note:
    - Phase 1 の mock 実装であり、本番 CRM 連携は行わない
    - validate は最低限 payload が dict であることを確認する
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class MockCrmAdapter:
    """CRM 操作を模した mock adapter。"""

    def __init__(self) -> None:
        """監査情報と副作用記録を初期化する。"""
        self._execution_count = 0
        self._audit_records: dict[str, dict[str, Any]] = {}
        self._operations: list[dict[str, Any]] = []

    def validate(self, payload: dict[str, Any]) -> dict[str, Any]:
        """入力が辞書であることを確認する。"""
        is_valid = isinstance(payload, dict)
        return {"ok": is_valid, "issues": [] if is_valid else ["payload"]}

    def execute(self, primitive_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        """CRM 操作を模した実行結果を返す。"""
        validation = self.validate(payload)
        if not validation["ok"]:
            return {"ok": False, "issues": validation["issues"], "dry_run": bool(payload.get("dry_run", False))}

        self._execution_count += 1
        execution_id = f"crm-exec-{self._execution_count:03d}"
        dry_run = bool(payload.get("dry_run", False))

        if not dry_run:
            self._operations.append({"primitive": primitive_name, "payload": payload.copy()})

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
