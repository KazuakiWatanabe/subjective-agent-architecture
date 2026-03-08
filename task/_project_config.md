# ファイル構成（1タスク1ファイル）

```
docs/tasks/
  _project_config.md          ← 【人間専用】タスクファイル生成・更新時のマスター定義
  P0B-1_churn_mapper.md
  P0B-2_churn_demo_schema.md
  P0B-3_primitives_registry.md
  P0B-4_kpi_schema.md
  P1-1_business_primitives.md
  P1-2_mock_adapters.md
  P1-3_plan_apply_flow.md
  P1-4_execution_audit.md
  P1-5_rollback_manager.md
  P2-1_state_churn_table.md
  P2-2_intervention_selector.md
  P2-3_kpi_confirmed.md
  P2-4_meta_store.md
  P2-5_approval_gate.md
  P3-1_policy_engine.md
  P3-2_approval_flow_doc.md
  P3-3_rollback_playbook_doc.md
  P4-1_adapter_interface.md
  P4-2_saas_backlog_doc.md
  P4-3_second_integration_doc.md
  P5-1_whitepaper_doc.md
  P5-2_business_mapping_doc.md
  P5-3_presentation_doc.md
```

---

> ## ⚠️ このファイルの位置づけ
>
> **`_project_config.md` は人間（プロジェクト管理者）専用のマスター定義です。**
>
> - AIエージェント（Codex / Claude Code）に直接渡すことは想定していません。
> - 各タスクファイルはこのファイルを元に生成・更新され、**単体で自己完結**するよう設計されています。
> - AIへの投入はタスクファイル単体で行ってください。
>
> ```
> 【タスクファイル生成・更新のワークフロー】
>
>   このファイル（マスター定義）を参照
>         ↓
>   タスクファイルを生成 / 更新（必要な制約・規約をすべて転記）
>         ↓
>   タスクファイル単体を AI に投入
> ```

---

# ===== FILE: _project_config.md =====
# プロジェクト共通設定（マスター定義）

```yaml
project: subjective-agent-architecture
domain: churn-prevention
roadmap: docs/roadmap_churn_whitepaper_v1.md

language: Python
test_framework: pytest
mock_library: unittest.mock / pytest-mock
coverage_tool: pytest-cov
coverage_threshold: 80
evidence_dir: test/evidence/

core_principle: "state をきれいに出すことではなく、state で再来店率を動かせることを証明する"
dry_run_default: true
```

## ドキュメント優先順位（タスクファイル生成時に転記すること）

タスクファイルに以下の優先順位を必ず明記すること。

```
1. AGENTS.md           ← 最上位ルール。他すべてに優先する
2. 各タスクファイル     ← 本ファイル群
3. CLAUDE.md           ← Claude Code 向け実装ガイド
```

AGENTS.md と各タスクファイルが矛盾する場合は **AGENTS.md を優先**すること。

## 作業開始前の必須読み込み順序（タスクファイルに転記すること）

新しいセッションを開始したら、必ず以下の順で読み込むこと。

```
1. AGENTS.md
2. 該当タスクファイル（例: docs/tasks/P0B-1_churn_mapper.md）
3. CLAUDE.md
```

> **注意**: `_project_config.md` はこのリストに含めないこと。
> タスクファイルは自己完結しており、AI が `_project_config.md` を別途参照する必要はない。

## ⛔ 暴走防止ルール（タスクファイルに転記すること）

```
1. 1回の実行で扱うタスクは必ず1つだけ。
   完了しても次のタスクファイルに自動で進まないこと。

2. target_files に記載されていないファイルは読むことはできるが、変更禁止。
   変更が必要と判断した場合は、作業を止めてその理由を報告すること。

3. 以下のコマンドは実行禁止（Claude Code 適用）:
   - git push（PR経由のみ許可）
   - git commit -m 以外の git commit オプション
   - main / develop への直接 push（Git Flow 厳守）
   - rm -rf を含む削除コマンド
   - pip install / poetry add などの依存追加（requirements.txt 変更も禁止）
   - タスクスコープ外のファイルへの書き込み

4. テストを通すために実装を大幅に書き換えることは禁止。
   既存コードが大きく変わると判断した時点で作業を止めて報告すること。

5. テストを削除・スキップして PASS させることは禁止（エビデンス改ざんに相当）。
```

## 実行環境別の動作指定（タスクファイルに転記すること）

```yaml
codex:
  execution_style: batch
  interaction: none
  file_write: snapshot_only
  checkpoint: done_criteria

claude_code:
  execution_style: interactive
  interaction: allowed           # 不明点は作業前に質問すること
  file_write: realtime
  checkpoint: before_each_write  # ファイル変更前に対象ファイルを報告すること
  confirm_before_start: true     # 実行前に「対象ファイル」「実施内容」を要約して確認を取ること
```

## Git Flow ルール（タスクファイルに転記すること）

```
【ブランチ方針】
- main / develop への直接 push は禁止
- すべての変更は feature/ ブランチ → Pull Request 経由でマージする

【ブランチ命名規則】
  feature/{タスクID}-{説明}
  例: feature/P0B-1-churn-mapper
      feature/P1-3-plan-apply-flow
      feature/P3-1-policy-engine

【通常フロー（feature → develop）】
  git checkout develop
  git pull origin develop
  git checkout -b feature/{タスクID}-{説明}
  # 実装 → テスト → エビデンス保存
  git add {実装ファイル} test/evidence/{task_id}_test_result.txt
  git commit -m "{タスクID}: {実装内容の要約}"
  git push origin feature/{タスクID}-{説明}
  # GitHub で PR を作成（base: develop）→ レビュー → マージ

【コミットメッセージ規則】
  {タスクID}: {実装内容の要約}
  例: P0B-1: ChurnStateMapper実装 - 7語彙マッピング・未知語保持対応
      P1-3: Planner/Applier実装 - validate-plan-apply最小フロー

【PR のルール】
  タイトル  : {タスクID}: {内容}
  base      : develop（hotfix のみ main）
  説明      : ac_ids の完了条件を箇条書きで転記する
  エビデンス: test/evidence/{task_id}_test_result.txt を含めること
  テスト    : PR 時点で全件 PASS していること
```

## Python コーディング規約（タスクファイルに転記すること）

```
【Pythonファイル先頭に必須の日本語 docstring】
  以下の4項目を含むモジュール docstring を必ず記述すること:
  - 概要
  - 入出力
  - 制約
  - Note
```

### docstring 記述例

タスクファイルにこのまま転記し、AI への実装指示として使用すること。

```python
"""
概要:
    ChurnStateMapper は顧客行動ログを受け取り、
    チャーンリスク語彙（7種）にマッピングするモジュール。

入出力:
    入力: CustomerEvent（dataclass） - イベント種別・タイムスタンプを含む
    出力: ChurnState（Enum） - 7語彙のいずれか、または UNKNOWN

制約:
    - 未知のイベント種別は例外を送出せず UNKNOWN として返す
    - dry_run=True の場合、外部 API 呼び出しは行わない

Note:
    語彙マッピングの定義は docs/churn_vocabulary.md を参照。
    Phase 1 以降で ML モデルへの差し替えを想定した設計にすること。
"""
```

```python
def map_event(self, event: CustomerEvent) -> ChurnState:
    """
    顧客イベントをチャーン語彙にマッピングする。

    Args:
        event (CustomerEvent): マッピング対象の顧客イベント

    Returns:
        ChurnState: マッピング結果。未知語の場合は UNKNOWN を返す

    Raises:
        なし（未知語は UNKNOWN として吸収する）

    Note:
        UNKNOWN を返した場合、呼び出し元でログ記録を行うこと。
    """
```

## 絶対に守るべき実装制約（タスクファイルに転記すること）

```
- action_bindings の dry_run を false にしない（Phase 0 では true 固定）
- audit_store.save() の呼び出しを省略しない（成功・失敗いずれでも必須）
- ValidationResult(ok=False) を受け取った Generator は GeneratorError を raise する
- MaxRetryError 発生時も audit_store.save(status="failed") を呼び出す
- src/ 以外に実装コードを置かない（AGENTS.md §3 パス構造変更禁止）
- Phase 1 以降の機能（DB永続化・本番API等）を先行実装しない
```

## モック方針（タスクファイルに転記すること）

```yaml
mock_policy:
  external_api: モック化（呼び出し引数・回数を検証）
  repository_layer: インメモリ偽実装（MetaStore / AuditStore）
  time_random: 固定値に差し替え
  same_service_class: 原則モックしない（統合バグを拾うため）
```

## 自己検証ステップ（タスクファイルに転記すること）

```
Step 1: 全テストが PASS することを確認
Step 2: 核となるロジックを意図的に壊し FAIL を確認
Step 3: 元に戻して再 PASS を確認
Step 4: Step 2 で FAIL しなかったテストは検証内容を見直す
```

## 禁止事項（タスクファイルに転記すること）

```
- テストのためだけに実装フラグを追加する
- assert True など常に通るアサーション
- テスト間で状態を共有する
- 実装と同時にテストを書いて一発グリーンにする
- 全ケースを1テストに詰め込む
- 全外部依存を一律モック化する
- AC ID のないテストにコメントを捏造する
- スコープ外ファイルのリファクタリング
- テストを削除・スキップして PASS させる
```

## 完了条件（タスクファイルに転記すること）

```
- 全テストがグリーンであること
- ac_ids 全件に対応するテストが存在すること
- 自己検証 Step 1〜4 を完了していること
- 各テストに AC ID コメントが記載されていること
- target_files 以外のコードを変更していないこと
- test/evidence/{task_id}_test_result.txt にエビデンスが保存されていること
- 追加・変更した仕様が README または docs に反映されていること
- feature/ ブランチが作成されており、main / develop への直接 push をしていないこと
- Pythonファイルに所定の日本語 docstring が記載されていること
- 【次のタスクには進んでいないこと】
```
