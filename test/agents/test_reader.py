"""Readerの振る舞いを検証するテスト。

観点:
    - 正常系: list[str] を返す
    - 異常系: 空入力とLLM失敗時の例外契約
"""

from unittest.mock import patch

import pytest

from services.inference.reader import Reader, ReaderError


@pytest.fixture
def reader():
    """テストで共通利用する Reader インスタンスを返す。"""
    return Reader()


def test_reader_returns_state_list(reader):
    """Readerが state の list を返すことを確認する。"""
    # Arrange/Act: _call_llm をモックし、返却型契約を検証する。
    with patch.object(reader, "_call_llm", return_value=["来店頻度低下", "価格感度低", "限定感志向"]):
        result = reader.extract("最近来店が減っている。値引きには反応しないが、限定感には反応する。")
    # Assert: list 型かつ1件以上で返ること。
    assert isinstance(result, list)
    assert len(result) >= 1


def test_reader_returns_at_least_one_state(reader):
    """最小1件以上の state を返すことを確認する。"""
    with patch.object(reader, "_call_llm", return_value=["来店頻度低下"]):
        result = reader.extract("何か変化があった")
    assert len(result) >= 1


def test_reader_raises_on_llm_failure(reader):
    """LLM呼び出し失敗時に ReaderError が送出されることを確認する。"""
    # LLM由来の例外を ReaderError に変換する契約を確認する。
    with patch.object(reader, "_call_llm", side_effect=Exception("LLM error")):
        with pytest.raises(ReaderError):
            reader.extract("テスト入力")


def test_reader_raises_on_empty_input(reader):
    """空文字入力時に ValueError となることを確認する。"""
    with pytest.raises(ValueError):
        reader.extract("")


def test_reader_raises_on_none_input(reader):
    """None入力時に ValueError となることを確認する。"""
    with pytest.raises(ValueError):
        reader.extract(None)
