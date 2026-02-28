"""Phase 0 向けの最小 API エンドポイントを提供する。

入出力: HTTP GET /health -> {"status": "ok"}。
制約:
    - /health は常に 200 を返す
    - レスポンス構造は status フィールドのみを返す

Note:
    - T0-5-1 ではヘルスチェックのみ実装対象とする
    - 業務変換系エンドポイントは後続タスクで追加する
"""

from fastapi import FastAPI

app = FastAPI(title="subjective-agent-architecture", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    """ヘルスチェック結果を返す。

    Returns:
        dict[str, str]: サービス正常時に {"status": "ok"} を返す
    """
    return {"status": "ok"}
