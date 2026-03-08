"""Rollback / compensating action の最小管理器を提供する。

概要:
    実行済み action に対して mock adapter の rollback を呼び出し、安全側の結果を返す。
入出力:
    rollback_request -> rollback_result。
制約:
    - 未知 adapter は manual_intervention_required=True で返す
    - execution_id が空の場合は error として返す
    - dry_run 指定の有無にかかわらず rollback 試行記録を残す
Note:
    - Phase 1 の最小実装として P1-2 の Mock Adapter を使用する
    - rollback 履歴はメモリ上にのみ保持する
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from adapters.mock_crm_adapter import MockCrmAdapter
from adapters.mock_line_adapter import MockLineAdapter
from adapters.mock_task_adapter import MockTaskAdapter


class RollbackManager:
    """rollback / compensating action を安全側で実行する。"""

    def __init__(self) -> None:
        """既知 adapter の対応表と rollback 履歴を初期化する。"""
        self._adapters = {
            "mock_crm": MockCrmAdapter(),
            "mock_line": MockLineAdapter(),
            "mock_task": MockTaskAdapter(),
        }
        self._records: list[dict[str, Any]] = []

    def rollback(self, request: dict[str, Any]) -> dict[str, Any]:
        """rollback request を評価して adapter へ委譲する。

        Args:
            request: execution_id / adapter / dry_run を含む rollback 要求

        Returns:
            rollback 結果の辞書
        """
        execution_id = str(request.get("execution_id") or "")
        adapter_name = request.get("adapter")
        dry_run = bool(request.get("dry_run", False))
        timestamp = datetime.now(UTC).isoformat()

        if not execution_id:
            result = {
                "status": "error",
                "execution_id": execution_id,
                "adapter": adapter_name,
                "dry_run": dry_run,
                "manual_intervention_required": True,
                "timestamp": timestamp,
            }
            self._records.append(result)
            return result

        adapter = self._adapters.get(str(adapter_name))
        if adapter is None:
            result = {
                "status": "manual_intervention_required",
                "execution_id": execution_id,
                "adapter": adapter_name,
                "dry_run": dry_run,
                "manual_intervention_required": True,
                "timestamp": timestamp,
            }
            self._records.append(result)
            return result

        adapter_result = adapter.rollback(execution_id)
        result = {
            "status": "rolled_back" if adapter_result.get("ok") else "error",
            "execution_id": execution_id,
            "adapter": adapter_name,
            "dry_run": dry_run,
            "manual_intervention_required": False,
            "timestamp": timestamp,
        }
        self._records.append(result)
        return result
