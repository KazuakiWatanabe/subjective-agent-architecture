# ファイル構成（1タスク1ファイル）

```
docs/tasks/
  _project_config.md          ← 全タスク共通設定（必ず先に読むこと）
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
---

# ===== FILE: _project_config.md =====
# プロジェクト共通設定

> **Codex / Claude Code 共通**。全タスクファイルはこの設定を継承する。
>
> **ドキュメント優先順位（最重要）**
> ```
> 1. AGENTS.md           ← 最上位ルール。他すべてに優先する
> 2. 各タスクファイル     ← 本ファイル群
> 3. CLAUDE.md           ← Claude Code 向け実装ガイド
> ```
> AGENTS.md と本ファイルが矛盾する場合は **AGENTS.md を優先**すること。

## 作業開始前の必須読み込み順序

新しいセッションを開始したら、必ず以下の順で読み込むこと。

```
1. AGENTS.md
2. 該当タスクファイル（例: docs/tasks/P0B-1_churn_mapper.md）
3. CLAUDE.md
```

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

## ⛔ 暴走防止ルール（Codex / Claude Code 共通・最優先）

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

## 実行環境別の動作指定

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

## Git Flow ルール（AGENTS.md §8 準拠）

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

## Python コーディング規約（AGENTS.md §11 / CLAUDE.md §6 準拠）

```
【Pythonファイル先頭に必須の日本語 docstring】
  以下の4項目を含むモジュール docstring を必ず記述すること:
  - 概要
  - 入出力（例: 入出力: payload -> result。）
  - 制約
  - Note

【関数・メソッドの docstring】
  必要に応じて Args / Returns / Raises / Note を記述すること

【補助コメント】
  条件分岐や補完ロジックなど意図が読み取りづらい処理には
  1〜2行の補助コメントを追加すること
```

## 絶対に守るべき実装制約（AGENTS.md §11 準拠）

```
- action_bindings の dry_run を false にしない（Phase 0 では true 固定）
- audit_store.save() の呼び出しを省略しない（成功・失敗いずれでも必須）
- ValidationResult(ok=False) を受け取った Generator は GeneratorError を raise する
- MaxRetryError 発生時も audit_store.save(status="failed") を呼び出す
- src/ 以外に実装コードを置かない（AGENTS.md §3 パス構造変更禁止）
- Phase 1 以降の機能（DB永続化・本番API等）を先行実装しない
```

## モック方針

```yaml
mock_policy:
  external_api: モック化（呼び出し引数・回数を検証）
  repository_layer: インメモリ偽実装（MetaStore / AuditStore）
  time_random: 固定値に差し替え
  same_service_class: 原則モックしない（統合バグを拾うため）
```

## 自己検証ステップ（全タスク共通）

```
Step 1: 全テストが PASS することを確認
Step 2: 核となるロジックを意図的に壊し FAIL を確認
Step 3: 元に戻して再 PASS を確認
Step 4: Step 2 で FAIL しなかったテストは検証内容を見直す
```

## 禁止事項（テスト品質）

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

## 完了条件（全タスク共通）

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
---
---

# ===== FILE: P1-3_plan_apply_flow.md =====
# P1-3｜Validate → Plan → Apply の最小フロー実装

**ロードマップ参照:** Phase 1 — Validate → Plan → Apply の最小フローを作る（ロードマップの核心）  
**目的:** subjective output → primitive決定 → validate → apply → audit の1本道を通す

## Section 0 - タスク固有設定

```yaml
target_files:
  - src/services/execution/planner.py
  - src/services/execution/applier.py
  - test/execution/test_plan_apply_flow.py   # 新規作成
target_functions:
  - Planner.build
  - Applier.apply
test_scope:
  include: "plan生成 / dry_run apply / 空plan / 未知primitive / validate失敗時の挙動"
  exclude: "並行性・パフォーマンス"
source_spec: docs/roadmap_churn_whitepaper_v1.md#phase-1
ac_ids:
  - "P1-3-AC-01: Planner は recommended_primitives から実行可能な steps を生成する"
  - "P1-3-AC-02: Applier は dry_run plan を completed または dry_run_completed で完了する"
  - "P1-3-AC-03: steps が空の plan は no_steps/skipped/error を返す"
  - "P1-3-AC-04: 未知 primitive を含む step は manual_review_required フラグが立つ"
  - "P1-3-AC-05: validate 失敗の step は apply されない"
```

## Claude Code 実行手順

```
【開始前】Planner と Applier の2ファイル作成についてユーザーに確認を取ること。
【依存確認】P1-2 の Mock Adapter が存在することを確認してから開始すること。
【実行順序】テスト作成 → RED確認 → planner.py / applier.py 実装 → GREEN確認 → 自己検証 → エビデンス保存
【完了後】結果サマリーを出力して停止。次のタスクに進まないこと。
```

## Codex 実行手順

```
- P1-2 の Mock Adapter を使用すること
- dry_run をデフォルトとすること
- 対象タスクのみ。次のタスクには進まないこと
```

## テストコード `test/execution/test_plan_apply_flow.py`

```python
import pytest
from services.execution.planner import Planner
from services.execution.applier import Applier


@pytest.fixture
def planner():
    return Planner()


@pytest.fixture
def applier():
    return Applier()


# P1-3-AC-01
def test_planner_generates_steps(planner):
    plan = planner.build({"state": ["来店頻度低下"], "recommended_primitives": ["send_line_message"]})
    assert len(plan["steps"]) >= 1


# P1-3-AC-02
def test_applier_completes_dry_run(applier):
    plan = {"steps": [{"primitive": "send_line_message",
                       "params": {"segment_id": "s1", "message": "hi", "dry_run": True}}]}
    assert applier.apply(plan)["status"] in ["completed", "dry_run_completed"]


# P1-3-AC-03: 空 plan（境界値）
def test_applier_handles_empty_plan(applier):
    assert applier.apply({"steps": []})["status"] in ["no_steps", "skipped", "error"]


# P1-3-AC-04: 未知 primitive フラグ（異常系）
def test_planner_flags_unknown_primitive(planner):
    plan = planner.build({"state": ["来店頻度低下"], "recommended_primitives": ["unknown_primitive"]})
    assert any(s.get("manual_review_required") for s in plan["steps"])


# P1-3-AC-05: validate 失敗の step は apply されない（異常系）
def test_applier_skips_invalid_step(applier):
    plan = {"steps": [{"primitive": "send_line_message",
                       "params": {"message": "hi", "dry_run": True}}]}  # segment_id 欠落
    result = applier.apply(plan)
    assert result.get("skipped_count", 0) >= 1 or result["status"] in ["error", "partial"]
```

## 自己検証ステップ

```
Step 2 で壊す箇所: applier の dry_run チェックを削除する
期待する結果: test_applier_completes_dry_run の dry_run_completed アサーションが FAIL すること
```

## 終了条件

- [ ] 全 5件のテストが PASS
- [ ] 自己検証 Step 1〜4 完了
- [ ] **次のタスク（P1-4）には進んでいないこと**

## エビデンス保存

```bash
pytest test/execution/test_plan_apply_flow.py -v > test/evidence/P1-3_test_result.txt
```
