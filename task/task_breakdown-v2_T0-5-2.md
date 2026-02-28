T0-5-2 を実施してください。

内容:
- POST /convert 実装
- Reader → Orchestrator 経由
- 空入力は400
- rollback_plan を必ず含める
- 10回中8回以上schema通過

テスト:
- test/integration/test_convert_e2e.py をPASS

完了後:
- test/evidence/T0-5-2_test_result.txt 保存
- diff提示