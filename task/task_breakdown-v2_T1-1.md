T1-1 を実施してください。

目的:
- LINE DryRun（validate）に必要な入出力の契約を固定する。

実装:
- src/contracts/line/ を新設し、以下を作成
  - validate_request.schema.json（内部API: /line/validate 用）
  - validate_response.schema.json
- validate_request には最低限:
  - channel: "push" | "broadcast" | "narrowcast" | "multicast"
  - messages: LINE message objects（今回は text を最低限サポート）
  - dry_run: true（必須）
- validate_response:
  - ok: bool
  - issues: list[str]
  - line_status_code: number（呼び出した場合）
  - request_id: string（取得できる場合）
  - trace_id: string

テスト:
- test/contracts/test_line_validate_schema.py を追加
- jsonschema.Draft7Validator.check_schema で schema妥当性確認
- valid/invalid payload の validate テスト

完了:
- pytest -v PASS
- test/evidence/T1-1_test_result.txt に保存
- diff提示