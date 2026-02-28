"""pytest実行時にsrc配下のモジュール解決を行う設定。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
