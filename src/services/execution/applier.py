"""execution plan を Mock Adapter で適用する Applier を提供する。

概要:
    Planner が生成した step を validate → execute の順で処理し、集計結果を返す。
入出力:
    plan -> apply_result。
制約:
    - dry_run をデフォルトとする
    - validate に失敗した step は execute しない
    - 未知 primitive または manual review 指定 step はスキップする
Note:
    - Phase 1 の最小実装として P1-2 の Mock Adapter を使用する
    - 監査の永続化は行わず、execution audit をメモリ上に保持する
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from adapters.mock_crm_adapter import MockCrmAdapter
from adapters.mock_line_adapter import MockLineAdapter
from adapters.mock_task_adapter import MockTaskAdapter


class AuditStore:
    """execution audit をメモリ上に保持する。"""

    def __init__(self) -> None:
        """監査レコード一覧を初期化する。"""
        self._records: list[dict[str, Any]] = []

    def save(self, record: dict[str, Any]) -> None:
        """監査レコードを保存する。

        Args:
            record: 保存対象の監査レコード
        """
        self._records.append(record)

    def last(self) -> dict[str, Any] | None:
        """最後に保存した監査レコードを返す。"""
        return self._records[-1] if self._records else None


class Applier:
    """plan の step を順次適用する。"""

    def __init__(self) -> None:
        """primitive と adapter の対応を初期化する。"""
        crm_adapter = MockCrmAdapter()
        line_adapter = MockLineAdapter()
        task_adapter = MockTaskAdapter()
        self._adapters = {
            "segment_customers": crm_adapter,
            "reserve_offer": crm_adapter,
            "cancel_offer": crm_adapter,
            "send_line_message": line_adapter,
            "create_followup_task": task_adapter,
        }
        self.audit_store = AuditStore()

    def apply(self, plan: dict[str, Any]) -> dict[str, Any]:
        """plan を順次 validate / execute する。

        Args:
            plan: steps を含む plan 辞書

        Returns:
            適用結果の辞書
        """
        steps = plan.get("steps", [])
        trace_id = str(plan.get("trace_id") or uuid4())
        selected_primitives = [step.get("primitive") for step in steps if step.get("primitive")]
        plan_dry_run = all(dict(step.get("params", {})).get("dry_run", True) for step in steps) if steps else True

        if not steps:
            result = {"status": "no_steps", "applied_count": 0, "skipped_count": 0, "results": []}
            self.audit_store.save(
                {
                    "trace_id": trace_id,
                    "selected_primitives": selected_primitives,
                    "dry_run": plan_dry_run,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            )
            return result

        applied_count = 0
        skipped_count = 0
        dry_run_count = 0
        results: list[dict[str, Any]] = []

        for step in steps:
            primitive = step.get("primitive")
            params = dict(step.get("params", {}))

            if step.get("manual_review_required"):
                skipped_count += 1
                results.append({"primitive": primitive, "status": "manual_review_required"})
                continue

            adapter = self._adapters.get(primitive)
            if adapter is None:
                skipped_count += 1
                results.append({"primitive": primitive, "status": "unknown_primitive"})
                continue

            # タスク要件に従い、dry_run 未指定時も安全側に倒す。
            params.setdefault("dry_run", True)
            validation = adapter.validate(params)
            if not validation.get("ok", False):
                skipped_count += 1
                results.append({"primitive": primitive, "status": "skipped", "issues": validation.get("issues", [])})
                continue

            execution = adapter.execute(primitive, params)
            applied_count += 1
            if execution.get("dry_run"):
                dry_run_count += 1
            results.append(execution)

        if applied_count == 0:
            status = "skipped" if skipped_count else "no_steps"
        elif skipped_count > 0:
            status = "partial"
        elif dry_run_count == applied_count:
            status = "dry_run_completed"
        else:
            status = "completed"

        result = {
            "status": status,
            "applied_count": applied_count,
            "skipped_count": skipped_count,
            "dry_run_count": dry_run_count,
            "results": results,
        }
        self.audit_store.save(
            {
                "trace_id": trace_id,
                "selected_primitives": selected_primitives,
                "dry_run": plan_dry_run,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )
        return result
