"""recommended_primitives から実行 plan を構築する Planner を提供する。

概要:
    subjective output に含まれる recommended_primitives を execution step へ正規化する。
入出力:
    payload -> plan。
制約:
    - dry_run をデフォルトで付与する
    - 未知 primitive は manual_review_required=True で残す
    - 入力順を保持して決定論的に step を生成する
Note:
    - Phase 1 の最小実装として、params は primitive ごとの簡易テンプレートを使う
    - Planner 自体は adapter 呼び出しを行わない
"""

from __future__ import annotations

from typing import Any


class Planner:
    """recommended_primitives を最小実行 plan に変換する。"""

    def build(self, payload: dict[str, Any]) -> dict[str, Any]:
        """subjective output から plan を生成する。

        Args:
            payload: state と recommended_primitives を含む辞書

        Returns:
            steps を含む plan 辞書
        """
        recommended_primitives = payload.get("recommended_primitives", [])
        states = payload.get("state", [])

        steps = [self._build_step(primitive, states) for primitive in recommended_primitives]
        return {"steps": steps}

    def _build_step(self, primitive: str, states: list[str]) -> dict[str, Any]:
        """primitive ごとの最小 step を返す。"""
        primary_state = states[0] if states else "unknown_state"
        step_templates = {
            "segment_customers": {
                "primitive": "segment_customers",
                "params": {"segment_rule": primary_state, "source_scope": "crm", "dry_run": True},
            },
            "send_line_message": {
                "primitive": "send_line_message",
                "params": {
                    "segment_id": f"segment-{primary_state}",
                    "message": f"{primary_state} 向けフォローメッセージ",
                    "dry_run": True,
                },
            },
            "reserve_offer": {
                "primitive": "reserve_offer",
                "params": {"customer_id": "cust-demo", "offer_id": "offer-demo", "dry_run": True},
            },
            "cancel_offer": {
                "primitive": "cancel_offer",
                "params": {"reservation_id": "reservation-demo", "reason": primary_state, "dry_run": True},
            },
            "create_followup_task": {
                "primitive": "create_followup_task",
                "params": {"customer_id": "cust-demo", "task_type": primary_state, "note": "follow-up", "dry_run": True},
            },
        }

        if primitive in step_templates:
            return step_templates[primitive]

        return {
            "primitive": primitive,
            "params": {"dry_run": True},
            "manual_review_required": True,
        }
