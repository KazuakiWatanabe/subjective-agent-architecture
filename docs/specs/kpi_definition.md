# KPI Definition

Phase 0B では KPI を仮定義として扱い、`status` はすべて `hypothesis` とする。  
Phase 2 で計測定義と baseline を確定し、必要に応じて `confirmed` へ更新する。

## KPI 一覧

| name | definition | numerator | denominator | frequency | owner | status |
| --- | --- | --- | --- | --- | --- | --- |
| 再来店率 | 施策対象顧客のうち再来店した割合 | 再来店した顧客数 | 施策対象顧客数 | monthly | pm | hypothesis |
| 30日継続率 | 接触後30日以内に継続利用した割合 | 30日以内継続利用顧客数 | 対象接触顧客数 | monthly | pm | hypothesis |
| 施策反応率 | 配信やオファーに反応した割合 | 反応した顧客数 | 施策配信顧客数 | weekly | marketing | hypothesis |
| 誤配信率 | 不適切な配信と判定された割合 | 誤配信件数 | 総配信件数 | weekly | operations | hypothesis |
| Meta 蓄積速度 | 補正に使える Meta が増える速度 | 新規 Meta 記録件数 | 観測期間日数 | weekly | pm | hypothesis |

## Note

- 再来店率、30日継続率、施策反応率、誤配信率、Meta 蓄積速度の 5 種を Phase 0B の対象とする。
- この文書は仮定義メモであり、確定版は Phase 2 の KPI 定義タスクで更新する。
