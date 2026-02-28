"""pytest実行時に `src/` 配下を import 可能にする設定。

本リポジトリではアプリ実装を `src/services/...` に配置するため、
テスト実行時に `services.*` を直接 import できるよう探索パスを調整する。
"""

import sys
from pathlib import Path

SRC_PATH = Path(__file__).parent / "src"

# テスト側から `services.*` を確実に参照できるよう先頭に追加する。
sys.path.insert(0, str(SRC_PATH))
