"""pytest 実行時に `src/` 配下を import 可能にする設定を提供する。

入出力: pytest起動時の初期化 -> sys.path 更新。
制約:
    - アプリ本体は `src/` 配下のみを探索対象にする
    - テストごとに個別パス設定を持ち込まない

Note:
    - `services.*` をテストから直接 import できる状態を維持する
    - 先頭挿入により同名モジュール競合の影響を最小化する
"""

import sys
from pathlib import Path

SRC_PATH = Path(__file__).parent / "src"

# テスト側から `services.*` を確実に参照できるよう先頭に追加する。
sys.path.insert(0, str(SRC_PATH))
