T1-3 を実施してください。

目的:
- Phase0の出力（state/intent/next_actions）から、LINE validate に渡す payload を作る。
- 送信禁止（dry_run固定）。

実装:
- src/services/bindings/line_binding.py を新設
- build_line_messages(state_intent_json) -> dict を実装
  - validate_request形式に変換する
  - messages はまず text 1件で良い（例: next_actions を箇条書きにまとめる）
  - channel は "push" をデフォルトにする（受信者IDは扱わず validateのみ）
  - dry_run=true を必須固定
- “文章出力禁止”は Generatorの話。ここはLINE payload生成なのでOKだが、
  出力はLINE message object（JSON）に限定。

テスト:
- test/services/test_line_binding.py を追加
- state/intent 出力から validate_request が生成されること
- dry_run が必ず true であること
- messages が空にならないこと

完了:
- pytest -v PASS
- test/evidence/T1-3_test_result.txt 保存
- diff提示