# Subjective Agent Architecture
## Whitepaper 実現ロードマップ（詳細版）

---

## 全体構造

```
Phase 0（社内モック）   ← 今ここ
    ↓ 「動く証拠」確立
Phase 1（D層：業務接続）
    ↓ state → 実行可能アクション 接続証明
Phase 2（C層：主観状態管理）
    ↓ ユーザーごとの学習ループ稼働
Phase 3（安全性・説明責任）
    ↓ エンタープライズ耐性
Phase 4（横展開・SaaS統合）
    ↓ 複数業務ドメインへ
Phase 5（Whitepaper完全体）
    → OSS・標準化・ポータブル主観モデル
```

---

## Phase 0：社内モック（現在〜2週間）

### 目的
「構造説明」より先に **触れる証拠** を作る。
agentic-bizflow の出力スキーマを state/intent 版に差し替える。

### 成果物

| # | 成果物 | 詳細 |
|---|---|---|
| 0-1 | `contracts/state_intent.schema.json` | 出力スキーマ固定 |
| 0-2 | `/convert` エンドポイント差し替え | Reader→Validator→Generator |
| 0-3 | プリセット入力ボタン | 「来店減」例文をワンクリック投入 |
| 0-4 | Cloud Run 更新デプロイ | 既存URLを上書きまたは別URL発行 |
| 0-5 | `docs/internal-demo-plan.md` | 社内共有用デモ説明資料 |

### 出力スキーマ（固定項目）

```json
{
  "state": ["来店頻度低下", "価格感度低", "限定感志向"],
  "intent": "再来店動機付け",
  "next_actions": ["限定LINE配信案", "会員限定イベント企画", "期間限定特典付与"],
  "constraints": ["過去7日以内配信済み除外", "クーポン併用不可"],
  "confidence": 0.82,
  "assumptions": ["来店履歴は直近90日基準"],
  "rollback_plan": "配信停止 + セグメント解除",
  "risks": ["誤配信リスク", "施策重複リスク"],
  "trace_id": "uuid",
  "generated_at": "ISO8601"
}
```

### エージェント構成（最小版）

```
Reader      ← 自然文から state 候補を抽出
    ↓
Validator   ← state>=3, intent必須, next_actions>=3, 矛盾チェック
    ↓ NG → Reader に差し戻し（最大2回 Retry）
Generator   ← JSON 固定出力（文章禁止）
```

### 完了条件（Acceptance Criteria）
- [ ] 自然文 → JSON が安定出力（10回試行で8回以上）
- [ ] state → next_actions の接続が人間に理解される
- [ ] rollback_plan / confidence / trace_id が出力に含まれる
- [ ] Cloud Run で動作確認

### 社内議論で出てほしい反応
> 「これ、うちの CRM に接続できる？」

→ これが出たら Phase 1 へ進む合図。

---

## Phase 1：D層（業務接続）〜2ヶ月

### 目的
state → Business Primitive（業務原子API）への接続を **1本証明** する。
「他社がやっていない理由」をコードで消す。

### 前提：Business Primitives とは
業務を最小単位のAPIに分解したもの。副作用が冪等で、意味が明確で、失敗時に補償できる操作。

例（小売・CRM文脈）：
```
segment_customers(conditions)   → 顧客セグメント作成
send_line_message(segment_id)   → LINE配信
reserve_offer(customer_id)      → 特典予約
cancel_offer(offer_id)          → 特典取消（compensating action）
get_visit_history(customer_id)  → 来店履歴取得
```

### Epic D1：Business Primitives API（意味API層）

| タスク | 内容 |
|---|---|
| D1-1 | Primitives の OpenAPI / JSON Schema 定義（5本） |
| D1-2 | Mock Adapter 実装（インメモリ or SQLite） |
| D1-3 | 各 Primitive の冪等性キー定義 |
| D1-4 | 契約テスト（入出力の保証） |

### Epic D2：Validate → Plan → Apply Gateway

```
Validate  ← 権限・同意・操作許可判定
    ↓
Plan      ← 実行順序・前提条件・リトライ戦略
    ↓
Apply     ← 実行 + 失敗ハンドリング
    ↓
Audit     ← 実行理由・主観状態・結果を保存
```

| タスク | 内容 |
|---|---|
| D2-1 | Validate：Policyチェック（仮実装でOK） |
| D2-2 | Plan：実行順序の決定ロジック |
| D2-3 | Apply：2つ以上の Primitives を連続実行 |
| D2-4 | 失敗パターンのテスト（在庫不足・権限エラー） |

### Epic D3：監査ログ + ロールバック基盤

| フィールド | 内容 |
|---|---|
| who | user_id, agent_name |
| when | timestamp |
| what | primitive_name, input, output |
| why | intent, state, confidence |
| trace_id | 主観状態との紐付け |
| rollback_status | 取消可否・compensating action |

### Phase 1 完了条件
- [ ] state（例：来店頻度低下）→ segment_customers → send_line_message が通る
- [ ] Audit Log に「なぜ配信したか」が残る
- [ ] 故意に失敗させても Rollback か 冪等で回復できる
- [ ] Mock Adapter を本物の API に差し替える準備ができている

---

## Phase 2：C層（主観状態管理）〜3ヶ月

### 目的
ユーザーごとに **Preference State を蓄積・更新** し、
推論精度と説明責任を同時に高める。

### Preference State の三層構造

```
Trait（長期傾向）
├── 更新頻度：低
├── 減衰：ゆるい
└── 例：価格感度低 / ブランド志向 / 新製品感度高

State（短期変動）
├── 更新頻度：高
├── 減衰：早い
└── 例：直近来店なし / 直近クーポン未使用 / 直近イベント参加

Meta（修正履歴）
├── 更新頻度：イベント駆動
└── 例：「それは違う」の否定ログ / フィードバック重みづけ
```

### Epic C1：Preference State Store v0

| タスク | 内容 |
|---|---|
| C1-1 | State Store のスキーマ設計（Trait/State/Meta） |
| C1-2 | `get_state(user_id)` API |
| C1-3 | `apply_feedback(user_id, feedback)` API |
| C1-4 | Trait の時間減衰ロジック |
| C1-5 | Meta への否定ログ蓄積 |

### Epic C2：Intent & Preference Parser + Confidence Scoring

| タスク | 内容 |
|---|---|
| C2-1 | LLM による state 抽出（ルール + LLM ハイブリッド） |
| C2-2 | confidence スコアの計算ロジック |
| C2-3 | 曖昧性ハンドラ（追加質問が必要な条件を定義） |
| C2-4 | state の粒度チェック（too broad / too narrow の検出） |

### Epic C3：Feedback Recalibration（修正ループ）

```
Agent 出力
    ↓
ユーザー確認（「それは違う」/ 「合ってる」）
    ↓
Meta に蓄積
    ↓
次回推論で再ランキング / ルール補正
    ↓（繰り返し）
Trait の緩やかな更新
```

### Phase 2 完了条件
- [ ] `get_state` → state/intent 生成 → D層実行 が一本で通る
- [ ] フィードバック後に次回出力が変化する
- [ ] Trait が3回以上の feedback で安定的に更新される
- [ ] confidence が正直（高すぎず低すぎず）

---

## Phase 3：安全性・説明責任強化〜4ヶ月

### 目的
エンタープライズ導入に耐える **安全性・監査・同意管理** を揃える。
「怖いから使えない」の懸念を構造で消す。

### Epic S1：Policy Engine（ポリシー制御）

```
操作要求
    ↓
Policy Engine
├── 同意チェック（このユーザーはこの操作に同意しているか）
├── 制限チェック（配信頻度上限・対象除外条件）
├── リスク評価（誤配信リスク・炎上リスク）
└── 承認ゲート（高リスク操作は人間承認を要求）
    ↓
Validate → Plan → Apply
```

### Epic S2：ロールバック自動化

| 操作 | Compensating Action |
|---|---|
| send_line_message | 配信取消 + 対象除外リスト追加 |
| reserve_offer | cancel_offer |
| segment_customers | セグメント解除 |

### Epic S3：説明責任ログ（Audit 強化）

- 「なぜこの state を導いたか」の推論根拠保存
- 「なぜこの Primitive を選んだか」の意図保存
- 外部監査ツールへのエクスポート対応

### Phase 3 完了条件
- [ ] Policy Engine が同意のない操作をブロックできる
- [ ] 高リスク操作で人間承認フローが動く
- [ ] 全操作が Audit Log → 外部ツール連携できる
- [ ] 誤配信を想定したロールバック訓練が通る

---

## Phase 4：横展開・SaaS統合〜6ヶ月

### 目的
Phase 1-3 で証明した「1業務接続」を **複数ドメイン・複数SaaS** に広げる。

### 優先順位（接続価値の高い順）

| 優先度 | SaaS | 接続価値 |
|---|---|---|
| ★★★ | LINE Business / プッシュ通知 | 直接の配信実行 |
| ★★★ | CRM（Salesforce / HubSpot 等） | state の根拠データ |
| ★★ | POS / 購買データ | Trait 更新の根拠 |
| ★★ | DM基盤（既存配信ツール） | 既存フローとの接続 |
| ★ | Google Workspace / Slack | 承認フロー・通知 |

### Epic E1：SaaS Adapter パターン化

Mock Adapter → 本物 Adapter への差し替えを **パターン化** する。
新しい SaaS を追加するコストを最小化する。

```
interface SaaSAdapter {
  validate(input): ValidationResult
  execute(primitive, input): ExecutionResult
  rollback(execution_id): RollbackResult
  audit(execution_id): AuditRecord
}
```

### Phase 4 完了条件
- [ ] 2つ以上の本物 SaaS と接続できている
- [ ] 新しい SaaS Adapter を1週間以内に追加できる
- [ ] CRM データが Trait/State 更新の根拠になっている

---

## Phase 5：Whitepaper 完全体〜1年

### 目的
実装実績を根拠に、**設計思想を標準化・OSS化・外部公開**する。

### 標準化の対象

| 対象 | 内容 |
|---|---|
| Subjective State Schema | Trait/State/Meta の標準フォーマット |
| Business Primitives Interface | SaaS横断で使える操作の共通I/F |
| Portable State Model | SaaS を跨いで state を持ち運べる形式 |
| Safety Protocol | Policy / Consent / Rollback の標準パターン |

### Whitepaper 完全体の証明条件

```
実装の実績
├── 2つ以上のSaaS接続
├── フィードバックループの稼働
├── 監査ログの外部公開デモ
└── ロールバックの自動化実証
    ↓
設計思想の検証
├── 「主観状態が業務接続を最適化した」事例
├── 「他社が接続できなかった理由」を構造で解決した事例
└── 「説明責任が担保された自律実行」の事例
    ↓
OSS公開 / 外部連携 / 標準化提案
```

---

## マイルストーン一覧

| Phase | 期間 | 証明すること |
|---|---|---|
| Phase 0 | 〜2週間 | state が施策に接続できる構造がある |
| Phase 1 | 〜2ヶ月 | state → 実際の業務APIが動く |
| Phase 2 | 〜3ヶ月 | 主観状態が蓄積・更新される |
| Phase 3 | 〜4ヶ月 | 安全に自律実行できる |
| Phase 4 | 〜6ヶ月 | 複数業務ドメインに横展開できる |
| Phase 5 | 〜1年 | Whitepaper が「実装済みの設計思想」になる |

---

## 戦略的判断軸（常に立ち返る問い）

> **「接続できた」から勝つ。「構造が正しい」から勝つのではない。**

- 正解率より「state → 施策 の接続の可視化」
- 完全体より「価値が出る最小単位で切る」
- 説明より「触れるもので判断させる」
- 「怖い」を口で解消せず「構造（rollback/policy/audit）で消す」
