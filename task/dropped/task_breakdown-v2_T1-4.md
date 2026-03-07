T1-4 を実施してください。

目的:
- /convert の結果（Phase0 JSON）に、LINE DryRun（validate）結果を付ける。
- 送信は禁止。validateのみ。

実装:
- src/services/inference/orchestrator.py または別の app layer で
  1) Phase0のstate_intent出力を得る
  2) line_binding で validate_request を作る
  3) line_client.validate_messages を実行
  4) 出力に line_dry_run を付与（例: { ok, issues, line_status_code, request_id }）
- LINEのvalidateが失敗しても、/convert 自体は 200 を返して良い（判断材料として返す）。
  ただし issues に理由を入れる。
- Audit Log にも line_dry_run 結果を保存する。

テスト:
- test/integration/test_convert_line_dry_run.py を追加
- LineClient をモックして:
  - validate OK の場合 line_dry_run.ok=True
  - validate NG の場合 line_dry_run.ok=False かつ issues が入る
- 送信APIが呼ばれていないこと（LineClientはvalidateのみ実装なので担保される）

完了:
- pytest -v PASS
- test/evidence/T1-4_test_result.txt 保存
- diff提示