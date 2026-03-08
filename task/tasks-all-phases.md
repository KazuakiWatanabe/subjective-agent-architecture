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

# ===== FILE: P0B-1_churn_mapper.md =====
# P0B-1｜チャーン向け state 語彙マッピング

**ロードマップ参照:** Phase 0B — state 語彙をチャーン文脈に寄せる  
**目的:** 自然文 state を churn-oriented 語彙に正規化し、後続の施策選択・KPI接続の基盤を作る

## Section 0 - タスク固有設定

```yaml
target_files:
  - src/services/demo/churn_mapper.py
  - test/analytics/test_churn_mapper.py   # 新規作成
target_functions:
  - ChurnStateMapper.map_states
test_scope:
  include: "正常系マッピング / 未知語保持 / 順序安定性 / 空入力 / 既知+未知の混在"
  exclude: "パフォーマンス・並行性"
source_spec: docs/roadmap_churn_whitepaper_v1.md#phase-0b
ac_ids:
  - "P0B-1-AC-01: 既知の自然文 state が churn 語彙（来店頻度低下等）に正規化される"
  - "P0B-1-AC-02: 未知語は破棄されず保持される"
  - "P0B-1-AC-03: 同一入力に対して結果が常に同じ順序で返る（順序安定）"
  - "P0B-1-AC-04: 空リスト入力は空リストを返す"
  - "P0B-1-AC-05: 既知語と未知語が混在する場合、双方が正しく処理される"
```

## Claude Code 実行手順

```
【開始前に必ず実施】
0. AGENTS.md → 本タスクファイル → CLAUDE.md の順で読み込むこと
1. 以下を要約してユーザーに提示し、確認を取ること:
   - 作成するファイル: src/services/demo/churn_mapper.py
   - 実施内容: ChurnStateMapper クラスの新規実装
   - 変更しないファイル: 上記2ファイル以外すべて
2. feature ブランチを切ること（main/develop への直接 push 禁止）:
   git checkout develop && git pull origin develop
   git checkout -b feature/P0B-1-churn-mapper

【実行順序】
Step A. test/analytics/test_churn_mapper.py を作成する（テストファースト）
Step B. pytest を実行して全テストが RED になることを確認する
Step C. src/services/demo/churn_mapper.py を実装する
         ※ファイル先頭に「概要・入出力・制約・Note」を含む日本語 docstring を記述すること
Step D. pytest を実行して全テストが GREEN になることを確認する
Step E. 自己検証（ロジックを壊して FAIL を確認 → 元に戻す）
Step F. エビデンスを保存する
Step G. コミット＆ push:
         git add src/services/demo/churn_mapper.py \
                 test/analytics/test_churn_mapper.py \
                 test/evidence/P0B-1_test_result.txt
         git commit -m "P0B-1: ChurnStateMapper実装 - 7語彙マッピング・未知語保持対応"
         git push origin feature/P0B-1-churn-mapper
         # GitHub で PR を作成（base: develop）

【完了後】
結果サマリーを出力して停止すること。次のタスクには進まないこと。
```

## Codex 実行手順

```
- AGENTS.md のルールを最優先で遵守すること
- pytest ベースでテストを先に書き、RED を確認してから実装すること
- Pythonファイル先頭に「概要・入出力・制約・Note」を含む日本語 docstring を記述すること
- 変更ファイル一覧を最後に出力すること
- 対象タスクのみを実装すること。次のタスクには進まないこと
```

## 実装内容

`src/services/demo/churn_mapper.py` を作成し、既存 state をチャーン文脈の語彙へ正規化する。

対応語彙（最低限）:  
来店頻度低下 / 予算逼迫 / 多忙 / 比較疲れ / 限定感志向 / 価格感度高 / 接触希薄化

## テストコード `test/analytics/test_churn_mapper.py`

```python
import pytest
from services.demo.churn_mapper import ChurnStateMapper


@pytest.fixture
def mapper():
    return ChurnStateMapper()


# P0B-1-AC-01: 既知の自然文 state が churn 語彙に正規化される
def test_maps_known_states_to_churn_terms(mapper):
    result = mapper.map_states(["来店が減っている", "限定に反応", "忙しくて来れない"])
    assert "来店頻度低下" in result
    assert "限定感志向" in result
    assert "多忙" in result


# P0B-1-AC-02: 未知語は破棄されず保持される
def test_unknown_state_is_preserved(mapper):
    result = mapper.map_states(["完全に謎の状態"])
    assert len(result) == 1


# P0B-1-AC-03: 同一入力に対して結果が常に同じ順序で返る
def test_mapping_is_stable(mapper):
    a = mapper.map_states(["来店が減っている", "限定に反応"])
    b = mapper.map_states(["来店が減っている", "限定に反応"])
    assert a == b


# P0B-1-AC-04: 空リスト入力は空リストを返す（境界値）
def test_empty_input_returns_empty(mapper):
    assert mapper.map_states([]) == []


# P0B-1-AC-05: 既知語と未知語が混在する場合、双方が正しく処理される
def test_mixed_known_and_unknown_preserves_both(mapper):
    result = mapper.map_states(["来店が減っている", "謎の状態"])
    assert "来店頻度低下" in result
    assert len(result) == 2
```

## 自己検証ステップ

```
Step 2 で壊す箇所: map_states 内のマッピング辞書から任意のキーを1件削除する
期待する結果: test_maps_known_states_to_churn_terms が FAIL すること
```

## 終了条件

- [ ] 上記 5件のテストが全て PASS
- [ ] 7語彙すべてのマッピングが実装されていること
- [ ] 自己検証 Step 1〜4 完了
- [ ] **次のタスク（P0B-2）には進んでいないこと**

## エビデンス保存

```bash
pytest test/analytics/test_churn_mapper.py -v > test/evidence/P0B-1_test_result.txt
```

---
---

# ===== FILE: P0B-2_churn_demo_schema.md =====
# P0B-2｜Trait / State / Meta の最小表現スキーマ

**ロードマップ参照:** Phase 0B — Trait / State / Meta の3層を最小限表現する  
**目的:** churn デモの出力を JSON Schema で定義し、後続タスクの入力契約を確立する

## Section 0 - タスク固有設定

```yaml
target_files:
  - src/contracts/churn_demo.schema.json
  - test/contracts/test_churn_demo_schema.py   # 新規作成
target_functions:
  - churn_demo JSON Schema
test_scope:
  include: "スキーマ妥当性 / 必須項目 / 正常ペイロード / 必須欠落エラー / confidence 範囲外 / 空配列"
  exclude: "パフォーマンス"
source_spec: docs/roadmap_churn_whitepaper_v1.md#phase-0b
ac_ids:
  - "P0B-2-AC-01: JSON Schema として Draft7 妥当である"
  - "P0B-2-AC-02: 8つの必須フィールドが required に含まれる"
  - "P0B-2-AC-03: 正常ペイロードがバリデーションを通過する"
  - "P0B-2-AC-04: 必須フィールド欠落はバリデーションエラーになる"
  - "P0B-2-AC-05: confidence > 1.0 はバリデーションエラーになる"
  - "P0B-2-AC-06: recommended_primitives が空配列はバリデーションエラーになる"
```

## Claude Code 実行手順

```
【開始前に必ず実施】
作成するファイルと実施内容をユーザーに提示して確認を取ること。

【実行順序】
Step A. test/contracts/test_churn_demo_schema.py を作成（テストファースト）
Step B. pytest → 全テスト RED を確認
Step C. src/contracts/churn_demo.schema.json を作成
Step D. pytest → 全テスト GREEN を確認
Step E. 自己検証（schema の required からフィールドを削除 → FAIL確認 → 元に戻す）
Step F. エビデンス保存

【完了後】結果サマリーを出力して停止。次のタスクに進まないこと。
```

## Codex 実行手順

```
- AGENTS.md のルールを最優先で遵守すること
- テストを先に書き、RED を確認してから schema を作成すること
- Pythonファイル先頭に「概要・入出力・制約・Note」を含む日本語 docstring を記述すること
- 対象タスクのみを実装すること。次のタスクには進まないこと
```

## テストコード `test/contracts/test_churn_demo_schema.py`

```python
import json
import pytest
import jsonschema
from pathlib import Path

SCHEMA_PATH = Path(__file__).parent.parent.parent / "src/contracts/churn_demo.schema.json"
REQUIRED_FIELDS = ["trait", "state", "meta", "intent",
                   "recommended_primitives", "kpi_hypothesis", "confidence", "trace_id"]


@pytest.fixture
def schema():
    return json.loads(SCHEMA_PATH.read_text())


@pytest.fixture
def valid_payload():
    return {
        "trait": ["限定感志向"],
        "state": ["来店頻度低下"],
        "meta": ["前回クーポン反応なし"],
        "intent": "再来店動機付け",
        "recommended_primitives": ["send_line_message"],
        "kpi_hypothesis": ["30日継続率改善"],
        "confidence": 0.8,
        "trace_id": "demo-001"
    }


# P0B-2-AC-01: JSON Schema として Draft7 妥当である
def test_schema_is_valid_draft7(schema):
    jsonschema.Draft7Validator.check_schema(schema)


# P0B-2-AC-02: 全必須フィールドが required に含まれる
@pytest.mark.parametrize("field", REQUIRED_FIELDS)
def test_required_fields_exist(schema, field):
    assert field in schema["required"]


# P0B-2-AC-03: 正常ペイロードがバリデーションを通過する
def test_valid_payload_passes(schema, valid_payload):
    jsonschema.validate(valid_payload, schema)


# P0B-2-AC-04: 必須フィールド欠落はバリデーションエラー（異常系）
def test_missing_trace_id_fails(schema, valid_payload):
    del valid_payload["trace_id"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(valid_payload, schema)


# P0B-2-AC-05: confidence > 1.0 はバリデーションエラー（境界値）
def test_confidence_over_1_fails(schema, valid_payload):
    valid_payload["confidence"] = 1.1
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(valid_payload, schema)


# P0B-2-AC-06: recommended_primitives 空配列はバリデーションエラー（境界値）
def test_empty_primitives_fails(schema, valid_payload):
    valid_payload["recommended_primitives"] = []
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(valid_payload, schema)
```

## 自己検証ステップ

```
Step 2 で壊す箇所: schema の required から "trace_id" を削除する
期待する結果: test_missing_trace_id_fails が FAIL すること
```

## 終了条件

- [ ] 全テストが PASS（parametrize 込みで 11件）
- [ ] 自己検証 Step 1〜4 完了
- [ ] **次のタスク（P0B-3）には進んでいないこと**

## エビデンス保存

```bash
pytest test/contracts/test_churn_demo_schema.py -v > test/evidence/P0B-2_test_result.txt
```

---
---

# ===== FILE: P0B-3_primitives_registry.md =====
# P0B-3｜next_actions を Business Primitive 候補に変換

**ロードマップ参照:** Phase 0B — next_actions を業務原子に寄せる  
**目的:** 自然文アクションを5種の Business Primitive にマッピングし、後続 Planner への橋渡しを作る

## Section 0 - タスク固有設定

```yaml
target_files:
  - src/services/execution/primitives_registry.py
  - test/execution/test_primitives_registry.py   # 新規作成
target_functions:
  - PrimitivesRegistry.resolve
  - PrimitivesRegistry.resolve_by_name
test_scope:
  include: "正常系変換 / 未知アクション処理 / 空入力 / 全 primitive 網羅確認"
  exclude: "パフォーマンス・並行性"
source_spec: docs/roadmap_churn_whitepaper_v1.md#phase-0b
ac_ids:
  - "P0B-3-AC-01: 自然文アクションから対応する primitive 名が返る"
  - "P0B-3-AC-02: 非対応アクションは manual_review_required=True で返る"
  - "P0B-3-AC-03: 空リスト入力は空リストを返す"
  - "P0B-3-AC-04: 複数の未知アクションがすべて manual_review_required=True になる"
  - "P0B-3-AC-05: 5種の primitive がすべて解決可能である"
```

## Claude Code 実行手順

```
【開始前に必ず実施】
作成するファイルと実施内容をユーザーに提示して確認を取ること。

【実行順序】
Step A. test/execution/test_primitives_registry.py を作成（テストファースト）
Step B. pytest → RED 確認
Step C. src/services/execution/primitives_registry.py を実装
Step D. pytest → GREEN 確認
Step E. 自己検証（send_line_messageマッピングを削除 → FAIL確認 → 元に戻す）
Step F. エビデンス保存

【完了後】結果サマリーを出力して停止。次のタスクに進まないこと。
```

## Codex 実行手順

```
- テストを先に書き、RED を確認してから実装すること
- 対象 primitive: segment_customers / send_line_message / reserve_offer / cancel_offer / create_followup_task
- 対象タスクのみを実装すること。次のタスクには進まないこと
```

## テストコード `test/execution/test_primitives_registry.py`

```python
import pytest
from services.execution.primitives_registry import PrimitivesRegistry

PRIMITIVES = [
    "segment_customers", "send_line_message", "reserve_offer",
    "cancel_offer", "create_followup_task",
]


@pytest.fixture
def registry():
    return PrimitivesRegistry()


# P0B-3-AC-01: 自然文アクションから対応する primitive 名が返る
def test_maps_actions_to_primitives(registry):
    result = registry.resolve(["LINEで限定オファーを配信", "フォロータスクを作成"])
    names = [r["primitive"] for r in result]
    assert "send_line_message" in names
    assert "create_followup_task" in names


# P0B-3-AC-02: 非対応アクションは manual_review_required=True で返る
def test_unknown_action_requires_manual_review(registry):
    result = registry.resolve(["スタッフに感覚で判断してもらう"])
    assert result[0]["manual_review_required"] is True


# P0B-3-AC-03: 空リスト入力は空リストを返す（境界値）
def test_empty_input_returns_empty(registry):
    assert registry.resolve([]) == []


# P0B-3-AC-04: 複数の未知アクションがすべて manual_review_required=True になる
def test_multiple_unknown_actions_all_flagged(registry):
    result = registry.resolve(["謎の行動1", "謎の行動2"])
    assert all(r["manual_review_required"] is True for r in result)
    assert len(result) == 2


# P0B-3-AC-05: 5種の primitive がすべて解決可能である
@pytest.mark.parametrize("primitive", PRIMITIVES)
def test_all_primitives_are_resolvable(registry, primitive):
    result = registry.resolve_by_name(primitive)
    assert result is not None
```

## 自己検証ステップ

```
Step 2 で壊す箇所: send_line_message のマッピングキーを削除する
期待する結果: test_maps_actions_to_primitives が FAIL すること
```

## 終了条件

- [ ] 全テストが PASS（parametrize 込みで 9件）
- [ ] 自己検証 Step 1〜4 完了
- [ ] **次のタスク（P0B-4）には進んでいないこと**

## エビデンス保存

```bash
pytest test/execution/test_primitives_registry.py -v > test/evidence/P0B-3_test_result.txt
```

---
---

# ===== FILE: P0B-4_kpi_schema.md =====
# P0B-4｜KPI 仮定義メモの構造化

**ロードマップ参照:** Phase 0B — KPI を仮定義する（確定は Phase 2）

## Section 0 - タスク固有設定

```yaml
target_files:
  - src/contracts/kpi_definition.schema.json
  - docs/specs/kpi_definition.md
  - test/contracts/test_kpi_definition_schema.py   # 新規作成
target_functions:
  - kpi_definition JSON Schema
test_scope:
  include: "スキーマ妥当性 / 正常ペイロード / status 制約 / 必須フィールド欠落 / 5種KPI文書確認"
  exclude: "パフォーマンス"
source_spec: docs/roadmap_churn_whitepaper_v1.md#phase-0b
ac_ids:
  - "P0B-4-AC-01: JSON Schema として Draft7 妥当である"
  - "P0B-4-AC-02: 正常な KPI ペイロードがバリデーションを通過する"
  - "P0B-4-AC-03: status は hypothesis または confirmed のみ許可される"
  - "P0B-4-AC-04: 必須フィールド（name）が欠落するとバリデーションエラーになる"
  - "P0B-4-AC-05: 5種の KPI が kpi_definition.md に記載されている"
```

## Claude Code 実行手順

```
【開始前に必ず実施】
作成・変更するファイルをユーザーに提示して確認を取ること。

【実行順序】
Step A. テストファイルを作成 → RED 確認
Step B. schema.json と kpi_definition.md を作成
Step C. pytest → GREEN 確認
Step D. 自己検証（statusのenumから"hypothesis"を削除 → FAIL確認 → 元に戻す）
Step E. エビデンス保存

【完了後】結果サマリーを出力して停止。次のタスクに進まないこと。
```

## Codex 実行手順

```
- status は hypothesis 固定で作成（Phase 2 で confirmed へ昇格）
- 対象 KPI: 再来店率 / 30日継続率 / 施策反応率 / 誤配信率 / Meta 蓄積速度
- 対象タスクのみを実装すること。次のタスクには進まないこと
```

## テストコード `test/contracts/test_kpi_definition_schema.py`

```python
import json
import pytest
import jsonschema
from pathlib import Path

SCHEMA_PATH = Path(__file__).parent.parent.parent / "src/contracts/kpi_definition.schema.json"
DOC_PATH = Path(__file__).parent.parent.parent / "docs/specs/kpi_definition.md"
KPI_NAMES = ["再来店率", "30日継続率", "施策反応率", "誤配信率", "Meta 蓄積速度"]


@pytest.fixture
def schema():
    return json.loads(SCHEMA_PATH.read_text())


@pytest.fixture
def valid_kpi(schema):
    return {
        "kpis": [{
            "name": "30日継続率",
            "definition": "配信後30日以内に再来店した割合",
            "numerator": "30日以内再来店顧客数",
            "denominator": "対象配信顧客数",
            "frequency": "monthly",
            "owner": "pm",
            "status": "hypothesis"
        }]
    }


# P0B-4-AC-01
def test_kpi_schema_is_valid_draft7(schema):
    jsonschema.Draft7Validator.check_schema(schema)


# P0B-4-AC-02
def test_valid_kpi_payload_passes(schema, valid_kpi):
    jsonschema.validate(valid_kpi, schema)


# P0B-4-AC-03: status は hypothesis/confirmed のみ許可（異常系）
def test_invalid_status_fails(schema, valid_kpi):
    valid_kpi["kpis"][0]["status"] = "draft"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(valid_kpi, schema)


# P0B-4-AC-04: 必須フィールド欠落はエラー（異常系）
def test_missing_name_fails(schema, valid_kpi):
    del valid_kpi["kpis"][0]["name"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(valid_kpi, schema)


# P0B-4-AC-05: 5種の KPI が docs に記載されている
@pytest.mark.parametrize("kpi_name", KPI_NAMES)
def test_kpi_doc_covers_all_kpis(kpi_name):
    text = DOC_PATH.read_text(encoding="utf-8")
    assert kpi_name in text
```

## 自己検証ステップ

```
Step 2 で壊す箇所: schema の status enum から "hypothesis" を削除する
期待する結果: test_valid_kpi_payload_passes が FAIL すること
```

## 終了条件

- [ ] 全テストが PASS（parametrize 込みで 9件）
- [ ] 自己検証 Step 1〜4 完了
- [ ] **次のタスク（P1-1）には進んでいないこと**

## エビデンス保存

```bash
pytest test/contracts/test_kpi_definition_schema.py -v > test/evidence/P0B-4_test_result.txt
```

---
---

# ===== FILE: P1-1_business_primitives.md =====
# P1-1｜Business Primitives 仕様の明文化

**ロードマップ参照:** Phase 1 — Business Primitives を定義する

## Section 0 - タスク固有設定

```yaml
target_files:
  - src/contracts/business_primitives.schema.json
  - docs/specs/business_primitives.md
  - test/contracts/test_business_primitives_schema.py   # 新規作成
target_functions:
  - business_primitives JSON Schema
test_scope:
  include: "スキーマ妥当性 / 必須フィールド6種 / rollback_hint欠落エラー / dry_run_behavior欠落エラー / 5種docs確認"
  exclude: "パフォーマンス"
source_spec: docs/roadmap_churn_whitepaper_v1.md#phase-1
ac_ids:
  - "P1-1-AC-01: JSON Schema として Draft7 妥当である"
  - "P1-1-AC-02: name/input/output/dry_run_behavior/rollback_hint/audit_fields が required"
  - "P1-1-AC-03: rollback_hint 欠落はバリデーションエラー"
  - "P1-1-AC-04: dry_run_behavior 欠落はバリデーションエラー"
  - "P1-1-AC-05: 5種の primitive が docs に記載されている"
```

## Claude Code 実行手順

```
【開始前】作成・変更ファイルをユーザーに提示して確認を取ること。
【実行順序】テスト作成 → RED確認 → schema + docs作成 → GREEN確認 → 自己検証 → エビデンス保存
【完了後】結果サマリーを出力して停止。次のタスクに進まないこと。
```

## Codex 実行手順

```
- 5種: segment_customers / send_line_message / reserve_offer / cancel_offer / create_followup_task
- 対象タスクのみ。次のタスクには進まないこと
```

## テストコード `test/contracts/test_business_primitives_schema.py`

```python
import json
import pytest
import jsonschema
from pathlib import Path

SCHEMA_PATH = Path(__file__).parent.parent.parent / "src/contracts/business_primitives.schema.json"
DOC_PATH = Path(__file__).parent.parent.parent / "docs/specs/business_primitives.md"
PRIMITIVES = ["segment_customers", "send_line_message", "reserve_offer",
              "cancel_offer", "create_followup_task"]
REQUIRED_FIELDS = ["name", "input", "output", "dry_run_behavior", "rollback_hint", "audit_fields"]


@pytest.fixture
def schema():
    return json.loads(SCHEMA_PATH.read_text())


@pytest.fixture
def valid_primitive():
    return {
        "name": "send_line_message",
        "input": {"segment_id": "string", "message": "string"},
        "output": {"execution_id": "string", "status": "string"},
        "dry_run_behavior": "副作用なしでシミュレート",
        "rollback_hint": "送信済みは取消不可。フォローアップで補償",
        "audit_fields": ["execution_id", "timestamp", "dry_run"]
    }


# P1-1-AC-01
def test_schema_is_valid_draft7(schema):
    jsonschema.Draft7Validator.check_schema(schema)


# P1-1-AC-02: 必須フィールドが required に含まれる
@pytest.mark.parametrize("field", REQUIRED_FIELDS)
def test_primitive_required_fields(schema, field):
    assert field in schema["definitions"]["primitive"]["required"]


# P1-1-AC-03: rollback_hint 欠落はエラー（異常系）
def test_missing_rollback_hint_fails(schema, valid_primitive):
    del valid_primitive["rollback_hint"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(valid_primitive, schema["definitions"]["primitive"])


# P1-1-AC-04: dry_run_behavior 欠落はエラー（異常系）
def test_missing_dry_run_behavior_fails(schema, valid_primitive):
    del valid_primitive["dry_run_behavior"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(valid_primitive, schema["definitions"]["primitive"])


# P1-1-AC-05: 5種 primitive が docs に記載されている
@pytest.mark.parametrize("primitive", PRIMITIVES)
def test_all_primitives_documented(primitive):
    assert primitive in DOC_PATH.read_text(encoding="utf-8")
```

## 自己検証ステップ

```
Step 2 で壊す箇所: required から "rollback_hint" を削除する
期待する結果: test_missing_rollback_hint_fails が FAIL すること
```

## 終了条件

- [ ] 全テストが PASS（parametrize 込みで 13件）
- [ ] 自己検証 Step 1〜4 完了
- [ ] **次のタスク（P1-2）には進んでいないこと**

## エビデンス保存

```bash
pytest test/contracts/test_business_primitives_schema.py -v > test/evidence/P1-1_test_result.txt
```

---
---

# ===== FILE: P1-2_mock_adapters.md =====
# P1-2｜Mock Adapter 実装

**ロードマップ参照:** Phase 1 — Mock Adapter を実装する

## Section 0 - タスク固有設定

```yaml
target_files:
  - src/adapters/mock_crm_adapter.py
  - src/adapters/mock_line_adapter.py
  - src/adapters/mock_task_adapter.py
  - test/adapters/test_mock_adapters.py   # 新規作成
target_functions:
  - MockLineAdapter.validate / execute / rollback / audit
test_scope:
  include: "validate正常系 / validate必須欠落エラー / dry_run実行 / rollback / audit記録 / 3Adapter interface確認"
  exclude: "パフォーマンス・並行性"
source_spec: docs/roadmap_churn_whitepaper_v1.md#phase-1
ac_ids:
  - "P1-2-AC-01: validate は正常入力に ok=True を返す"
  - "P1-2-AC-02: validate は必須フィールド欠落に ok=False を返す"
  - "P1-2-AC-03: dry_run=True 実行では execution_id が返り副作用がない"
  - "P1-2-AC-04: rollback は ok=True を返す"
  - "P1-2-AC-05: audit は execution_id に対応する記録を返す"
  - "P1-2-AC-06: 3つの Adapter が全て validate/execute/rollback/audit を持つ"
```

## Claude Code 実行手順

```
【開始前】作成する3ファイルと実施内容をユーザーに提示して確認を取ること。
【実行順序】テスト作成 → RED確認 → 3Adapter実装 → GREEN確認 → 自己検証 → エビデンス保存
【完了後】結果サマリーを出力して停止。次のタスクに進まないこと。
```

## Codex 実行手順

```
- 3ファイルを全て新規作成すること
- dry_run=True の場合、副作用は発生させないこと
- 対象タスクのみ。次のタスクには進まないこと
```

## テストコード `test/adapters/test_mock_adapters.py`

```python
import pytest
from adapters.mock_line_adapter import MockLineAdapter
from adapters.mock_crm_adapter import MockCrmAdapter
from adapters.mock_task_adapter import MockTaskAdapter

ADAPTER_CLASSES = [MockLineAdapter, MockCrmAdapter, MockTaskAdapter]
REQUIRED_METHODS = ["validate", "execute", "rollback", "audit"]


@pytest.fixture
def adapter():
    return MockLineAdapter()


@pytest.fixture
def valid_input():
    return {"segment_id": "seg-001", "message": "hello"}


# P1-2-AC-01
def test_validate_returns_ok(adapter, valid_input):
    assert adapter.validate(valid_input)["ok"] is True


# P1-2-AC-02: 必須欠落は ok=False（異常系）
def test_validate_fails_on_missing_field(adapter):
    assert adapter.validate({"message": "hello"})["ok"] is False


# P1-2-AC-03: dry_run=True で execution_id が返る
def test_execute_dry_run(adapter, valid_input):
    result = adapter.execute("send_line_message", {**valid_input, "dry_run": True})
    assert result["dry_run"] is True
    assert "execution_id" in result


# P1-2-AC-04
def test_rollback_returns_ok(adapter):
    assert adapter.rollback("exec-001")["ok"] is True


# P1-2-AC-05
def test_audit_returns_record(adapter, valid_input):
    result = adapter.execute("send_line_message", {**valid_input, "dry_run": True})
    audit = adapter.audit(result["execution_id"])
    assert audit["execution_id"] == result["execution_id"]


# P1-2-AC-06: 全 Adapter が共通 interface を持つ
@pytest.mark.parametrize("adapter_cls", ADAPTER_CLASSES)
@pytest.mark.parametrize("method", REQUIRED_METHODS)
def test_all_adapters_have_interface(adapter_cls, method):
    assert hasattr(adapter_cls(), method)
```

## 自己検証ステップ

```
Step 2 で壊す箇所: validate から segment_id チェックを削除する
期待する結果: test_validate_fails_on_missing_field が FAIL すること
```

## 終了条件

- [ ] 全テストが PASS（parametrize 込みで 17件）
- [ ] 自己検証 Step 1〜4 完了
- [ ] **次のタスク（P1-3）には進んでいないこと**

## エビデンス保存

```bash
pytest test/adapters/test_mock_adapters.py -v > test/evidence/P1-2_test_result.txt
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

---
---

# ===== FILE: P1-4_execution_audit.md =====
# P1-4｜Audit Log の execution 拡張

**ロードマップ参照:** Phase 1 — Audit Log を保存する

## Section 0 - タスク固有設定

```yaml
target_files:
  - src/services/execution/applier.py   # P1-3 で作成済み。拡張のみ
  - test/execution/test_execution_audit.py   # 新規作成
target_functions:
  - Applier.apply
  - AuditStore.last
test_scope:
  include: "trace_id / selected_primitives / dry_run / timestamp の各記録 / trace_id未指定時"
  exclude: "並行性・パフォーマンス"
source_spec: docs/roadmap_churn_whitepaper_v1.md#phase-1
ac_ids:
  - "P1-4-AC-01: audit に trace_id が記録される"
  - "P1-4-AC-02: audit に selected_primitives が記録される"
  - "P1-4-AC-03: audit に dry_run フラグが記録される"
  - "P1-4-AC-04: audit に timestamp が記録される"
  - "P1-4-AC-05: trace_id 未指定でも audit レコードが作成される"
```

## Claude Code 実行手順

```
【開始前】
- applier.py を変更することをユーザーに提示して確認を取ること
- 変更は AuditStore 書き込み追加のみとすること（既存ロジックの書き換え禁止）

【実行順序】テスト作成 → RED確認 → applier.py に audit 拡張 → GREEN確認 → 自己検証 → エビデンス保存
【完了後】結果サマリーを出力して停止。次のタスクに進まないこと。
```

## Codex 実行手順

```
- P1-3 の applier.py に audit 機能を追加すること
- AuditStore はインメモリ実装でよい
- 対象タスクのみ。次のタスクには進まないこと
```

## テストコード `test/execution/test_execution_audit.py`

```python
import pytest
from services.execution.applier import Applier


@pytest.fixture
def applier():
    return Applier()


@pytest.fixture
def dry_run_plan():
    return {
        "trace_id": "trace-001",
        "steps": [{"primitive": "send_line_message",
                   "params": {"segment_id": "s1", "message": "hi", "dry_run": True}}]
    }


# P1-4-AC-01
def test_audit_contains_trace_id(applier, dry_run_plan):
    applier.apply(dry_run_plan)
    assert applier.audit_store.last()["trace_id"] == "trace-001"


# P1-4-AC-02
def test_audit_contains_selected_primitives(applier, dry_run_plan):
    applier.apply(dry_run_plan)
    assert "send_line_message" in applier.audit_store.last()["selected_primitives"]


# P1-4-AC-03
def test_audit_contains_dry_run_flag(applier, dry_run_plan):
    applier.apply(dry_run_plan)
    assert applier.audit_store.last()["dry_run"] is True


# P1-4-AC-04
def test_audit_contains_timestamp(applier, dry_run_plan):
    applier.apply(dry_run_plan)
    audit = applier.audit_store.last()
    assert "timestamp" in audit and audit["timestamp"] is not None


# P1-4-AC-05: trace_id 未指定でも audit が作成される（境界値）
def test_audit_created_without_trace_id(applier):
    plan = {"steps": [{"primitive": "send_line_message",
                       "params": {"segment_id": "s1", "message": "hi", "dry_run": True}}]}
    applier.apply(plan)
    assert applier.audit_store.last() is not None
```

## 自己検証ステップ

```
Step 2 で壊す箇所: audit_store.save() の trace_id 書き込みをコメントアウト
期待する結果: test_audit_contains_trace_id が FAIL すること
```

## 終了条件

- [ ] 全 5件のテストが PASS
- [ ] 自己検証 Step 1〜4 完了
- [ ] **次のタスク（P1-5）には進んでいないこと**

## エビデンス保存

```bash
pytest test/execution/test_execution_audit.py -v > test/evidence/P1-4_test_result.txt
```

---
---

# ===== FILE: P1-5_rollback_manager.md =====
# P1-5｜Rollback / compensating action の最小実装

**ロードマップ参照:** Phase 1 — rollback / compensating action の最小形を作る

## Section 0 - タスク固有設定

```yaml
target_files:
  - src/services/execution/rollback_manager.py
  - test/execution/test_rollback_manager.py   # 新規作成
target_functions:
  - RollbackManager.rollback
test_scope:
  include: "正常rollback / 未知adapter / dry_run記録 / 空execution_id"
  exclude: "並行性・パフォーマンス"
source_spec: docs/roadmap_churn_whitepaper_v1.md#phase-1
ac_ids:
  - "P1-5-AC-01: 既知 adapter の rollback は status フィールドを返す"
  - "P1-5-AC-02: 未知 adapter の rollback は manual_intervention_required=True"
  - "P1-5-AC-03: dry_run 実行に対する rollback でも記録が残る"
  - "P1-5-AC-04: execution_id が空の場合は error または manual_intervention_required=True"
```

## Claude Code 実行手順

```
【開始前】rollback_manager.py 新規作成についてユーザーに確認を取ること。
【実行順序】テスト作成 → RED確認 → 実装 → GREEN確認 → 自己検証 → エビデンス保存
【完了後】結果サマリーを出力して停止。次のタスクに進まないこと。
```

## テストコード `test/execution/test_rollback_manager.py`

```python
import pytest
from services.execution.rollback_manager import RollbackManager


@pytest.fixture
def manager():
    return RollbackManager()


# P1-5-AC-01
def test_rollback_returns_status_for_known_adapter(manager):
    result = manager.rollback({"execution_id": "exec-001", "adapter": "mock_line"})
    assert "status" in result


# P1-5-AC-02: 未知 adapter（異常系）
def test_unknown_adapter_requires_manual_intervention(manager):
    result = manager.rollback({"execution_id": "exec-001", "adapter": "unknown_adapter"})
    assert result["manual_intervention_required"] is True


# P1-5-AC-03: dry_run に対しても記録が残る
def test_rollback_record_for_dry_run(manager):
    result = manager.rollback({"execution_id": "exec-dry-001", "adapter": "mock_line", "dry_run": True})
    assert "status" in result


# P1-5-AC-04: 空 execution_id（境界値）
def test_empty_execution_id_handled_safely(manager):
    result = manager.rollback({"execution_id": "", "adapter": "mock_line"})
    assert result.get("status") == "error" or result.get("manual_intervention_required") is True
```

## 自己検証ステップ

```
Step 2 で壊す箇所: unknown adapter チェックを削除して常に status を返す
期待する結果: test_unknown_adapter_requires_manual_intervention が FAIL すること
```

## 終了条件

- [ ] 全 4件のテストが PASS
- [ ] 自己検証 Step 1〜4 完了
- [ ] **次のタスク（P2-1）には進んでいないこと**

## エビデンス保存

```bash
pytest test/execution/test_rollback_manager.py -v > test/evidence/P1-5_test_result.txt
```

---
---

# ===== FILE: P2-1_state_churn_table.md =====
# P2-1｜state-to-churn hypothesis table の生成

**ロードマップ参照:** Phase 2 — state とチャーン予兆の相関を見る

## Section 0 - タスク固有設定

```yaml
target_files:
  - docs/hypotheses/state_to_churn_table.md
  - test/analytics/test_state_churn_hypothesis_table.py   # 新規作成
target_functions:
  - state_to_churn_table ドキュメント
test_scope:
  include: "ファイル存在 / 全7 state 網羅 / 必須4カラム存在"
  exclude: "パフォーマンス"
source_spec: docs/roadmap_churn_whitepaper_v1.md#phase-2
ac_ids:
  - "P2-1-AC-01: state_to_churn_table.md が存在する"
  - "P2-1-AC-02: P0B-1 定義の7種 churn state がすべて記載されている"
  - "P2-1-AC-03: state/churn_risk_hypothesis/assumed_signal/recommended_intervention/evidence_level の5カラムが存在する"
```

## Claude Code 実行手順

```
【開始前】docs/hypotheses/ ディレクトリの作成を含む内容をユーザーに確認すること。
【実行順序】テスト作成 → RED確認 → docs作成 → GREEN確認 → 自己検証 → エビデンス保存
【完了後】結果サマリーを出力して停止。次のタスクに進まないこと。
```

## テストコード `test/analytics/test_state_churn_hypothesis_table.py`

```python
import pytest
from pathlib import Path

TABLE_PATH = Path(__file__).parent.parent.parent / "docs/hypotheses/state_to_churn_table.md"
CHURN_STATES = ["来店頻度低下", "予算逼迫", "多忙", "比較疲れ", "限定感志向", "価格感度高", "接触希薄化"]
REQUIRED_COLUMNS = ["churn_risk_hypothesis", "assumed_signal", "recommended_intervention", "evidence_level"]


# P2-1-AC-01
def test_hypothesis_table_exists():
    assert TABLE_PATH.exists()


# P2-1-AC-02: 7種の churn state が全て記載されている
@pytest.mark.parametrize("state", CHURN_STATES)
def test_all_churn_states_covered(state):
    assert state in TABLE_PATH.read_text(encoding="utf-8")


# P2-1-AC-03: 必須カラムが存在する
@pytest.mark.parametrize("col", REQUIRED_COLUMNS)
def test_required_columns_exist(col):
    assert col in TABLE_PATH.read_text(encoding="utf-8")
```

## 自己検証ステップ

```
Step 2 で壊す箇所: テーブルから "来店頻度低下" の行を削除する
期待する結果: test_all_churn_states_covered[来店頻度低下] が FAIL すること
```

## 終了条件

- [ ] 全テストが PASS（parametrize 込みで 12件）
- [ ] 自己検証 Step 1〜4 完了
- [ ] **次のタスク（P2-2）には進んでいないこと**

## エビデンス保存

```bash
pytest test/analytics/test_state_churn_hypothesis_table.py -v > test/evidence/P2-1_test_result.txt
```

---
---

# ===== FILE: P2-2_intervention_selector.md =====
# P2-2｜Trait × State 別の施策差分ロジック

**ロードマップ参照:** Phase 2 — Trait × State ごとの施策差分を設計する

## Section 0 - タスク固有設定

```yaml
target_files:
  - src/services/analytics/intervention_selector.py
  - test/analytics/test_intervention_selector.py   # 新規作成
target_functions:
  - InterventionSelector.select
test_scope:
  include: "trait差分 / 最低1件返却 / 空trait / 空state / 冪等性"
  exclude: "パフォーマンス・並行性"
source_spec: docs/roadmap_churn_whitepaper_v1.md#phase-2
ac_ids:
  - "P2-2-AC-01: trait が異なると返る施策が異なる"
  - "P2-2-AC-02: 常に 1件以上の施策が返る"
  - "P2-2-AC-03: 空 trait でも施策が返る（デフォルト施策）"
  - "P2-2-AC-04: 空 state でも施策が返る（デフォルト施策）"
  - "P2-2-AC-05: 同一入力での繰り返し呼び出しで結果が安定する"
```

## Claude Code 実行手順

```
【開始前】intervention_selector.py 新規作成についてユーザーに確認を取ること。
【実行順序】テスト作成 → RED確認 → 実装 → GREEN確認 → 自己検証 → エビデンス保存
【完了後】結果サマリーを出力して停止。次のタスクに進まないこと。
```

## テストコード `test/analytics/test_intervention_selector.py`

```python
import pytest
from services.analytics.intervention_selector import InterventionSelector


@pytest.fixture
def selector():
    return InterventionSelector()


# P2-2-AC-01
def test_different_trait_yields_different_intervention(selector):
    a = selector.select(trait=["価格感度高"], state=["来店頻度低下"])
    b = selector.select(trait=["限定感志向"], state=["来店頻度低下"])
    assert a != b


# P2-2-AC-02
def test_at_least_one_intervention_returned(selector):
    assert len(selector.select(trait=["限定感志向"], state=["来店頻度低下"])) >= 1


# P2-2-AC-03: 空 trait（境界値）
def test_empty_trait_returns_default(selector):
    assert len(selector.select(trait=[], state=["来店頻度低下"])) >= 1


# P2-2-AC-04: 空 state（境界値）
def test_empty_state_returns_default(selector):
    assert len(selector.select(trait=["限定感志向"], state=[])) >= 1


# P2-2-AC-05: 冪等性
def test_repeated_call_is_stable(selector):
    a = selector.select(trait=["限定感志向"], state=["来店頻度低下"])
    b = selector.select(trait=["限定感志向"], state=["来店頻度低下"])
    assert a == b
```

## 自己検証ステップ

```
Step 2 で壊す箇所: trait による分岐を削除して全 trait に同じ施策を返す
期待する結果: test_different_trait_yields_different_intervention が FAIL すること
```

## 終了条件

- [ ] 全 5件のテストが PASS
- [ ] 自己検証 Step 1〜4 完了
- [ ] **次のタスク（P2-3）には進んでいないこと**

## エビデンス保存

```bash
pytest test/analytics/test_intervention_selector.py -v > test/evidence/P2-2_test_result.txt
```

---
---

# ===== FILE: P2-3_kpi_confirmed.md =====
# P2-3｜KPI definition の確定化

**ロードマップ参照:** Phase 2 — KPI を確定する（P0B-4 の hypothesis → confirmed）

## Section 0 - タスク固有設定

```yaml
target_files:
  - docs/specs/kpi_definition.md   # P0B-4 で作成済み。更新のみ
  - test/contracts/test_confirmed_kpi_definition.py   # 新規作成
target_functions:
  - kpi_definition ドキュメント
test_scope:
  include: "追加フィールド4種 / confirmed status の存在"
  exclude: "パフォーマンス"
source_spec: docs/roadmap_churn_whitepaper_v1.md#phase-2
ac_ids:
  - "P2-3-AC-01: baseline フィールドが記載されている"
  - "P2-3-AC-02: comparison_method フィールドが記載されている"
  - "P2-3-AC-03: data_source フィールドが記載されている"
  - "P2-3-AC-04: measurement_window フィールドが記載されている"
  - "P2-3-AC-05: status が confirmed の KPI が 1件以上存在する"
```

## Claude Code 実行手順

```
【開始前】
- kpi_definition.md を更新することをユーザーに提示して確認を取ること
- 既存内容を削除せず追記・更新のみ行うこと

【実行順序】テスト作成 → RED確認 → docs更新 → GREEN確認 → 自己検証 → エビデンス保存
【完了後】結果サマリーを出力して停止。次のタスクに進まないこと。
```

## テストコード `test/contracts/test_confirmed_kpi_definition.py`

```python
import pytest
from pathlib import Path

DOC_PATH = Path(__file__).parent.parent.parent / "docs/specs/kpi_definition.md"
NEW_FIELDS = ["baseline", "comparison_method", "data_source", "measurement_window"]


@pytest.mark.parametrize("field", NEW_FIELDS)
def test_confirmed_fields_exist(field):
    assert field in DOC_PATH.read_text(encoding="utf-8")


def test_at_least_one_confirmed_kpi():
    assert "confirmed" in DOC_PATH.read_text(encoding="utf-8")
```

## 自己検証ステップ

```
Step 2 で壊す箇所: docs から "baseline" を削除する
期待する結果: test_confirmed_fields_exist[baseline] が FAIL すること
```

## 終了条件

- [ ] 全テストが PASS（5件）
- [ ] 自己検証 Step 1〜4 完了
- [ ] **次のタスク（P2-4）には進んでいないこと**

## エビデンス保存

```bash
pytest test/contracts/test_confirmed_kpi_definition.py -v > test/evidence/P2-3_test_result.txt
```

---
---

# ===== FILE: P2-4_meta_store.md =====
# P2-4｜Meta Store prototype 実装

**ロードマップ参照:** Phase 2 — feedback / correction を Meta に保存し始める

## Section 0 - タスク固有設定

```yaml
target_files:
  - src/contracts/meta_event.schema.json
  - src/services/meta/meta_store.py
  - src/services/meta/correction_logger.py
  - test/meta/test_meta_store.py   # 新規作成
target_functions:
  - MetaStore.save
  - MetaStore.last
test_scope:
  include: "feedback/correction/rejection保存 / 空時のlast / trace_id欠落エラー"
  exclude: "パフォーマンス・並行性"
source_spec: docs/roadmap_churn_whitepaper_v1.md#phase-2
ac_ids:
  - "P2-4-AC-01: feedback イベントが保存・取得できる"
  - "P2-4-AC-02: correction イベントが保存・取得できる"
  - "P2-4-AC-03: rejection イベントが保存・取得できる"
  - "P2-4-AC-04: 何も保存していない状態で last() は None またはエラー"
  - "P2-4-AC-05: trace_id 欠落のイベントは保存を拒否される"
```

## Claude Code 実行手順

```
【開始前】3ファイルの新規作成についてユーザーに確認を取ること。
【実行順序】テスト作成 → RED確認 → 3ファイル実装 → GREEN確認 → 自己検証 → エビデンス保存
【完了後】結果サマリーを出力して停止。次のタスクに進まないこと。
```

## テストコード `test/meta/test_meta_store.py`

```python
import pytest
from services.meta.meta_store import MetaStore


@pytest.fixture
def store():
    return MetaStore()  # テストごとに新インスタンスで状態を独立


# P2-4-AC-01
def test_saves_feedback_event(store):
    store.save({"trace_id": "t1", "event_type": "feedback", "value": "反応なし"})
    assert store.last()["event_type"] == "feedback"


# P2-4-AC-02
def test_saves_correction_event(store):
    store.save({"trace_id": "t1", "event_type": "correction", "value": "価格感度高→限定感志向"})
    assert store.last()["event_type"] == "correction"


# P2-4-AC-03
def test_saves_rejection_event(store):
    store.save({"trace_id": "t1", "event_type": "rejection", "value": "施策不適切"})
    assert store.last()["event_type"] == "rejection"


# P2-4-AC-04: 空の状態で last() は None またはエラー（境界値）
def test_last_on_empty_is_none_or_raises(store):
    try:
        assert store.last() is None
    except Exception:
        pass


# P2-4-AC-05: trace_id 欠落は保存を拒否（異常系）
def test_save_without_trace_id_raises(store):
    with pytest.raises(Exception):
        store.save({"event_type": "feedback", "value": "trace_idなし"})
```

## 自己検証ステップ

```
Step 2 で壊す箇所: trace_id バリデーションを削除する
期待する結果: test_save_without_trace_id_raises が FAIL すること
```

## 終了条件

- [ ] 全 5件のテストが PASS
- [ ] 自己検証 Step 1〜4 完了
- [ ] **次のタスク（P2-5）には進んでいないこと**

## エビデンス保存

```bash
pytest test/meta/test_meta_store.py -v > test/evidence/P2-4_test_result.txt
```

---
---

# ===== FILE: P2-5_approval_gate.md =====
# P2-5｜dry_run + 人手承認付き試験運用フロー

**ロードマップ参照:** Phase 2 — dry_run + 人手承認で試験運用する

## Section 0 - タスク固有設定

```yaml
target_files:
  - src/services/execution/approval_gate.py
  - test/execution/test_approval_gate.py   # 新規作成
target_functions:
  - ApprovalGate.check
test_scope:
  include: "承認あり / 承認なし / approved キー欠落（デフォルト拒否）"
  exclude: "パフォーマンス・並行性"
source_spec: docs/roadmap_churn_whitepaper_v1.md#phase-2
ac_ids:
  - "P2-5-AC-01: approved=False のとき can_execute=False"
  - "P2-5-AC-02: approved=True のとき can_execute=True"
  - "P2-5-AC-03: approved キー欠落はデフォルト拒否（Deny by Default）"
```

## Claude Code 実行手順

```
【開始前】approval_gate.py 新規作成についてユーザーに確認を取ること。
【実行順序】テスト作成 → RED確認 → 実装 → GREEN確認 → 自己検証 → エビデンス保存
【完了後】結果サマリーを出力して停止。次のタスクに進まないこと。
```

## テストコード `test/execution/test_approval_gate.py`

```python
import pytest
from services.execution.approval_gate import ApprovalGate


@pytest.fixture
def gate():
    return ApprovalGate()


# P2-5-AC-01
def test_blocked_without_approval(gate):
    assert gate.check({"approved": False})["can_execute"] is False


# P2-5-AC-02
def test_passes_with_approval(gate):
    assert gate.check({"approved": True})["can_execute"] is True


# P2-5-AC-03: approved キー欠落はデフォルト拒否（境界値）
def test_missing_approved_key_defaults_to_deny(gate):
    assert gate.check({})["can_execute"] is False
```

## 自己検証ステップ

```
Step 2 で壊す箇所: デフォルト拒否を削除して approved キー欠落を True 扱いにする
期待する結果: test_missing_approved_key_defaults_to_deny が FAIL すること
```

## 終了条件

- [ ] 全 3件のテストが PASS
- [ ] 自己検証 Step 1〜4 完了
- [ ] **次のタスク（P3-1）には進んでいないこと**

## エビデンス保存

```bash
pytest test/execution/test_approval_gate.py -v > test/evidence/P2-5_test_result.txt
```

---
---

# ===== FILE: P3-1_policy_engine.md =====
# P3-1｜Consent / Policy 制御の実装

**ロードマップ参照:** Phase 3 — consent / policy 制御を明確化する（「怖いから使えない」を構造で解消する）

## Section 0 - タスク固有設定

```yaml
target_files:
  - src/policy/consent.py
  - src/policy/policy_engine.py
  - docs/specs/policy_design.md
  - test/policy/test_policy_engine.py   # 新規作成
target_functions:
  - PolicyEngine.evaluate
test_scope:
  include: "send系ブロック / send系許可 / audit記録 / consent欠落デフォルト拒否 / 非send系は許可"
  exclude: "パフォーマンス・並行性"
source_spec: docs/roadmap_churn_whitepaper_v1.md#phase-3
ac_ids:
  - "P3-1-AC-01: consent=False では send 系がブロックされる"
  - "P3-1-AC-02: consent=True では send 系が許可される"
  - "P3-1-AC-03: ポリシー判定結果が audit に記録される"
  - "P3-1-AC-04: consent キー欠落はデフォルト拒否"
  - "P3-1-AC-05: 非 send 系は consent に関わらず許可される"
```

## Claude Code 実行手順

```
【開始前】
- src/policy/ ディレクトリ作成を含む3ファイルの新規作成をユーザーに確認すること
- AuditStore はインメモリ実装とすること（外部DB接続禁止）

【実行順序】テスト作成 → RED確認 → 実装 → GREEN確認 → 自己検証 → エビデンス保存
【完了後】結果サマリーを出力して停止。次のタスクに進まないこと。
```

## テストコード `test/policy/test_policy_engine.py`

```python
import pytest
from policy.policy_engine import PolicyEngine


@pytest.fixture
def engine():
    return PolicyEngine()


# P3-1-AC-01
def test_send_blocked_without_consent(engine):
    assert engine.evaluate(action="send_line_message", context={"consent": False})["allowed"] is False


# P3-1-AC-02
def test_send_allowed_with_consent(engine):
    assert engine.evaluate(action="send_line_message", context={"consent": True})["allowed"] is True


# P3-1-AC-03: audit に記録される
def test_policy_result_is_audited(engine):
    engine.evaluate(action="send_line_message", context={"consent": True})
    assert engine.audit_store.last()["action"] == "send_line_message"


# P3-1-AC-04: consent キー欠落はデフォルト拒否（境界値）
def test_missing_consent_defaults_to_deny(engine):
    assert engine.evaluate(action="send_line_message", context={})["allowed"] is False


# P3-1-AC-05: 非 send 系は consent 不問で許可
def test_non_send_allowed_without_consent(engine):
    assert engine.evaluate(action="create_followup_task", context={"consent": False})["allowed"] is True
```

## 自己検証ステップ

```
Step 2 で壊す箇所: consent=False でもブロックしないよう条件を削除する
期待する結果: test_send_blocked_without_consent が FAIL すること
```

## 終了条件

- [ ] 全 5件のテストが PASS
- [ ] docs/specs/policy_design.md が作成されていること
- [ ] 自己検証 Step 1〜4 完了
- [ ] **次のタスク（P3-2）には進んでいないこと**

## エビデンス保存

```bash
pytest test/policy/test_policy_engine.py -v > test/evidence/P3-1_test_result.txt
```

---
---

# ===== FILE: P3-2_approval_flow_doc.md =====
# P3-2｜Approval Flow 文書化

**ロードマップ参照:** Phase 3 — 承認ゲートを追加する

## Section 0 - タスク固有設定

```yaml
target_files:
  - docs/specs/approval_flow.md
  - test/policy/test_approval_flow_doc.py   # 新規作成
target_functions:
  - approval_flow ドキュメント
test_scope:
  include: "ファイル存在 / 必須キーワード3種"
  exclude: "パフォーマンス"
source_spec: docs/roadmap_churn_whitepaper_v1.md#phase-3
ac_ids:
  - "P3-2-AC-01: approval_flow.md が存在する"
  - "P3-2-AC-02: エスカレーション手順が記載されている"
  - "P3-2-AC-03: 自動実行不可条件が記載されている"
  - "P3-2-AC-04: 再承認条件が記載されている"
```

## Claude Code 実行手順

```
【開始前】docs/specs/approval_flow.md 新規作成についてユーザーに確認を取ること。
【実行順序】テスト作成 → RED確認 → docs作成 → GREEN確認 → 自己検証 → エビデンス保存
【完了後】結果サマリーを出力して停止。次のタスクに進まないこと。
```

## テストコード `test/policy/test_approval_flow_doc.py`

```python
import pytest
from pathlib import Path

DOC_PATH = Path(__file__).parent.parent.parent / "docs/specs/approval_flow.md"
REQUIRED_KEYWORDS = ["エスカレーション", "自動実行", "再承認"]


def test_approval_flow_doc_exists():
    assert DOC_PATH.exists()


@pytest.mark.parametrize("keyword", REQUIRED_KEYWORDS)
def test_required_section_exists(keyword):
    assert keyword in DOC_PATH.read_text(encoding="utf-8")
```

## 終了条件

- [ ] 全テストが PASS（4件）
- [ ] 自己検証 Step 1〜4 完了
- [ ] **次のタスク（P3-3）には進んでいないこと**

## エビデンス保存

```bash
pytest test/policy/test_approval_flow_doc.py -v > test/evidence/P3-2_test_result.txt
```

---
---

# ===== FILE: P3-3_rollback_playbook_doc.md =====
# P3-3｜Rollback Playbook 整備

**ロードマップ参照:** Phase 3 — ロールバック方針を整備する

## Section 0 - タスク固有設定

```yaml
target_files:
  - docs/specs/rollback_playbook.md
  - test/policy/test_rollback_playbook_doc.py   # 新規作成
target_functions:
  - rollback_playbook ドキュメント
test_scope:
  include: "ファイル存在 / 必須5シナリオ網羅"
  exclude: "パフォーマンス"
source_spec: docs/roadmap_churn_whitepaper_v1.md#phase-3
ac_ids:
  - "P3-3-AC-01: rollback_playbook.md が存在する"
  - "P3-3-AC-02〜06: 誤配信/誤セグメント/誤推論/手動介入/監査記録 が各々記載されている"
```

## Claude Code 実行手順

```
【開始前】docs/specs/rollback_playbook.md 新規作成についてユーザーに確認を取ること。
【完了後】結果サマリーを出力して停止。次のタスクに進まないこと。
```

## テストコード `test/policy/test_rollback_playbook_doc.py`

```python
import pytest
from pathlib import Path

DOC_PATH = Path(__file__).parent.parent.parent / "docs/specs/rollback_playbook.md"
REQUIRED_SCENARIOS = ["誤配信", "誤セグメント", "誤推論", "手動介入", "監査記録"]


def test_rollback_playbook_exists():
    assert DOC_PATH.exists()


@pytest.mark.parametrize("scenario", REQUIRED_SCENARIOS)
def test_required_scenarios_covered(scenario):
    assert scenario in DOC_PATH.read_text(encoding="utf-8")
```

## 終了条件

- [ ] 全テストが PASS（6件）
- [ ] 自己検証 Step 1〜4 完了
- [ ] **次のタスク（P4-1）には進んでいないこと**

## エビデンス保存

```bash
pytest test/policy/test_rollback_playbook_doc.py -v > test/evidence/P3-3_test_result.txt
```

---
---

# ===== FILE: P4-1_adapter_interface.md =====
# P4-1｜Adapter Pattern 共通化

**ロードマップ参照:** Phase 4 — adapter pattern を共通化する

## Section 0 - タスク固有設定

```yaml
target_files:
  - docs/specs/adapter_pattern.md
  - test/adapters/test_adapter_interface_contract.py   # 新規作成
target_functions:
  - MockLineAdapter / MockCrmAdapter / MockTaskAdapter（interface 検証のみ）
test_scope:
  include: "docs存在 / 4 interface文書確認 / 全3 Adapter × 全4メソッド存在確認"
  exclude: "パフォーマンス"
source_spec: docs/roadmap_churn_whitepaper_v1.md#phase-4
ac_ids:
  - "P4-1-AC-01: adapter_pattern.md が存在する"
  - "P4-1-AC-02: 4 interface が docs に記載されている"
  - "P4-1-AC-03: 3つの Mock Adapter が全て 4 interface を実装している"
```

## Claude Code 実行手順

```
【開始前】docs/specs/adapter_pattern.md 新規作成のみであることをユーザーに確認すること。
【注意】src/adapters/ の既存コードは変更禁止。テストで interface を確認するのみ。
【完了後】結果サマリーを出力して停止。次のタスクに進まないこと。
```

## テストコード `test/adapters/test_adapter_interface_contract.py`

```python
import pytest
from pathlib import Path
from adapters.mock_line_adapter import MockLineAdapter
from adapters.mock_crm_adapter import MockCrmAdapter
from adapters.mock_task_adapter import MockTaskAdapter

DOC_PATH = Path(__file__).parent.parent.parent / "docs/specs/adapter_pattern.md"
ADAPTER_CLASSES = [MockLineAdapter, MockCrmAdapter, MockTaskAdapter]
REQUIRED_METHODS = ["validate", "execute", "rollback", "audit"]


def test_adapter_pattern_doc_exists():
    assert DOC_PATH.exists()


@pytest.mark.parametrize("method", REQUIRED_METHODS)
def test_interface_documented(method):
    assert method in DOC_PATH.read_text(encoding="utf-8")


@pytest.mark.parametrize("adapter_cls", ADAPTER_CLASSES)
@pytest.mark.parametrize("method", REQUIRED_METHODS)
def test_all_adapters_implement_interface(adapter_cls, method):
    assert hasattr(adapter_cls(), method)
```

## 終了条件

- [ ] 全テストが PASS（parametrize 込みで 17件）
- [ ] 自己検証 Step 1〜4 完了
- [ ] **次のタスク（P4-2）には進んでいないこと**

## エビデンス保存

```bash
pytest test/adapters/test_adapter_interface_contract.py -v > test/evidence/P4-1_test_result.txt
```

---
---

# ===== FILE: P4-2_saas_backlog_doc.md =====
# P4-2｜SaaS integration backlog 作成

**ロードマップ参照:** Phase 4 — CRM / LINE / 配信基盤の優先順位を整理する

## Section 0 - タスク固有設定

```yaml
target_files:
  - docs/specs/saas_integration_backlog.md
  - test/adapters/test_saas_integration_backlog_doc.py   # 新規作成
source_spec: docs/roadmap_churn_whitepaper_v1.md#phase-4
ac_ids:
  - "P4-2-AC-01: saas_integration_backlog.md が存在する"
  - "P4-2-AC-02: priority カラムが存在する"
  - "P4-2-AC-03: CRM / LINE / 配信基盤 / タスク管理が含まれる"
```

## Claude Code 実行手順

```
【開始前】docs新規作成についてユーザーに確認すること。
【完了後】結果サマリーを出力して停止。次のタスクに進まないこと。
```

## テストコード `test/adapters/test_saas_integration_backlog_doc.py`

```python
import pytest
from pathlib import Path

DOC_PATH = Path(__file__).parent.parent.parent / "docs/specs/saas_integration_backlog.md"
REQUIRED_SERVICES = ["CRM", "LINE", "配信", "タスク"]


def test_backlog_doc_exists():
    assert DOC_PATH.exists()


def test_backlog_has_priority_column():
    assert "priority" in DOC_PATH.read_text(encoding="utf-8").lower()


@pytest.mark.parametrize("service", REQUIRED_SERVICES)
def test_required_services_covered(service):
    assert service in DOC_PATH.read_text(encoding="utf-8")
```

## 終了条件

- [ ] 全テストが PASS（6件）
- [ ] **次のタスク（P4-3）には進んでいないこと**

## エビデンス保存

```bash
pytest test/adapters/test_saas_integration_backlog_doc.py -v > test/evidence/P4-2_test_result.txt
```

---
---

# ===== FILE: P4-3_second_integration_doc.md =====
# P4-3｜Second integration plan 作成

**ロードマップ参照:** Phase 4 — 2つ目以降の接続先候補を整理する

## Section 0 - タスク固有設定

```yaml
target_files:
  - docs/specs/second_integration_plan.md
  - test/adapters/test_second_integration_plan_doc.py
source_spec: docs/roadmap_churn_whitepaper_v1.md#phase-4
ac_ids:
  - "P4-3-AC-01: second_integration_plan.md が存在する"
  - "P4-3-AC-02〜06: required fields / policy impact / rollback impact / KPI impact が各々記載されている"
```

## Claude Code 実行手順

```
【完了後】結果サマリーを出力して停止。次のタスクに進まないこと。
```

## テストコード `test/adapters/test_second_integration_plan_doc.py`

```python
import pytest
from pathlib import Path

DOC_PATH = Path(__file__).parent.parent.parent / "docs/specs/second_integration_plan.md"
REQUIRED_SECTIONS = ["required fields", "policy impact", "rollback impact", "KPI impact"]


def test_second_integration_plan_exists():
    assert DOC_PATH.exists()


@pytest.mark.parametrize("section", REQUIRED_SECTIONS)
def test_required_sections_covered(section):
    assert section in DOC_PATH.read_text(encoding="utf-8")
```

## 終了条件

- [ ] 全テストが PASS（5件）
- [ ] **次のタスク（P5-1）には進んでいないこと**

## エビデンス保存

```bash
pytest test/adapters/test_second_integration_plan_doc.py -v > test/evidence/P4-3_test_result.txt
```

---
---

# ===== FILE: P5-1_whitepaper_doc.md =====
# P5-1｜Whitepaper 改訂版の作成

**ロードマップ参照:** Phase 5 — Whitepaper を実装実績ベースの設計文書に再構成する

## Section 0 - タスク固有設定

```yaml
target_files:
  - docs/whitepaper.md
  - test/contracts/test_revised_whitepaper_doc.py
source_spec: docs/roadmap_churn_whitepaper_v1.md#phase-5
ac_ids:
  - "P5-1-AC-01〜05: KPI/D Layer接続/Meta/Safety・Governance/SaaS が各々記載されている"
```

## Claude Code 実行手順

```
【開始前】whitepaper.md の更新についてユーザーに確認すること。既存内容を削除しないこと。
【完了後】結果サマリーを出力して停止。次のタスクに進まないこと。
```

## テストコード `test/contracts/test_revised_whitepaper_doc.py`

```python
import pytest
from pathlib import Path

DOC_PATH = Path(__file__).parent.parent.parent / "docs/whitepaper.md"
REQUIRED_TOPICS = {
    "P5-1-AC-01": ["KPI"],
    "P5-1-AC-02": ["D Layer", "業務接続"],
    "P5-1-AC-03": ["Meta"],
    "P5-1-AC-04": ["Safety", "Governance"],
    "P5-1-AC-05": ["SaaS"],
}


@pytest.mark.parametrize("ac_id,keywords", REQUIRED_TOPICS.items())
def test_whitepaper_contains_required_topic(ac_id, keywords):
    text = DOC_PATH.read_text(encoding="utf-8")
    assert any(kw in text for kw in keywords)
```

## 終了条件

- [ ] 全テストが PASS（5件）
- [ ] **次のタスク（P5-2）には進んでいないこと**

## エビデンス保存

```bash
pytest test/contracts/test_revised_whitepaper_doc.py -v > test/evidence/P5-1_test_result.txt
```

---
---

# ===== FILE: P5-2_business_mapping_doc.md =====
# P5-2｜business mapping 改訂

**ロードマップ参照:** Phase 5 — revised business mapping

## Section 0 - タスク固有設定

```yaml
target_files:
  - docs/business-mapping.md
  - test/contracts/test_revised_business_mapping_doc.py
source_spec: docs/roadmap_churn_whitepaper_v1.md#phase-5
ac_ids:
  - "P5-2-AC-01: business-mapping.md が存在する"
  - "P5-2-AC-02: churn または チャーン が含まれる"
  - "P5-2-AC-03: P0B-1 定義の churn state が 1件以上言及されている"
```

## Claude Code 実行手順

```
【開始前】既存 business-mapping.md を更新する場合、削除せず追記・更新のみとすること。
【完了後】結果サマリーを出力して停止。次のタスクに進まないこと。
```

## テストコード `test/contracts/test_revised_business_mapping_doc.py`

```python
from pathlib import Path

DOC_PATH = Path(__file__).parent.parent.parent / "docs/business-mapping.md"
CHURN_STATES = ["来店頻度低下", "限定感志向", "価格感度高", "接触希薄化"]


def test_business_mapping_exists():
    assert DOC_PATH.exists()


def test_business_mapping_mentions_churn():
    text = DOC_PATH.read_text(encoding="utf-8")
    assert "churn" in text.lower() or "チャーン" in text


def test_at_least_one_churn_state_mentioned():
    text = DOC_PATH.read_text(encoding="utf-8")
    assert any(s in text for s in CHURN_STATES)
```

## 終了条件

- [ ] 全 3件のテストが PASS
- [ ] **次のタスク（P5-3）には進んでいないこと**

## エビデンス保存

```bash
pytest test/contracts/test_revised_business_mapping_doc.py -v > test/evidence/P5-2_test_result.txt
```

---
---

# ===== FILE: P5-3_presentation_doc.md =====
# P5-3｜対内・対外説明資料ドラフト作成

**ロードマップ参照:** Phase 5 — external/internal presentation draft

## Section 0 - タスク固有設定

```yaml
target_files:
  - docs/demo/README_churn_demo.md
  - test/contracts/test_presentation_draft_doc.py
source_spec: docs/roadmap_churn_whitepaper_v1.md#phase-5
ac_ids:
  - "P5-3-AC-01: README_churn_demo.md が存在する"
  - "P5-3-AC-02: mock または dry_run の境界が明示されている"
  - "P5-3-AC-03: 何を証明したか／していないかが記載されている"
  - "P5-3-AC-04: KPI 仮説への言及がある"
  - "P5-3-AC-05: 安全に扱える根拠（consent/policy/rollback）が記載されている"
```

## Claude Code 実行手順

```
【開始前】docs/demo/ ディレクトリ作成を含む新規ファイル作成をユーザーに確認すること。
【完了後】結果サマリーを出力して停止。これが最終タスクです。
```

## テストコード `test/contracts/test_presentation_draft_doc.py`

```python
import pytest
from pathlib import Path

DOC_PATH = Path(__file__).parent.parent.parent / "docs/demo/README_churn_demo.md"
REQUIRED = {
    "P5-3-AC-02": ["mock", "dry_run"],
    "P5-3-AC-03": ["証明"],
    "P5-3-AC-04": ["KPI"],
    "P5-3-AC-05": ["consent", "policy", "rollback"],
}


def test_demo_doc_exists():
    assert DOC_PATH.exists()


@pytest.mark.parametrize("ac_id,keywords", REQUIRED.items())
def test_required_content_exists(ac_id, keywords):
    text = DOC_PATH.read_text(encoding="utf-8").lower()
    assert any(kw.lower() in text for kw in keywords)
```

## 終了条件

- [ ] 全テストが PASS（5件）
- [ ] 自己検証 Step 1〜4 完了
- [ ] **これが最終タスクです。追加の作業は行わないこと**

## エビデンス保存

```bash
pytest test/contracts/test_presentation_draft_doc.py -v > test/evidence/P5-3_test_result.txt
```
