# AGENTS.md
Subjective Agent Architecture ― 最上位ルール定義書（日本語）

本ドキュメントは、本リポジトリに関わる **すべてのAI（Codex等）と人間**が遵守すべき最上位ルールです。  
README や設計資料よりも **AGENTS.md を優先**します。

本プロジェクトは `task/task-breakdown-v2.md` および `docs/roadmap_churn_whitepaper_v1.md` に基づいて実装します。

> **現在の実装フェーズ**  
> Phase 0 は完了済みです。現在は **Phase 0B（デモ再編集）〜 Phase 1（業務接続）** の移行期にあります。  
> ロードマップの詳細は `docs/roadmap_churn_whitepaper_v1.md` を参照してください。

---

## 1. プロジェクトの目的

本プロジェクトは、自然文（社内で刺さる現場の言葉）から

- **state / intent / next_actions**
- **rollback_plan（安全性）**
- **action_bindings（業務接続の足場）**
- **監査ログ（説明責任）**

を備えた **決定論的なJSON** を生成し、**チャーン防止施策との業務接続・KPI改善** を証明することを最終目標とします。

### 現在の目標（Phase 0B）

- state 語彙をチャーン文脈（来店頻度低下 / 予算逼迫 / 限定感志向 等）へ再調整する
- Trait / State / Meta の3層を最低限表現する
- next_actions を業務原子（Business Primitives）に寄せる
- KPI を仮定義する（再来店率 / 30日継続率 / 施策反応率 / 誤配信率）

### 次の目標（Phase 1）

- Business Primitives（`segment_customers` / `send_line_message` / `create_followup_task` 等）を定義する
- Mock Adapter を実装し、Validate → Plan → Apply の最小フローを作る
- dry_run モードと rollback 最小形を持つ

---

## 2. スコープ制約（必須）

- 外部APIの本番実行（配信や更新など）は **Phase 1 完了まで禁止**（`dry_run: true` のみ）
- UIやインフラは **必要最低限**（業務接続の証明が目的）
- 現フェーズのスコープ外となる機能（Phase 2 以降の C層運用・Meta 学習ループ等）は **先行実装しない**

> **Note**  
> Phase 1（実業務接続）以降の詳細設計は `docs/roadmap_churn_whitepaper_v1.md` §6 を参照してください。

---

## 3. リポジトリ構造（前提）

本リポジトリは以下の構造を前提とします（**変更禁止**）。

```
subjective-agent-architecture/
  docs/
    whitepaper.md                        # アーキテクチャ設計書
    roadmap_churn_whitepaper_v1.md       # 現行ロードマップ（チャーン防止特化）
  task/
    task-breakdown-v2.md                 # タスク定義
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
    evidence/                            # pytest -v の出力結果（自動生成）
  src/
    contracts/
      state_intent.schema.json           # 出力スキーマ定義
      presets.json                       # デモ用プリセット入力
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
  conftest.py
  pytest.ini
  AGENTS.md                              # 本ファイル（最上位ルール）
  CLAUDE.md                              # Claude Code 向け実装ガイド
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

> **Phase 1 以降**  
> Business Primitives との接続レイヤー（Mock Adapter）が追加されます。  
> 詳細は `docs/roadmap_churn_whitepaper_v1.md` §6 Phase 1 を参照してください。

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
スキーマ変更はテストが全件PASS することを確認してから行います。

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
| `action_bindings[].dry_run` | boolean | **Phase 1 完了まで true 固定** |

---

## 8. ブランチ戦略

### 基本方針

本リポジトリは **Git Flow** を採用します。  
`main` および `develop` への直接 push は禁止です。すべての変更は Pull Request 経由でマージします。

### ブランチ構成

```
main        本番相当（Cloud Run デプロイ済みの状態）
develop     統合ブランチ
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
  feature/P0B-churn-vocab          # Phase 0B: state語彙のチャーン文脈化
  feature/P0B-kpi-hypothesis       # Phase 0B: KPI仮定義
  feature/P1-primitives-spec       # Phase 1: Business Primitives定義
  feature/P1-mock-adapter          # Phase 1: Mock Adapter実装
  release/phase-1
  hotfix/schema-minItems-fix
```

### PR のルール

| 項目 | ルール |
|---|---|
| タイトル | `{フェーズ-タスク}: {内容}` の形式 |
| base ブランチ | feature → `develop`、release/hotfix → `main` |
| 説明 | 完了条件を箇条書きで転記する |
| エビデンス | `test/evidence/` に対応する結果ファイルが含まれていること |
| テスト | PR 時点で全件 PASS していること |
| セキュリティ | §11 のコードレビューチェックリストを確認済みであること |
| レビュー | セルフマージ可（1名運用を前提） |

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

---

## 10. テスト・エビデンス運用ルール

### 実行方法

```bash
# 全テスト一括実行
pytest

# モジュール単位で実行してエビデンス保存
pytest test/contracts/ -v > test/evidence/contracts_test_result.txt
pytest test/agents/    -v > test/evidence/agents_test_result.txt
pytest test/integration/ -v > test/evidence/integration_test_result.txt
```

### ルール

- タスク完了の定義は **pytest が全件PASS** かつ **`test/evidence/` にエビデンスが保存されている** こと
- `test/evidence/` の `.txt` ファイルはコミット対象とする（証跡として残す）
- テストを削除・スキップして PASS させることは **禁止**

---

## 11. AI（Codex等）への指示

AIが本リポジトリで作業する際は以下を遵守します。

1. **ロードマップに従う**：`docs/roadmap_churn_whitepaper_v1.md` の現フェーズ（Phase 0B / Phase 1）に記載された実装内容・完了条件を厳守する
2. **スコープを超えない**：現フェーズに存在しない機能（Phase 2 以降の学習ループ等）を先行実装しない
3. **パスを変更しない**：§3 の構造は変更禁止
4. **dry_run を外さない**：`action_bindings` の `dry_run` を `false` にしない（Phase 1 完了まで）
5. **テストを先に確認する**：実装前に対応するテストコードを読み、完了条件を把握する
6. **エビデンスを保存する**：タスク完了時に必ず `test/evidence/` へ出力する
7. **Audit Log を省略しない**：成功・失敗いずれのパスでも `audit_store.save()` を呼び出す
8. **ブランチルールを守る**：`main`・`develop` への直接 push 禁止。必ず `feature/` ブランチを切って PR を出す
9. **Pythonコメント規約を守る**：Pythonファイル先頭に「概要」「入出力」「制約」「Note」を含む日本語docstringを記述する。関数/メソッドでは必要に応じて `Args / Returns / Raises / Note` を明示し、分岐意図が読み取りづらい処理には1〜2行の補助コメントを追加する
10. **既存コードのimportを無条件に踏襲しない**：既存ファイルで使われているパッケージであっても、新しいファイルで `import` する前に §12 のセキュリティチェックを実施する。`requirements.txt` に記載のないパッケージは使用禁止

---

## 12. セキュリティルール（サプライチェーン攻撃対策）

> **背景**  
> AIは「既存コードで使われているパッケージ」を既知・安全なものとして扱い、  
> 悪意あるコードをそのまま新しいファイルへ踏襲する場合があります（攻撃成功率100%の事例あり）。  
> CLAUDE.md への直接的なバックドア指示は防がれますが、既存コードのパターンは精査されません。  
> このセクションはその盲点を補うための多重防御として機能します。

### AI・人間の双方が遵守するルール

| ルール | 詳細 |
|---|---|
| **既存importの盲信禁止** | 既存コードに含まれる `import` / `from ... import` であっても、初めて別ファイルで使う際は下記チェックを必ず実施する |
| **環境変数の外部送信禁止** | `os.environ` / `os.getenv` の値を外部URLへ送信するコードを一切書かない |
| **許可リスト外パッケージの使用禁止** | `requirements.txt` に記載のないパッケージを追加する場合は、PyPI公式ページ・ソースコードを確認してからのみ追加可とする |
| **未知の外部エンドポイント禁止** | コード中に現れる外部URLはすべて目視確認する。`internal-monitoring` 等のそれらしい名称であっても例外なし |
| **auto-acceptモードの使用禁止** | Claude Codeをauto-acceptで運用しない。生成コードは必ず確認してから適用する |

### セキュリティチェック手順（パッケージ追加・変更時）

```bash
pip install pip-audit
pip-audit

# スキャン結果をエビデンスとして保存
pip-audit > test/evidence/security_audit.txt
```

確認ポイント（新規パッケージのソースコードを目視）：

- `httpx` / `requests` / `urllib` 等による外部通信
- `os.environ` / `os.getenv` の参照と送信
- `subprocess` / `eval` / `exec` の使用

### コードレビューチェックリスト（PR時）

- [ ] 新規 `import` 文はすべて `requirements.txt` 記載のパッケージか
- [ ] 環境変数（`os.environ` / `os.getenv`）を外部へ送信していないか
- [ ] 外部URLへのHTTPリクエストが意図しない箇所に存在しないか
- [ ] 既存パッケージのパターンを踏襲する際に、そのパッケージが安全であることを確認したか
