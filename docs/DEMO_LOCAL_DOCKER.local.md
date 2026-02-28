# ローカルデモ（Docker）※scriptディレクトリから実行する版

この手順は **ローカル環境専用** です（Cloud Run 等は対象外）。  
Windows + PowerShell を前提にしています。

---

## ✅ 実行前提

リポジトリ構成（例）:

```
subjective-agent-architecture/
  Dockerfile.local
  docker-compose.local.yml
  docker-compose.local.with-tests.yml（自動生成）
  docs/
  script/
    demo.local.ps1
    demo.local.with-tests.ps1
  src/
  test/
```

---

# 🚀 推奨実行方法（scriptフォルダから実行）

## 1️⃣ script フォルダへ移動

```powershell
cd C:\Git\subjective-agent-architecture\script
```

## 2️⃣ 一時的にスクリプト実行を許可（このウィンドウのみ有効）

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## 3️⃣ テスト + デモを自動実行

```powershell
.\demo.local.with-tests.ps1
```

---

# 🔄 スクリプトが行う処理

このスクリプトは内部で以下を自動実行します：

1. リポジトリルートを自動検出
2. docker-compose.local.with-tests.yml を生成
3. Docker build
4. test コンテナで pytest 実行
5. pytestログを保存（test\evidence\pytest.local.YYYYMMDD-HHMMSS.log）
6. app をバックグラウンド起動
7. /health 確認
8. /convert を社内向けプリセットで複数実行
9. 空入力（400エラー）確認

---

# 🧪 pytestログ保存場所

```
subjective-agent-architecture/
  test/
    evidence/
      pytest.local.20260228-135143.log
```

社内説明用の「再現性の証拠」として使用できます。

---

# 🛑 停止方法

```powershell
docker compose -f ..\docker-compose.local.with-tests.yml down
```

※ script ディレクトリから実行しているため、`..\` を付けています。

---

# 📌 単体デモのみ実行したい場合

```powershell
cd C:\Git\subjective-agent-architecture\script
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\demo.local.ps1
```

---

# ❗ よくあるハマり

### PowerShellで「実行できない」エラー
→ `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` を実行していない

### ポート 8080 が使用中
→ 既存コンテナを停止

```
docker compose -f ..\docker-compose.local.with-tests.yml down
```

---

# 🎯 デモの見せ方（社内向け）

1. state が分割されること
2. intent が明示されること
3. next_actions が施策に接続されること
4. dry_run=true（安全設計）
5. rollback_plan が存在すること
6. trace_id により監査可能であること

---

これで **「動く」+「再現できる」+「証拠が残る」デモ環境** になります。
