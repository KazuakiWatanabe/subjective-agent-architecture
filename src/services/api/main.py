"""Phase 0 向けの最小 API エンドポイントを提供する。

入出力: GET /health, POST /convert -> JSONレスポンス。
制約:
    - /health は常に 200 と {"status":"ok"} を返す
    - /convert は空入力時に 400 を返し、成功時は schema 準拠JSONを返す

Note:
    - /convert は Orchestrator を経由して Reader->Validator->Generator を実行する
    - 失敗時レスポンスは業務詳細を漏らさない最小情報に留める
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from services.inference.orchestrator import MaxRetryError, Orchestrator

app = FastAPI(title="subjective-agent-architecture", version="0.1.0")
orchestrator = Orchestrator()


class ConvertRequest(BaseModel):
    """/convert のリクエストボディ。

    Args:
        text: 変換対象の自然文
    """

    text: str | None = None


@app.get("/health")
def health() -> dict[str, str]:
    """ヘルスチェック結果を返す。

    Returns:
        dict[str, str]: サービス正常時に {"status": "ok"} を返す
    """
    return {"status": "ok"}


@app.post("/convert")
def convert(req: ConvertRequest) -> dict[str, object]:
    """自然文を state-intent JSON へ変換する。

    Args:
        req: text を含む入力モデル

    Returns:
        dict[str, object]: schema 準拠の変換結果

    Raises:
        HTTPException: 入力不正または変換失敗時
    """
    text = (req.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="text must not be empty")

    try:
        return orchestrator.run(text)
    except MaxRetryError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
