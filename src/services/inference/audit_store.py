"""Orchestrator の監査ログを保持する AuditStore を提供する。

入出力: record(dict) の保存 / 最新record(dict|None) の取得。
制約:
    - Phase 0 ではインメモリ保存のみを扱う
    - save/last のインターフェースを固定し、後続フェーズで差し替え可能にする

Note:
    - 保存時は deep copy を行い外部からの破壊的変更を防ぐ
    - last() は未保存時に None を返す
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


class AuditStore:
    """監査ログをインメモリで保持するクラス。"""

    def __init__(self) -> None:
        """空のログ配列で初期化する。"""
        self._records: list[dict[str, Any]] = []

    def save(self, record: dict[str, Any]) -> None:
        """監査ログを1件保存する。

        Args:
            record: 監査ログ辞書
        """
        self._records.append(deepcopy(record))

    def last(self) -> dict[str, Any] | None:
        """最新の監査ログを返す。

        Returns:
            dict[str, Any] | None: ログがない場合はNone
        """
        if not self._records:
            return None
        return deepcopy(self._records[-1])
