# CLAUDE.md
Subjective Agent Architecture ― Claude Code 向け実装ガイド

本ドキュメントは **Claude Code** が本リポジトリで作業する際の実装手順・コマンド・制約を定義します。  
プロジェクトの目的・スコープ・設計方針は `AGENTS.md` を参照してください。  
**AGENTS.md と本ドキュメントが矛盾する場合は AGENTS.md を優先します。**

---

## 1. 作業開始前の確認事項

新しいセッションを開始したら、必ず以下の順で読み込んでください。

```
1. AGENTS.md          # 最上位ルール・スコープ制約
2. task/task-breakdown-v2.md  # タスク定義・完了条件・テストコード
3. 本ファイル（CLAUDE.md）   # 実装コマンド・操作手順
```

---

## 2. 環境セットアップ

### 依存ライブラリのインストール

```bash
pip install -r requirements.txt
```

`requirements.txt` に含めるべき最小構成：

```
fastapi
uvicorn[standard]
jsonschema
pydantic
```

### Vertex AI 認証（ローカル実行時）

```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

### パス確認

```bash
# src/ が Python パスに通っていることを確認
python -c "from services.inference.reader import Reader; print('OK')"
```

---

## 3. テストの実行

### 基本コマンド

```bash
# 全テスト実行
pytest

# タスク単位で実行
pytest test/contracts/test_state_intent_schema.py -v
pytest test/agents/test_reader.py -v
pytest test/agents/test_validator.py -v
pytest test/agents/test_generator.py -v
pytest test/agents/test_orchestrator.py -v
pytest test/agents/test_orchestrator_audit.py -v
pytest test/contracts/test_presets.py -v

# 統合テスト（サーバー起動後）
DEMO_URL=http://localhost:8080 pytest test/integration/ -v
```

### エビデンス保存（タスク完了時に必ず実行）

```bash
pytest test/contracts/test_state_intent_schema.py -v > test/evidence/T0-2-1_test_result.txt
pytest test/agents/test_reader.py             -v > test/evidence/T0-3-1_test_result.txt
pytest test/agents/test_validator.py          -v > test/evidence/T0-3-2_test_result.txt
pytest test/agents/test_generator.py          -v > test/evidence/T0-3-3_test_result.txt
pytest test/agents/test_orchestrator.py       -v > test/evidence/T0-3-4_test_result.txt
pytest test/agents/test_orchestrator_audit.py -v > test/evidence/T0-3-4a_test_result.txt
pytest test/contracts/test_presets.py         -v > test/evidence/T0-4-1_test_result.txt
pytest test/integration/test_health.py        -v > test/evidence/T0-5-1_test_result.txt
pytest test/integration/test_convert_e2e.py   -v > test/evidence/T0-5-2_test_result.txt
```

---

## 4. ローカル開発サーバー

### Docker を使う（推奨）

```bash
# ビルド＆起動
docker compose up --build

# バックグラウンド起動
docker compose up --build -d

# ログ確認
docker compose logs -f

# 停止
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

## 5. 実装手順（タスク順）

`task/task-breakdown-v2.md` のタスク順に従います。各ステップで **テストを先に読んでから実装**してください。

```
Step 1  src/contracts/state_intent.schema.json
        → test/contracts/test_state_intent_schema.py を読んでから作成

Step 2  src/services/inference/reader.py
        → test/agents/test_reader.py を読んでから実装

Step 3  src/services/inference/validator.py
        → test/agents/test_validator.py を読んでから実装

Step 4  src/services/inference/generator.py
        → test/agents/test_generator.py を読んでから実装

Step 5  src/services/inference/orchestrator.py
        → test/agents/test_orchestrator.py を読んでから実装

Step 6  src/services/inference/audit_store.py
        → test/agents/test_orchestrator_audit.py を読んでから実装

Step 7  src/contracts/presets.json
        → test/contracts/test_presets.py を読んでから作成

Step 8  サーバー起動 → test/integration/ を実行
```

---

## 6. 実装上の制約（Claude Code が守るべきルール）

### やってはいけないこと

| 禁止事項 | 理由 |
|---|---|
| `action_bindings` の `dry_run` を `false` にする | Phase 0 では本番API実行禁止 |
| テストを削除・スキップして PASS させる | エビデンスの改ざんに相当する |
| `src/` 以外に実装コードを置く | パス構造変更禁止（AGENTS.md §3） |
| Phase 1 以降の機能（DB永続化・本番API等）を先行実装する | スコープ拡張禁止 |
| `audit_store.save()` の呼び出しを省略する | 成功・失敗いずれでも Audit Log は必須 |

### 必ずやること

- 各タスク完了後に `test/evidence/` へエビデンスを保存する
- `ValidationResult(ok=False)` を受け取った `Generator` は `GeneratorError` を raise する
- `MaxRetryError` 発生時も `audit_store.save(status="failed")` を呼び出す
- スキーマ変更時は `test/contracts/test_state_intent_schema.py` を再実行して全件PASS を確認する

---

## 7. ファイル別の実装メモ

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
- **Phase 0 では `action_bindings` の `dry_run` を常に `True` に強制する**

### `src/services/inference/orchestrator.py`

- `run(input_text: str) -> dict` を実装する
- Retry 上限は `2`（初回 + 再試行2回 = 計3回）
- `audit_store` を `__init__` で初期化し、`self.audit_store` として保持する
- 成功時：`audit_store.save(status="success", trace_id=..., input_text=..., state=..., timestamp=...)`
- 失敗時：`audit_store.save(status="failed", error=..., input_text=..., timestamp=...)`

### `src/services/inference/audit_store.py`

- Phase 0 はインメモリ実装（`list` で保持）
- `save(record: dict) -> None` と `last() -> dict | None` を実装する
- Phase 1 で DB 永続化に差し替える前提でインターフェースを固定する

---

## 8. Cloud Run デプロイ

```bash
# プロジェクト設定
gcloud config set project YOUR_PROJECT_ID

# Cloud Build でビルド＆デプロイ
gcloud builds submit --config cloudbuild.yaml .

# デプロイ後の E2E テスト
DEMO_URL=https://YOUR_CLOUD_RUN_URL pytest test/integration/ -v \
  > test/evidence/T0-5-2_test_result.txt
```

デプロイ後、`DEMO_URL` を実際の Cloud Run URL に置き換えて E2E テストを実行し、エビデンスを保存してください。

---

## 9. ブランチ戦略

### 基本方針

本リポジトリは **Git Flow** を採用します。  
`main` および `develop` への直接 push は禁止です。すべての変更は Pull Request 経由でマージします。

### ブランチ構成

```
main          本番相当（Cloud Run デプロイ済みの状態）
develop       統合ブランチ（Phase 0 完了時に main へマージ）
feature/      機能実装（develop から分岐）
release/      リリース準備（develop → main への橋渡し）
hotfix/       main の緊急修正
```

### ブランチ命名規則

```
feature/{タスクID}-{説明}
release/phase-{フェーズ番号}
hotfix/{内容}

例：
  feature/T0-2-1-schema
  feature/T0-3-1-reader
  feature/T0-3-2-validator
  feature/T0-3-3-generator
  feature/T0-3-4-orchestrator
  feature/T0-3-4a-audit-log
  feature/T0-4-1-presets
  feature/T0-5-1-health
  feature/T0-5-2-e2e
  release/phase-0
  hotfix/schema-minItems-fix
```

### 通常フロー（feature → develop）

```bash
# 1. develop を最新化
git checkout develop
git pull origin develop

# 2. feature ブランチを作成
git checkout -b feature/T0-3-1-reader

# 3. 実装 → テスト → エビデンス保存
pytest test/agents/test_reader.py -v > test/evidence/T0-3-1_test_result.txt

# 4. コミット
git add src/services/inference/reader.py test/evidence/T0-3-1_test_result.txt
git commit -m "T0-3-1: Reader実装 - state候補抽出・ReaderError対応"

# 5. push
git push origin feature/T0-3-1-reader

# 6. GitHub で PR を作成（base: develop）→ レビュー → マージ
```

### リリースフロー（develop → main）

Phase 0 完了チェックリストが全件クリアされたタイミングで実施します。

```bash
# 1. release ブランチを develop から作成
git checkout develop
git pull origin develop
git checkout -b release/phase-0

# 2. 最終確認（全テスト・エビデンス・E2E）
pytest
DEMO_URL=https://YOUR_CLOUD_RUN_URL pytest test/integration/ -v \
  > test/evidence/T0-5-2_test_result.txt

# 3. PR を作成（base: main）→ マージ
# 4. main にマージ後、develop にもマージしてブランチを削除
git checkout main && git pull origin main
git checkout develop && git merge main
git push origin develop
git branch -d release/phase-0
git push origin --delete release/phase-0

# 5. main に tag を打つ
git checkout main
git tag -a phase-0 -m "Phase 0 完了"
git push origin phase-0
```

### hotfix フロー（main の緊急修正）

```bash
# 1. main から hotfix ブランチを作成
git checkout main
git pull origin main
git checkout -b hotfix/schema-minItems-fix

# 2. 修正 → テスト
# 3. PR を作成（base: main）→ マージ
# 4. develop にも反映
git checkout develop
git merge main
git push origin develop
```

### コミットメッセージ規則

```
{タスクID}: {実装内容の要約}

例：
  T0-2-1: state_intent.schema.json作成 - action_bindings追加
  T0-3-2: Validator実装 - 重複stateチェック・action_bindings空配列NG対応
  T0-3-4a: AuditStore実装 - 失敗時ログ保存・trace_id紐付け
```

### Pull Request のルール

| 項目 | ルール |
|---|---|
| タイトル | `{タスクID}: {内容}` の形式 |
| base ブランチ | feature → `develop`、release/hotfix → `main` |
| 説明 | 完了条件（task-breakdown-v2.md 記載）を箇条書きで転記する |
| エビデンス | `test/evidence/{タスクID}_test_result.txt` が含まれていること |
| テスト | PR 時点で全件 PASS していること |
| レビュー | セルフマージ可（Phase 0 は1名運用を前提） |

### ブランチ保護設定（GitHub Settings）

**main**
```
Settings → Branches → Branch protection rules → Add rule

対象ブランチ: main
✅ Require a pull request before merging
✅ Require status checks to pass before merging
✅ Do not allow bypassing the above settings
```

**develop**
```
対象ブランチ: develop
✅ Require a pull request before merging
✅ Do not allow bypassing the above settings
```

### タスク順とブランチの対応表

| ブランチ名 | 対応タスク | base | 依存 |
|---|---|---|---|
| `feature/T0-2-1-schema` | スキーマ作成 | develop | なし |
| `feature/T0-3-1-reader` | Reader実装 | develop | T0-2-1 |
| `feature/T0-3-2-validator` | Validator実装 | develop | T0-2-1 |
| `feature/T0-3-3-generator` | Generator実装 | develop | T0-3-2 |
| `feature/T0-3-4-orchestrator` | Orchestrator実装 | develop | T0-3-1〜3 |
| `feature/T0-3-4a-audit-log` | AuditStore実装 | develop | T0-3-4 |
| `feature/T0-4-1-presets` | presets.json作成 | develop | なし |
| `feature/T0-5-1-health` | ヘルスチェック確認 | develop | デプロイ後 |
| `feature/T0-5-2-e2e` | E2Eテスト | develop | T0-5-1 |
| `release/phase-0` | Phase 0リリース | main | 全タスク完了後 |

> **Note**  
> 依存タスクのブランチが develop にマージされていない状態で次の feature ブランチを作る場合は、  
> `develop` ではなく依存 feature ブランチから分岐して作業し、PR のベースブランチを調整してください。

---

## 10. トラブルシューティング

| 症状 | 確認箇所 |
|---|---|
| `ModuleNotFoundError: services` | `conftest.py` が存在するか、`PYTHONPATH=src` が設定されているか確認 |
| `jsonschema.ValidationError` | `src/contracts/state_intent.schema.json` の必須項目・minItems を確認 |
| `ReaderError` が発生する | Vertex AI の認証（`gcloud auth application-default login`）を確認 |
| `MaxRetryError` が多発する | Reader の LLM プロンプトが state を3件以上返しているか確認 |
| E2E が不安定（安定率 < 8/10） | Generator のプロンプトに「必ずJSON形式で返す」旨を明示する |
| `dry_run` が `false` になっている | `generator.py` の `action_bindings` 生成部分を確認。Phase 0 では `True` 固定 |
