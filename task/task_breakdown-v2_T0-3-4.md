T0-3-4 を実施してください。

内容:
- src/services/inference/orchestrator.py を実装
- Reader → Validator → Generator の順
- Validator NG の場合 最大2回 retry
- 2回失敗で MaxRetryError
- 成功/失敗いずれも Audit保存
- generatorはvalidation失敗時に呼ばない

テスト:
- test/agents/test_orchestrator.py をPASS

完了後:
- test/evidence/T0-3-4_test_result.txt 保存
- diff提示