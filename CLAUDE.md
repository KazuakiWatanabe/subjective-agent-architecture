# CLAUDE.md
Subjective Agent Architecture ― Claude Code 向け実装ガイド

本ドキュメントは **Claude Code** が本リポジトリで作業する際の実装手順・コマンド・制約を定義します。  
プロジェクトの目的・スコープ・設計方針は `AGENTS.md` を参照してください。  
**AGENTS.md と本ドキュメントが矛盾する場合は AGENTS.md を優先します。**

---

## 1. 作業開始前の確認事項

新しいセッションを開始したら、必ず以下の順で読み込んでください。

```
1. AGENTS.md                              # 最上位ルール・スコープ制約・セキュリティルール
2. docs/roadmap_churn_whitepaper_v1.md    # 現行ロードマップ・現フェーズの完了条件
3. task/task-breakdown-v2.md              # タスク定義・テストコード（Phase 0 実績）
4. 本ファイル（CLAUDE.md）               # 実装コマンド・操作手順
```

> **現在の実装フェーズ**  
> Phase 0 は完了済みです。現在は **Phase 0B〜Phase 1** の移行期にあります。  
> 作業対象タスクは `docs/roadmap_churn_whitepaper_v1.md` §6 を確認してから着手してください。

---

## 2. 環境セットアップ

### 依存ライブラリのインストール

```bash
pip install -r requirements.txt
```

### セキュリティスキャン（インストール後に必ず実行）

```bash
pip install pip-audit
pip-audit > test/evidence/security_audit.txt
```

`pip-audit` で脆弱性が検出された場合は、対象パッケージを修正してから作業を進めてください。

### Vertex AI 認証（ローカル実行時）

```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

### パス確認

```bash
python -c "from services.inference.reader import Reader; print('OK')"
```

---

## 3. テストの実行

### 基本コマンド

```bash
# 全テスト実行
pytest

# モジュール単位で実行
pytest test/contracts/ -v
pytest test/agents/    -v

# 統合テスト（サーバー起動後）
DEMO_URL=http://localhost:8080 pytest test/integration/ -v
```

### エビデンス保存

```bash
pytest test/contracts/ -v > test/evidence/contracts_test_result.txt
pytest test/agents/    -v > test/evidence/agents_test_result.txt
pytest test/integration/test_health.py       -v > test/evidence/integration_health_result.txt
pytest test/integration/test_convert_e2e.py  -v > test/evidence/integration_e2e_result.txt
```

---

## 4. ローカル開発サーバー

### Docker を使う（推奨）

```bash
docker compose up --build
docker compose up --build -d   # バックグラウンド起動
docker compose logs -f
docker compose down
```

### Docker なしで起動する場合

```bash
PYTHONPATH=src uvicorn services.api.main:app --reload --port 8080
```

### 動作確認

```bash
curl http://localhost:8080/health

curl -X POST http://localhost:8080/convert \
  -H "Content-Type: application/json" \
  -d '{"text": "最近来店が減っている。値引きには反応しないが、限定感には反応する。"}'
```

---

## 5. 現フェーズの実装手順

現フェーズ（Phase 0B / Phase 1）のタスクを着手する際は、必ず以下の順で進めてください。

```
Step 0  pip-audit を実行し、依存パッケージに脆弱性がないことを確認する
        → test/evidence/security_audit.txt に結果を保存する

Step 1  docs/roadmap_churn_whitepaper_v1.md §6 で現フェーズのタスクと完了条件を確認する

Step 2  対応するテストコードを読んでから実装する（テスト先読みの原則）

Step 3  実装 → pytest 全件PASS → test/evidence/ へエビデンス保存

Step 4  AGENTS.md §12 のセキュリティチェックリストを確認してから PR を作成する
```

### Phase 0B の主要タスク（参考）

| タスク | 内容 |
|---|---|
| state語彙の再調整 | チャーン文脈（来店頻度低下 / 予算逼迫 / 限定感志向 等）へ寄せる |
| Trait/State/Meta最小表現 | 3層を出力JSONに最低限含める |
| next_actionsの業務原子化 | 自然文ではなく Business Primitives に寄せる |
| KPI仮定義メモ | 再来店率 / 30日継続率 / 施策反応率 / 誤配信率 を仮置きする |
| デモ資料修正 | 「構造説明」から「施策判断支援」へ切り替える |

### Phase 1 の主要タスク（参考）

| タスク | 内容 |
|---|---|
| Business Primitives定義 | `segment_customers` / `send_line_message` / `create_followup_task` 等 |
| Mock Adapter実装 | `validate` / `execute` / `rollback` / `audit` の最小インターフェース |
| 実行フロー | Validate → Plan → Apply の一連フロー |
| dry_run / approval gate | 本番実行前の承認ゲート |
| Audit Log拡張 | 業務実行ログの保存 |

---

## 6. 実装上の制約

### やってはいけないこと

| 禁止事項 | 理由 |
|---|---|
| `action_bindings` の `dry_run` を `false` にする | Phase 1 完了まで本番API実行禁止 |
| テストを削除・スキップして PASS させる | エビデンスの改ざんに相当する |
| `src/` 以外に実装コードを置く | パス構造変更禁止（AGENTS.md §3） |
| Phase 2 以降の機能（Meta学習ループ・DB永続化等）を先行実装する | スコープ拡張禁止 |
| `audit_store.save()` の呼び出しを省略する | 成功・失敗いずれでも Audit Log は必須 |
| 既存ファイルの `import` を確認なしに新ファイルへ踏襲する | サプライチェーン攻撃の踏襲リスク（AGENTS.md §12） |
| `requirements.txt` 未記載のパッケージを使用する | 許可リスト外パッケージの使用禁止 |
| `os.environ` / `os.getenv` の値を外部URLへ送信する | 環境変数の外部送信禁止 |

### 必ずやること

- 各タスク完了後に `test/evidence/` へエビデンスを保存する
- 新しいファイルで既存パッケージを `import` する前に `requirements.txt` への記載を確認する
- パッケージを追加する際は PyPI公式ページとソースコードを確認してから `requirements.txt` へ追記する
- Pythonファイル先頭に「概要」「入出力」「制約」「Note」を含む日本語docstringを必須とする
- 関数/メソッドでは必要に応じて `Args / Returns / Raises / Note` を記述する
- 条件分岐や補完ロジックなど意図が読み取りづらい処理には1〜2行の補助コメントを追加する

---

## 7. 既存ファイル別の実装メモ

### `src/services/inference/reader.py`

- `extract(input_text: str) -> list[str]` を実装する
- `input_text` が `None` または空文字の場合は `ValueError` を raise する
- LLM 呼び出しは `_call_llm(input_text)` に分離する（テストでモック対象になる）
- LLM 呼び出し失敗時は `ReaderError` を raise する

### `src/services/inference/validator.py`

- `validate(payload: dict) -> ValidationResult` を実装する
- `ValidationResult` は `ok: bool` と `issues: list[str]` を持つ dataclass とする
- `state` の重複検出時は `issues` に `"重複"` を含む文字列を追加する
- `action_bindings` が空配列の場合は `issues` に `"action_bindings"` を含む文字列を追加する

### `src/services/inference/generator.py`

- `generate(payload: dict, validation_result: ValidationResult) -> dict` を実装する
- `validation_result.ok` が `False` の場合は `GeneratorError` を raise する
- `trace_id` は `uuid.uuid4()` で生成する
- `generated_at` は `datetime.utcnow().isoformat()` で生成する
- **`action_bindings` の `dry_run` を常に `True` に強制する（Phase 1 完了まで）**

### `src/services/inference/orchestrator.py`

- `run(input_text: str) -> dict` を実装する
- Retry 上限は `2`（初回 + 再試行2回 = 計3回）
- 成功時：`audit_store.save(status="success", trace_id=..., input_text=..., state=..., timestamp=...)`
- 失敗時：`audit_store.save(status="failed", error=..., input_text=..., timestamp=...)`

### `src/services/inference/audit_store.py`

- 現在はインメモリ実装（`list` で保持）
- `save(record: dict) -> None` と `last() -> dict | None` を実装する
- Phase 1 の Audit Log 拡張時もインターフェースを維持したまま差し替える

---

## 8. Cloud Run デプロイ

```bash
gcloud config set project YOUR_PROJECT_ID
gcloud builds submit --config cloudbuild.yaml .

# デプロイ後の E2E テスト
DEMO_URL=https://YOUR_CLOUD_RUN_URL pytest test/integration/ -v \
  > test/evidence/integration_e2e_result.txt
```

---

## 9. ブランチ戦略

### 基本方針

本リポジトリは **Git Flow** を採用します。  
`main` および `develop` への直接 push は禁止です。すべての変更は Pull Request 経由でマージします。

### ブランチ命名規則

```
feature/{フェーズ}-{説明}
release/phase-{フェーズ番号}
hotfix/{内容}

例：
  feature/P0B-churn-vocab
  feature/P0B-kpi-hypothesis
  feature/P1-primitives-spec
  feature/P1-mock-adapter
  release/phase-1
  hotfix/schema-minItems-fix
```

### 通常フロー（feature → develop）

```bash
git checkout develop && git pull origin develop
git checkout -b feature/P0B-churn-vocab

# 実装 → テスト → エビデンス保存
pytest test/agents/ -v > test/evidence/agents_test_result.txt

git add src/ test/evidence/
git commit -m "P0B: state語彙をチャーン文脈へ再調整"
git push origin feature/P0B-churn-vocab
# GitHub で PR を作成（base: develop）→ レビュー → マージ
```

### リリースフロー（develop → main）

```bash
git checkout develop && git pull origin develop
git checkout -b release/phase-1

# 最終確認
pytest
pip-audit > test/evidence/security_audit.txt
DEMO_URL=https://YOUR_CLOUD_RUN_URL pytest test/integration/ -v \
  > test/evidence/integration_e2e_result.txt

# PR 作成（base: main）→ マージ後
git checkout main && git pull origin main
git checkout develop && git merge main && git push origin develop
git branch -d release/phase-1 && git push origin --delete release/phase-1

git checkout main
git tag -a phase-1 -m "Phase 1 完了"
git push origin phase-1
```

### Pull Request のルール

| 項目 | ルール |
|---|---|
| タイトル | `{フェーズ-タスク}: {内容}` の形式 |
| base ブランチ | feature → `develop`、release/hotfix → `main` |
| 説明 | `roadmap_churn_whitepaper_v1.md` 記載の完了条件を箇条書きで転記する |
| エビデンス | `test/evidence/` に対応する結果ファイルが含まれていること |
| テスト | PR 時点で全件 PASS していること |
| セキュリティ | AGENTS.md §12 のコードレビューチェックリストを確認済みであること |
| レビュー | セルフマージ可（1名運用を前提） |

---

## 10. トラブルシューティング

| 症状 | 確認箇所 |
|---|---|
| `ModuleNotFoundError: services` | `conftest.py` が存在するか、`PYTHONPATH=src` が設定されているか確認 |
| `jsonschema.ValidationError` | `src/contracts/state_intent.schema.json` の必須項目・minItems を確認 |
| `ReaderError` が発生する | Vertex AI の認証（`gcloud auth application-default login`）を確認 |
| `MaxRetryError` が多発する | Reader の LLM プロンプトが state を3件以上返しているか確認 |
| E2E が不安定（安定率 < 8/10） | Generator のプロンプトに「必ずJSON形式で返す」旨を明示する |
| `dry_run` が `false` になっている | `generator.py` の `action_bindings` 生成部分を確認。Phase 1 完了まで `True` 固定 |
| `pip-audit` で脆弱性が検出された | 対象パッケージのバージョンを上げるか代替パッケージを検討する。修正前に作業を進めない |
| 既存コードにあるパッケージが `requirements.txt` にない | そのパッケージを新ファイルで使用してはならない。経緯を確認してから `requirements.txt` へ追記するか削除する |
