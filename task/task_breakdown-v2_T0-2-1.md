T0-2-1 を実施してください。

内容:
- src/contracts/state_intent.schema.json を作成
- Draft7 JSON Schema
- required: state, intent, next_actions, confidence, trace_id
- state.minItems = 3
- next_actions.minItems = 3
- confidence 0〜1

テスト:
- test/contracts/test_state_intent_schema.py を追加/修正
- pytest -v 実行
- PASSさせる

完了後:
- test/evidence/T0-2-1_test_result.txt にpytest出力保存
- 変更diffを提示