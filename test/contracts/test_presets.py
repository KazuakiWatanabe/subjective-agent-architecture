"""presets.json の存在と構造を検証するテストを提供する。

入出力: presets.json 読み込み -> 構造検証。
制約:
    - 各要素は label と text を持つ
    - text は空文字を許可しない

Note:
    - T0-4-1 は UI 実装を含まず、ファイル契約のみを検証する
"""

import json
from pathlib import Path

PRESETS_PATH = Path(__file__).parent.parent.parent / "src/contracts/presets.json"


def test_presets_file_exists():
    """presets ファイルが存在することを確認する。"""
    assert PRESETS_PATH.exists()


def test_presets_has_at_least_one_entry():
    """最低1件以上のプリセットがあることを確認する。"""
    presets = json.loads(PRESETS_PATH.read_text(encoding="utf-8"))
    assert len(presets) >= 1


def test_each_preset_has_label_and_text():
    """各プリセットが label と text を持つことを確認する。"""
    presets = json.loads(PRESETS_PATH.read_text(encoding="utf-8"))
    for preset in presets:
        assert "label" in preset
        assert "text" in preset
        assert len(preset["text"]) > 0


def test_preset_text_is_not_empty_string():
    """text が空白のみでないことを確認する。"""
    presets = json.loads(PRESETS_PATH.read_text(encoding="utf-8"))
    for preset in presets:
        assert preset["text"].strip() != ""
