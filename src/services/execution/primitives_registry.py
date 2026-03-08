"""自然文アクションを Business Primitive 候補へ解決するレジストリを提供する。

概要:
    Phase 0B の next_actions を Planner 前段で扱える primitive 名へ正規化する。
入出力:
    actions -> list[dict]、primitive_name -> dict | None。
制約:
    - 対象 primitive は 5 種に限定する
    - 未知アクションは破棄せず manual_review_required=True で返す
    - 入力順を保持して決定論的に解決する
Note:
    - 判定は部分一致ベースの簡易実装とし、Phase 1 で拡張可能な形に留める
    - resolve_by_name は登録済み primitive の最小メタ情報を返す
"""

from __future__ import annotations


class PrimitivesRegistry:
    """自然文アクションと Business Primitive の対応を管理する。"""

    _REGISTRY: dict[str, dict[str, object]] = {
        "segment_customers": {
            "description": "顧客を条件に応じてセグメント分けする",
            "keywords": ("セグメント", "絞り込み", "対象顧客を抽出", "対象者を分け", "顧客を分類"),
        },
        "send_line_message": {
            "description": "LINE メッセージを配信する",
            "keywords": ("LINE", "配信", "メッセージ", "通知", "送る"),
        },
        "reserve_offer": {
            "description": "オファーを予約して後続フローへ渡す",
            "keywords": ("オファーを予約", "特典を確保", "特典を予約", "オファーを確保", "クーポンを取り置き"),
        },
        "cancel_offer": {
            "description": "既存オファーを取り消す",
            "keywords": ("オファーを取消", "オファーを取り消", "特典を取消", "特典をキャンセル", "予約を解除"),
        },
        "create_followup_task": {
            "description": "人手フォロー用のタスクを作成する",
            "keywords": ("フォロータスク", "フォロー", "タスクを作成", "確認タスク", "追客タスク"),
        },
    }

    def resolve(self, actions: list[str]) -> list[dict[str, object]]:
        """自然文アクションの配列を primitive 解決結果へ変換する。

        Args:
            actions: next_actions 由来の自然文アクション

        Returns:
            primitive 解決結果のリスト

        Note:
            - 空入力は空リストを返す
            - 未知アクションも結果に残し、手動確認フラグで扱う
        """
        if not actions:
            return []

        resolved_actions: list[dict[str, object]] = []
        for action in actions:
            resolved_actions.append(self._resolve_single_action(action))
        return resolved_actions

    def resolve_by_name(self, primitive_name: str) -> dict[str, object] | None:
        """primitive 名から登録済みメタ情報を取得する。

        Args:
            primitive_name: 取得対象の primitive 名

        Returns:
            登録済み primitive の情報。未登録なら None
        """
        primitive = self._REGISTRY.get(primitive_name)
        if primitive is None:
            return None

        return {
            "primitive": primitive_name,
            "description": primitive["description"],
            "manual_review_required": False,
        }

    def _resolve_single_action(self, action: str) -> dict[str, object]:
        """単一アクションを primitive または manual review へ解決する。"""
        normalized_action = action.strip()

        for primitive_name, definition in self._REGISTRY.items():
            keywords = definition["keywords"]
            # 評価順を固定し、同一文言に対して常に同じ primitive を返す。
            if any(keyword in normalized_action for keyword in keywords):
                return {
                    "action": normalized_action,
                    "primitive": primitive_name,
                    "manual_review_required": False,
                }

        return {
            "action": normalized_action,
            "primitive": None,
            "manual_review_required": True,
        }
