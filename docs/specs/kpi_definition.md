# KPI Definition

Phase 0B では KPI を仮定義として扱い、`status` はすべて `hypothesis` としていた。  
Phase 2 では baseline、comparison_method、data_source、measurement_window を追加し、計測定義が固まった KPI から `confirmed` へ更新する。

## KPI 一覧

| name | definition | numerator | denominator | frequency | owner | baseline | comparison_method | data_source | measurement_window | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 再来店率 | 施策対象顧客のうち再来店した割合 | 再来店した顧客数 | 施策対象顧客数 | monthly | pm | 一律施策での再来店率 18% | state-based施策群と一律施策群の月次比較 | CRM 来店履歴、配信対象一覧 | 初回接触後30日 | confirmed |
| 30日継続率 | 接触後30日以内に継続利用した割合 | 30日以内継続利用顧客数 | 対象接触顧客数 | monthly | pm | 直近四半期平均 42% | trait/state 別施策対象と従来施策対象の cohort 比較 | CRM 利用履歴、配信ログ | 接触日から30日 | confirmed |
| 施策反応率 | 配信やオファーに反応した割合 | 反応した顧客数 | 施策配信顧客数 | weekly | marketing | 現行配信平均 6% | state-based配信と通常配信の週次比較 | LINE 配信ログ、クーポン利用ログ | 配信後7日 | confirmed |
| 誤配信率 | 不適切な配信と判定された割合 | 誤配信件数 | 総配信件数 | weekly | operations | 手動レビュー時の誤配信率 1.5% | 承認付き配信と従来配信の差分比較 | 監査ログ、CS 問い合わせ記録 | 配信後7日 | hypothesis |
| Meta 蓄積速度 | 補正に使える Meta が増える速度 | 新規 Meta 記録件数 | 観測期間日数 | weekly | pm | 週次 15 件 | state ごとの補正記録件数推移を週次比較 | Meta store、feedback log | 毎週月曜締め | hypothesis |

## Phase 2 Confirmed Fields

- `baseline`: 比較起点となる現行値または過去平均
- `comparison_method`: 一律施策と state-based施策の比較方法
- `data_source`: 集計元となるログまたは業務データ
- `measurement_window`: KPI を集計する観測期間

## Note

- 再来店率、30日継続率、施策反応率、誤配信率、Meta 蓄積速度の 5 種を継続して対象とする。
- Phase 2 時点では業務接続の効果測定に直結する 3 KPI を confirmed、運用設計の残る 2 KPI を hypothesis とする。
