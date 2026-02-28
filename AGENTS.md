# AGENTS.md
Subjective Agent Architecture ― 最上位ルール定義書（日本語）

本ドキュメントは、本リポジトリに関わる **すべてのAI（Codex等）と人間**が遵守すべき最上位ルールです。  
README や設計資料よりも **AGENTS.md を優先**します。

本プロジェクトは `task/task-breakdown-v2.md` に基づいて実装します。  
**Phase 0（社内モック）完了まではスコープ拡張を禁止**します。

---

## 1. プロジェクトの目的（Phase 0）

本プロジェクトは、自然文（社内で刺さる現場の言葉）から

- **state / intent / next_actions**
- **rollback_plan（安全性）**
- **action_bindings（業務接続の足場）**
- **監査ログ（説明責任）**

を備えた **決定論的なJSON** を生成し、社内が「触って判断できる」デモを最短で成立させます。

### Phase 0 の最小ゴール

- `POST /convert` に自然文を渡すと、`src/contracts/state_intent.schema.json` に **準拠したJSON** を返す
- **Retry Loop** により、Validator NG を最大2回まで再試行する
- 成功・失敗いずれの場合も **Audit Log を残す**
- すべて `pytest` がPASSし、証跡を `test/evidence/` に保存する

---

## 2. 最上位のスコープ制約（必須）

- Phase 0 の間は **「社内モック」以外を実装しない**
- 外部APIの本番実行（配信や更新など）は **禁止**（`dry_run: true` のみ）
- UIやインフラは **必要最低限**（デモ成立が目的）

> **Note**  
> Phase 1（実業務接続）以降の設計は、Phase 0 完了後に別タスクで追加する

---

## 3. リポジトリ構造（前提）

本リポジトリは以下の構造を前提とします（**変更禁止**）。

```
subjective-agent-architecture/
  docs/
    whitepaper.md               # アーキテクチャ設計書
  task/
    task-breakdown-v2.md        # タスク定義（本ドキュメントより詳細な実装指示）
  test/
    contracts/
      test_state_intent_schema.py
      test_presets.py
    agents/
      test_reader.py
      test_validator.py
      test_generator.py
      test_orchestrator.py
      test_orchestrator_audit.py
    integration/
      test_health.py
      test_convert_e2e.py
    evidence/                   # pytest -v の出力結果（自動生成）
  src/
    contracts/
      state_intent.schema.json  # 出力スキーマ定義
      presets.json              # デモ用プリセット入力
    services/
      inference/
        reader.py
        validator.py
        generator.py
        orchestrator.py
        audit_store.py
  Dockerfile
  docker-compose.yml
  cloudbuild.yaml
  .dockerignore
  conftest.py                   # sys.path 解決（src/ をルートに追加）
  pytest.ini                    # testpaths = test
  AGENTS.md                     # 本ファイル（最上位ルール）
  CLAUDE.md                     # Claude Code 向け実装ガイド
  LICENSE
  README.md
```

---

## 4. エージェント構成

本リポジトリのエージェント構成は **Reader → Validator → Generator** の3層です。

```
自然文入力
    ↓
Reader        src/services/inference/reader.py
              自然文から state 候補リストを抽出する
    ↓
Validator     src/services/inference/validator.py
              state_intent.schema.json に対してペイロードを検証する
              NG の場合は Reader に差し戻し（最大2回 Retry）
    ↓
Generator     src/services/inference/generator.py
              Validator 通過済みデータのみを受け取り、JSON を生成する
              trace_id（UUID）・generated_at（ISO8601）を自動付与する
    ↓
JSON出力（schema準拠）
```

> **Note：agentic-bizflow との相違について**  
> [agentic-bizflow](https://github.com/KazuakiWatanabe/agentic-bizflow) は  
> Reader → **Planner** → Validator → Generator の4層構成です。  
> 本リポジトリは **state/intent変換** に特化した別ドメインのため、  
> Planner を持たない3層構成を意図的に採用しています。

---

## 5. Orchestrator の動作仕様

`src/services/inference/orchestrator.py` は以下の制御フローを実装します。

```
orchestrator.run(input_text)
    │
    ├─ Reader.extract(input_text)
    │
    ├─ Validator.validate(payload)
    │     ├─ OK  → Generator.generate(payload, validation_result)
    │     │              └─ audit_store.save(status="success")
    │     │                       └─ return JSON
    │     │
    │     └─ NG  → Retry（最大2回）
    │               ├─ 2回以内に OK → Generator へ
    │               └─ 2回超過    → audit_store.save(status="failed")
    │                                      └─ raise MaxRetryError
    │
    └─ ※ 成功・失敗いずれの場合も Audit Log を保存する
```

---

## 6. Audit Log 仕様

`src/services/inference/audit_store.py` はインメモリ実装とします。

| フィールド | 型 | 説明 |
|---|---|---|
| `trace_id` | string | Generator が付与した UUID（失敗時は Orchestrator が生成） |
| `input_text` | string | 元の自然文入力 |
| `state` | list[str] | Reader が抽出した state |
| `status` | string | `"success"` または `"failed"` |
| `timestamp` | string | ISO8601形式 |
| `error` | string | 失敗時のみ。MaxRetryError のメッセージ |

> **Phase 1 移行時**：`audit_store.py` のインターフェースを維持したまま、  
> インメモリ実装をDB永続化（Cloud Firestore等）に差し替える。

---

## 7. スキーマ制約

`src/contracts/state_intent.schema.json` の必須項目と制約は以下の通りです。  
スキーマ変更は `T0-2-1` のテストが全件PASS することを確認してから行います。

| フィールド | 型 | 制約 |
|---|---|---|
| `state` | array[string] | minItems: 3、重複禁止 |
| `intent` | string | 必須 |
| `next_actions` | array[string] | minItems: 3 |
| `confidence` | number | 0以上1以下 |
| `trace_id` | string | UUID形式、自動付与 |
| `rollback_plan` | string | 必須 |
| `action_bindings` | array[object] | minItems: 1 |
| `action_bindings[].action` | string | 必須 |
| `action_bindings[].api` | string | 必須 |
| `action_bindings[].dry_run` | boolean | **Phase 0 は true 固定** |

---

## 8. ブランチ戦略

### 基本方針

本リポジトリは **Git Flow** を採用します。  
`main` および `develop` への直接 push は禁止です。すべての変更は Pull Request 経由でマージします。

### ブランチ構成

```
main        本番相当（Cloud Run デプロイ済みの状態）
develop     統合ブランチ（Phase 0 完了時に main へマージ）
feature/    機能実装（develop から分岐）
release/    リリース準備（develop → main への橋渡し）
hotfix/     main の緊急修正
```

### ブランチ命名規則

```
feature/{タスクID}-{説明}
release/phase-{フェーズ番号}
hotfix/{内容}

例：
  feature/T0-2-1-schema
  feature/T0-3-1-reader
  feature/T0-3-4a-audit-log
  release/phase-0
  hotfix/schema-minItems-fix
```

### PR のルール

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
✅ Require a pull request before merging
✅ Require status checks to pass before merging
✅ Do not allow bypassing the above settings
```

**develop**
```
✅ Require a pull request before merging
✅ Do not allow bypassing the above settings
```

### タスクとブランチの対応表

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

---

## 9. Docker / デプロイ構成

### 前提

| 項目 | 内容 |
|---|---|
| ベースイメージ | `python:3.12-slim` |
| ローカル検証 | `docker-compose.yml` で `src/` をマウントして起動 |
| 本番デプロイ | Cloud Run（`cloudbuild.yaml` でビルド → push → deploy） |
| ポート | `8080`（Cloud Run のデフォルト） |
| 環境変数 | `DEMO_URL`（E2Eテストの接続先）、`GOOGLE_CLOUD_PROJECT`（Vertex AI） |

### ファイル配置

```
Dockerfile
docker-compose.yml
cloudbuild.yaml
.dockerignore
```

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY conftest.py .

ENV PORT=8080
ENV PYTHONPATH=/app/src

CMD ["uvicorn", "services.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### docker-compose.yml（ローカル検証用）

```yaml
services:
  app:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./src:/app/src
    environment:
      - PYTHONPATH=/app/src
      - GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}
    command: >
      uvicorn services.api.main:app
      --host 0.0.0.0
      --port 8080
      --reload
```

### cloudbuild.yaml（Cloud Run デプロイ用）

```yaml
steps:
  - name: "gcr.io/cloud-builders/docker"
    args: [build, -t, "gcr.io/$PROJECT_ID/subjective-agent:$COMMIT_SHA", .]

  - name: "gcr.io/cloud-builders/docker"
    args: [push, "gcr.io/$PROJECT_ID/subjective-agent:$COMMIT_SHA"]

  - name: "gcr.io/google.com/cloudsdktool/cloud-sdk"
    entrypoint: gcloud
    args:
      - run
      - deploy
      - subjective-agent
      - --image=gcr.io/$PROJECT_ID/subjective-agent:$COMMIT_SHA
      - --region=asia-northeast1
      - --platform=managed
      - --allow-unauthenticated
      - --port=8080
      - --set-env-vars=GOOGLE_CLOUD_PROJECT=$PROJECT_ID

images:
  - "gcr.io/$PROJECT_ID/subjective-agent:$COMMIT_SHA"
```

> **Note**  
> Phase 0 では `--allow-unauthenticated` を使用します。  
> Phase 1 以降で認証（Cloud IAP等）を追加する際は `cloudbuild.yaml` を更新します。

---

## 10. テスト・エビデンス運用ルール

### 実行方法

```bash
# 全テスト一括実行
pytest

# タスク単位で実行してエビデンス保存
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

### ルール

- タスク完了の定義は **pytest が全件PASS** かつ **`test/evidence/` にエビデンスが保存されている** こと
- `test/evidence/` の `.txt` ファイルはコミット対象とする（証跡として残す）
- テストを削除・スキップして PASS させることは **禁止**

---

## 11. AI（Codex等）への指示

AIが本リポジトリで作業する際は以下を遵守します。

1. **タスク定義に従う**：`task/task-breakdown-v2.md` に記載された実装内容・完了条件を厳守する
2. **スコープを超えない**：Phase 0 に存在しないファイル・ディレクトリを新設しない
3. **パスを変更しない**：セクション3の構造は変更禁止
4. **dry_run を外さない**：`action_bindings` の `dry_run` を `false` にしない
5. **テストを先に確認する**：実装前に対応するテストコードを読み、完了条件を把握する
6. **エビデンスを保存する**：タスク完了時に必ず `test/evidence/` へ出力する
7. **Audit Log を省略しない**：成功・失敗いずれのパスでも `audit_store.save()` を呼び出す
8. **ブランチルールを守る**：`main`・`develop` への直接 push 禁止。必ず `feature/` ブランチを切って PR を出す
9. **Pythonコメント規約を守る**：Pythonファイル先頭に「概要」「入出力」「制約」「Note」を含む日本語docstringを記述する（例: `入出力: A -> B。`）。関数/メソッドでは必要に応じて `Args / Returns / Raises / Note` を明示し、分岐意図が読み取りづらい処理には1〜2行の補助コメントを追加する

---

## 12. Phase 0 完了チェックリスト

Phase 0 完了の判定は以下が **すべて満たされている** こととします。

- [ ] `test/evidence/T0-2-1_test_result.txt` ― 全件PASS
- [ ] `test/evidence/T0-3-1_test_result.txt` ― 全件PASS
- [ ] `test/evidence/T0-3-2_test_result.txt` ― 全件PASS
- [ ] `test/evidence/T0-3-3_test_result.txt` ― 全件PASS
- [ ] `test/evidence/T0-3-4_test_result.txt` ― 全件PASS
- [ ] `test/evidence/T0-3-4a_test_result.txt` ― 全件PASS
- [ ] `test/evidence/T0-4-1_test_result.txt` ― 全件PASS
- [ ] `test/evidence/T0-5-1_test_result.txt` ― 全件PASS
- [ ] `test/evidence/T0-5-2_test_result.txt` ― 安定率 8/10 以上
- [ ] `action_bindings` の `dry_run` が全件 `true` であることをE2Eで確認済み
- [ ] Audit Log が成功・失敗いずれのパスでも保存されることを確認済み
- [ ] `release/phase-0` ブランチから PR を作成し、`main` へマージ済み
- [ ] `git tag phase-0` を打ち、リモートへ push 済み

上記完了後、Phase 1（業務接続）へ進む。
