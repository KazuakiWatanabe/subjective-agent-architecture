# Business Primitives

Phase 1 では、主観状態から実行計画へ接続する最小単位として Business Primitive を定義する。  
Phase 0B で定義した `recommended_primitives` は、ここで示す 5 種の primitive 名に対応する。

## Primitive List

| name | input | output | dry_run_behavior | rollback_hint | audit_fields |
| --- | --- | --- | --- | --- | --- |
| segment_customers | segment_rule, source_scope | segment_id, matched_count | 条件評価のみ実施し、セグメント登録は行わない | dry_run では rollback 不要。本実行時は生成 segment_id を無効化する | trace_id, segment_id, matched_count, dry_run, timestamp |
| send_line_message | segment_id, message | execution_id, status | 対象件数と配信内容の確認まで行い、送信しない | 送信済みは取消不可。フォローアップ送信で補償する | trace_id, execution_id, segment_id, dry_run, timestamp |
| reserve_offer | customer_id, offer_id | reservation_id, status | 予約可否だけ判定し、実予約は作成しない | reservation_id を使って予約を取消する | trace_id, reservation_id, offer_id, dry_run, timestamp |
| cancel_offer | reservation_id, reason | cancellation_id, status | 取消対象の確認のみ行い、取消確定はしない | 誤取消時は reserve_offer で再登録する | trace_id, cancellation_id, reservation_id, dry_run, timestamp |
| create_followup_task | customer_id, task_type, note | task_id, status | タスク内容を生成するが、実タスクは登録しない | task_id を使ってクローズまたは無効化する | trace_id, task_id, customer_id, dry_run, timestamp |

## Notes

- `segment_customers`, `send_line_message`, `reserve_offer`, `cancel_offer`, `create_followup_task` の 5 種を初期セットとする。
- すべての primitive は Phase 1 時点では `dry_run` 前提で扱い、本番副作用は発生させない。
- audit_fields は後続の Audit Log 実装で最低限残すべき観測項目を示す。
