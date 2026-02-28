# Demo Phase0 — Subjective Agent Architecture

## 1. 位置づけ

This demo represents **Phase0** of the Subjective Agent Architecture.

Phase0の目的は：

- 構造の正当性証明
- 再現性の担保
- 安全設計（DryRun + Rollback）の明示
- 「state → intent → action」接続の可視化

本デモは **本番統合を目的としたものではありません**。  
あくまで「構造が価値に接続可能であること」を証明する段階です。

---

## 2. デモの目的

社内で説明したいのは以下の一点です：

> 自然文から "state" を抽出し、  
> それが施策（action）に接続される構造を持てる。

正解率より重要なのは：

- stateが分割されること
- intentが明示されること
- actionが業務APIに接続可能な形式で出ること
- 安全設計（dry_run / rollback_plan）が存在すること
- trace_idで監査可能であること

---

## 3. アーキテクチャ（Phase0）

```
Input (Natural Language)
  ↓
Reader
  * state候補抽出
  ↓
Validator
  * JSON Schema検証
  * 必須項目確認
  * retry制御
  ↓
Generator
  * state/intent/next_actions確定
  * rollback_plan生成
  * action_bindings (dry_run=true)
  ↓
Structured Output (JSON)
```

---

## 4. 出力構造（抜粋）

```json
{
  "state": [...],
  "intent": "...",
  "next_actions": [...],
  "confidence": 0.8,
  "trace_id": "...",
  "rollback_plan": "...",
  "action_bindings": [
    {
      "action": "LINE配信",
      "api": "line.broadcast",
      "dry_run": true
    }
  ]
}
```

重要ポイント：

- `dry_run: true` → 本番誤実行を防ぐ
- `rollback_plan` → 説明責任と安全性
- `trace_id` → 監査可能設計

---

## 5. デモシナリオ（社内向け題材）

### ケース①：チャーン兆候

**入力：**

> 最近来店が減っている。値引きには反応しないが、限定感には反応する。

**出力：**

- state: 来店頻度低下 / 価格感度低 / 限定志向
- intent: 再来店動機付け
- next_actions: 限定LINE配信案 / 会員限定イベント

---

### ケース②：CS問い合わせ増加

**入力：**

> サポート問い合わせが増加。機能は使われているが設定が複雑との声がある。

**出力：**

- state: 利用継続 / UX摩擦あり / 設定理解不足
- intent: 解約防止
- next_actions: チュートリアル配信 / UI改善提案

---

### ケース③：販促施策停滞

**入力：**

> DM配信の開封率が下がっている。キャンペーンの内容は変えていない。

**出力：**

- state: 開封率低下 / コンテンツ固定化
- intent: 反応率改善
- next_actions: セグメント配信 / 件名ABテスト

---

## 6. Phase0で証明できたこと

- ✅ JSON Schemaで構造保証
- ✅ 37件テストパス（pytest自動実行）
- ✅ 10回連続実行でも安定出力
- ✅ 空入力は400エラー
- ✅ DryRun安全設計
- ✅ Rollback設計
- ✅ trace_id監査可能

---

## 7. Phase0でやっていないこと

- ❌ 本番API接続
- ❌ 実データ接続
- ❌ ROI算出
- ❌ 自動実行

---

## 8. 次フェーズへの接続

Phase1では：

- 限定業務APIに接続（LINE DryRun → 限定実行）
- 1業務に絞った価値証明
- 施策 → KPI接続

---

## 9. 社内へのメッセージ

このデモは、「LLMで賢くする」ことが目的ではない。

目的は：

> 業務構造をstateとして分解し、  
> 意図（intent）と施策（action）を接続できる構造を持つこと。

これが成立すれば、

- チャーン対策
- CS最適化
- 販促最適化
- 店舗施策設計

すべてに拡張可能。

---

## 10. 結論

Phase0は、**構造の再現性と安全性の証明**。

この土台があることで、Phase1以降の「価値接続」が現実的になります。
