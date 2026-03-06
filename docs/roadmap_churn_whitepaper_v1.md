# Churn Prevention to Whitepaper Roadmap v1

Version: v1  
Date: 2026-03  
Status: Current roadmap  
Previous roadmap: `docs/roadmap.md`

---

## 1. Purpose / この文書の目的

本ドキュメントは、`subjective-agent-architecture` における **Phase 0 実装完了後の現在地** を整理し、
**チャーン防止ユースケースから Whitepaper の方向へ最大化するためのロードマップ** を定義するものです。

狙いは、単なる構造説明や PoC の延長ではなく、
**主観状態（Trait / State / Meta）を業務接続し、KPI 改善につなげるまでの実装計画** を明確にすることです。

また本書は、既存の詳細版ロードマップ `docs/roadmap.md` を置き換えるものではなく、
**チャーン防止ユースケースに絞った現行実行計画** として位置づけます。

---

## 2. Current Position / 現在の立ち位置

### 2.1 What has been achieved

Phase 0 の実装により、以下はすでに一定程度実証できています。

- 自然文から state / intent / next_actions を抽出する構造
- subjective interpretation の基本的な流れ
- 社内向けに「主観を構造化できる」ことを示すデモ
- architecture の概念説明に耐える最小限の動く証拠

### 2.2 What is still missing

一方で、Whitepaper の方向性と比較すると、以下が不足しています。

- state が実際の業務アクションに接続されること
- state とチャーン予兆の相関検証
- Trait × State ごとの施策最適化
- Meta による施策改善ループ
- KPI / ROI ベースで説明できること

### 2.3 Gap / 乖離の正体

現在の Phase 0 は、主に **構造証明（structure proof）** の段階です。

しかし Whitepaper が本来目指しているのは、
**「主観状態を扱える」ことではなく、「主観状態を業務に接続し、継続率やLTV改善につなげる」こと** です。

つまり今のギャップは、

- 現在地: 主観を分類・解釈できる
- 目標: 主観を施策・業務接続・KPI改善に使える

という差です。

---

## 3. Strategic Direction / 今後の基本方針

### 3.1 Focus the theme on churn prevention

今後のテーマは広げず、まずは **チャーン防止** に固定します。

理由:

- Business Mapping 上で最も事業接続しやすい
- 継続率 / 再来店率 / 反応率など、評価指標を置きやすい
- Whitepaper の主張を KPI に翻訳しやすい
- 社内説明において「何に効くのか」が明確になる

### 3.2 Prioritize connection over sophistication

今後の重点は、state の精緻化そのものではありません。重要なのは、**state → action の接続を通すこと** です。

したがって順序は次です。

1. 主観状態を抽出する
2. 業務原子（Business Primitives）へ落とす
3. Mock / Adapter で接続する
4. KPI との関係を見る
5. 学習ループへ進む

### 3.3 Reframe the value proposition

今後の対内・対外説明は、
「AIが主観を理解する」では弱く、

#### 「顧客状態を仮説化し、チャーン防止施策につなげる」

という表現へ寄せます。

---

## 4. Target State / 目指す到達点

到達点は、次の状態です。

- Trait / State / Meta を最小限扱える
- state に応じて業務施策を候補化できる
- 少なくとも1本の施策フローが接続される
- 施策結果を Meta として蓄積できる
- KPI 改善仮説を測定できる
- Whitepaper を「思想」ではなく「実装済み設計思想」として再構成できる

---

## 5. Phase Mapping / 既存 roadmap.md との対応

本書は `docs/roadmap.md` の Phase 体系を大きく崩さず、
**チャーン防止ユースケースに合わせて実行順を再解釈したもの** です。

| This document | Original `docs/roadmap.md` | Notes |
| --- | --- | --- |
| Phase 0A | Phase 0 | Phase 0 完了判定 |
| Phase 0B | Phase 0 の後半タスク | 旧 0.5 相当。Phase番号は増やさない |
| Phase 1 | Phase 1 | D層：業務接続 |
| Phase 2 | Phase 2 | C層：Trait / State / Meta 運用開始 |
| Phase 3 | Phase 3 | 安全性・説明責任 |
| Phase 4 | Phase 4 | 横展開・SaaS統合 |
| Phase 5 | Phase 5 | Whitepaper 完全体 |

---

## 6. Phase Roadmap / フェーズ別ロードマップ

### Phase 0A — Phase 0 Completion Gate

#### Objective

既存 `docs/roadmap.md` における Phase 0 を正式に完了判定する。

#### Completion Gate

以下は旧ロードマップの完了条件を引き継ぐ。

- 自然文 → JSON が安定出力（10回試行で8回以上）
- state → next_actions の接続が人間に理解される
- rollback_plan / confidence / trace_id が出力に含まれる
- Cloud Run で動作確認できる

#### Exit Condition

社内レビュー参加者 **3名以上** の場で、次の反応または同等の質問が確認されること。

> 「これ、うちの CRM に接続できる？」

この問いが出た時点で、構造証明から業務接続フェーズへ移行する。

補足として、これは主観的な盛り上がりではなく、
**「構造理解の次に接続可能性が論点になった」ことを確認するゲート** として扱う。

### Phase 0B — Demo Reframing for Churn

#### Objective (Phase 0B)

Phase 0 の成果物を、**分類デモ** から **チャーン防止判断支援デモ** へ再編集する。

#### Tasks (Phase 0B)

- state 語彙をチャーン文脈に寄せる
  - 例: 来店頻度低下 / 予算逼迫 / 多忙 / 比較疲れ / 限定感志向
- Trait / State / Meta の3層を最低限表現する
- next_actions を自然文ではなく業務原子に寄せる
- デモ資料を「構造説明」から「施策判断支援」へ修正する
- KPI を **仮定義** する

#### Deliverables (Phase 0B)

- churn-oriented demo JSON
- revised demo README
- revised explanation slides or markdown
- KPI hypothesis memo

### Phase 1 — D Layer First (Business Connection)

#### Objective (Phase 1)

主観状態から業務アクションへの **最小接続** を証明する。

#### Tasks (Phase 1)

- Business Primitives を定義する
  - `segment_customers`
  - `send_line_message`
  - `reserve_offer`
  - `cancel_offer`
  - `create_followup_task`
- Mock Adapter を実装する
- Validate → Plan → Apply の最小フローを作る
- Audit Log を保存する
- dry_run モードを入れる
- rollback / compensating action の最小形を作る

#### Deliverables (Phase 1)

- primitives spec
- mock adapter implementation
- execution flow demo
- audit log sample

### Phase 2 — C Layer and Churn Correlation

#### Objective (Phase 2)

Trait / State / Meta を最小運用しながら、
state が本当にチャーン予兆として使えるかを確認する。

#### Note

本書では、**C層の最小運用開始と Meta の初期蓄積開始を同一フェーズで扱う**。
これは `docs/roadmap.md` の思想を否定するものではなく、
チャーン防止ユースケースにおいては **早期に feedback / correction を溜め始めた方が有効** という実装上の判断である。

#### Tasks (Phase 2)

- 過去データを用いて state とチャーン予兆の相関を見る
- Trait × State ごとの施策差分を設計する
- KPI を **確定** する
  - 再来店率
  - 30日継続率
  - 施策反応率
  - 誤配信率
  - Meta 蓄積速度
- dry_run + 人手承認で試験運用する
- feedback / correction を Meta に保存し始める

#### Deliverables (Phase 2)

- KPI definition document
- state-to-churn hypothesis table
- intervention design draft
- meta store prototype

### Phase 3 — Safety, Policy, Governance

#### Objective (Phase 3)

業務適用に必要な安全性・説明責任を整備する。

#### Design Principle

「怖いから使えない」を構造で消す。

#### Tasks (Phase 3)

- consent / policy 制御を明確化する
- 承認ゲートを追加する
- ロールバック方針を整備する
- audit trail を拡張する
- 誤配信や誤推論時の対応フローを作る

#### Deliverables (Phase 3)

- policy design
- approval flow
- rollback playbook
- governance notes

### Phase 4 — Expansion and SaaS Integration

#### Objective (Phase 4)

Phase 1-3 で証明した「1業務接続」を、複数接続へ広げる。

#### Tasks (Phase 4)

- 2つ目以降の接続先候補を整理する
- adapter pattern を共通化する
- CRM / LINE / 配信基盤の優先順位を整理する
- state 更新根拠データとの結合を強める

#### Deliverables (Phase 4)

- adapter pattern memo
- SaaS integration backlog
- second integration plan

### Phase 5 — Whitepaper Reconstruction

#### Objective (Phase 5)

Whitepaper を、思想文書から **実装実績ベースの設計文書** に再構成する。

#### Tasks (Phase 5)

- KPI 仮説と実証結果を反映する
- D Layer 接続実績を明記する
- C Layer 的な学習ループの成果を反映する
- 安全性・説明責任の設計を統合する
- 将来の SaaS 横展開パターンを整理する

#### Deliverables (Phase 5)

- revised whitepaper
- revised business mapping
- external/internal presentation draft

---

## 7. KPI Strategy / KPI の置き方

KPI は後回しにしない。ただし、**最初から確定もしない**。

したがって、本ロードマップでは次の2段階で扱う。

### Phase 0B で仮定義する KPI

- 再来店率
- 30日継続率
- 施策反応率
- 誤配信率
- Meta 蓄積速度

### Phase 2 で確定する KPI

- 計測定義
- 分母 / 分子
- 計測頻度
- baseline
- 比較方法（一律施策 vs state-based施策）

これにより、直近優先事項と後続スケジュールの矛盾を解消する。

---

## 8. Concrete Schedule / 具体スケジュール

### 2026-03

- Phase 0 完了判定会議
- demo をチャーン専用語彙へ再調整
- Trait / State / Meta の最小表現を追加
- README / demo explanation を施策判断支援型へ修正
- KPI 仮定義を作成

### 2026-04

- Business Primitives 定義
- Mock Adapter 実装開始
- `segment_customers` / `send_line_message` / `create_followup_task` を優先実装
- Audit Log 最小版を作成

### 2026-05

- Validate → Plan → Apply の一連フローを実装
- dry_run / approval gate を追加
- rollback の最小構造を追加
- 社内向け 2nd demo 実施

### 2026-06

- 過去データで state とチャーン予兆の相関確認
- KPI 定義の確定
- Trait × State 別の施策分岐草案を作成
- Meta 保存開始

### 2026-07

- 小規模な比較テスト設計
- 一律施策 vs state-based 施策 の比較準備
- feedback / correction を蓄積

### 2026-08

- Meta に基づく補正ロジック試験
- 施策外れの学習ループ検証
- recommendation の改善確認

### 2026-09

- Policy / Consent / Governance の強化
- 誤配信・誤推論時の運用設計
- 監査ログを強化

### 2026-10 to 2026-11

- 2つ目の接続先候補を整理
- adapter pattern を共通化
- Whitepaper 改訂版の構成を作成

### 2026-12

- Whitepaper 改訂版を公開
- business mapping を更新
- 「チャーン防止での実装実績」中心に再編集
- 外部説明向けの story 化を実施

---

## 9. Preserved Concepts / 旧 roadmap.md から引き継ぐ重要概念

本書では詳細を簡略化しているが、以下の概念は削除ではなく **継承** する。

### 9.1 Preference State の三層構造

- Trait: 長期傾向
- State: 短期変動
- Meta: 修正履歴・否定ログ・補正根拠

### 9.2 SaaS Adapter Interface

将来の Phase 4 で横展開するため、以下のインターフェース思想を保持する。

```text
validate(input): ValidationResult
execute(primitive, input): ExecutionResult
rollback(execution_id): RollbackResult
audit(execution_id): AuditRecord
```

### 9.3 Safety by Structure

口頭説明ではなく、**policy / consent / rollback / audit** によって
「怖いから使えない」を構造で解消する。

### 9.4 Reference

詳細設計は以下を参照する。

- Previous roadmap: `docs/roadmap.md`
- Related business mapping: `docs/business-mapping.md`  
  - 存在する場合は参照する。未作成の場合は **作成予定ドキュメント** として扱う。

---

## 10. Immediate Priorities / 直近の最優先事項

今すぐやるべきことは次の3つです。

### 1. Whitepaper の到達点をチャーン防止に固定する

汎用議論に広げず、1業務で勝ち筋を作る。

### 2. Demo output を execution-oriented にする

説明 JSON ではなく、Primitives につながる出力へ寄せる。

### 3. KPI を仮定義してから検証へ進む

いきなり確定せず、まず仮置きし、Phase 2 で定義を確定する。

---

## 11. Final Message / 結論

現在の Phase 0 実装は、Whitepaper から外れているのではなく、
**Whitepaper に向かうための土台** です。

ただし、ここから先に必要なのは、
「主観をうまく説明すること」ではなく、

### 「主観をチャーン防止の業務とKPIに接続すること」

です。

今後の判断基準は次の一文に集約されます。

> State をきれいに出すことではなく、State で再来店率を動かせることを証明する。
