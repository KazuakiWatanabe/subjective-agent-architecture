T1-5 を実施してください。

目的:
- Phase1の安全性をテストで固定する（“絶対に実送信しない”）。

実装:
- src/services/line/line_client.py に「send系メソッド」を作らない（禁止）
- src/services/bindings/line_binding.py で dry_run は常に true
- src/services/inference/generator.py でも action_bindings がある場合 dry_run=true を強制（あれば）

テスト:
- test/security/test_no_send_operations.py を追加
  - LineClient に send/push/broadcast 的なメソッドが存在しないこと
  - validate_request.dry_run が必ず true であること
- 既存テストもPASS

完了:
- pytest -v PASS
- test/evidence/T1-5_test_result.txt 保存
- diff提示