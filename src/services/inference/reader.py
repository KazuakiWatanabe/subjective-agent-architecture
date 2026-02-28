"""自然文入力から state 候補を抽出する Reader を提供する。

入出力: text -> list[str]。
制約:
    - 空文字/None は受け付けない
    - スキーマ外の自由形式オブジェクトは返さない

Note:
    - LLM呼び出し失敗は ReaderError に変換する
    - _call_llm を分離し、テストでモック可能にする
"""

from __future__ import annotations

import re


class ReaderError(Exception):
    """Reader処理の失敗を表す例外。

    Note:
        - LLM呼び出しの例外や不正レスポンスを呼び出し側へ明示する
    """


class Reader:
    """自然文から state 候補を抽出するクラス。"""

    def extract(self, text: str) -> list[str]:
        """自然文入力を受け取り、state候補の文字列リストを返す。

        Args:
            text: state抽出対象の自然文

        Returns:
            抽出済み state の文字列リスト

        Raises:
            ValueError: text が None/空文字/文字列以外の場合
            ReaderError: LLM呼び出し失敗または戻り値が不正な場合

        Note:
            - 呼び出し結果は list[str] に正規化して返す
            - 空文字の要素は除去する
        """
        # テスト要件: 空入力は ValueError に統一する。
        if text is None or not isinstance(text, str) or text.strip() == "":
            raise ValueError("text must be a non-empty string")

        try:
            # テストでモックできるよう LLM呼び出しは専用メソッドに分離する。
            raw_states = self._call_llm(text)
        except Exception as exc:
            raise ReaderError("failed to extract states from input text") from exc

        if not isinstance(raw_states, list):
            raise ReaderError("llm response must be list[str]")

        # 型と空白を正規化し、空要素は除外する。
        states = [state.strip() for state in raw_states if isinstance(state, str) and state.strip()]
        if not states:
            raise ReaderError("no state extracted")

        return states

    def _call_llm(self, text: str) -> list[str]:
        """LLM呼び出しを模した抽出処理を行う。

        Args:
            text: 抽出対象の自然文

        Returns:
            state候補の文字列リスト

        Note:
            - Phase 0 では簡易実装として句読点で分割し先頭3件を採用する
            - 本番LLM接続時も戻り値契約は list[str] を維持する
        """
        # 句読点と改行で入力を分割し、state候補に変換する。
        parts = re.split(r"[。\n.!?、,]+", text)
        states = [part.strip() for part in parts if part.strip()]

        # 分割結果が空の場合は入力全体を1候補として扱う。
        if not states:
            return [text.strip()]

        # Phase 0 では過剰な候補数を抑えるため先頭3件まで返す。
        return states[:3]
