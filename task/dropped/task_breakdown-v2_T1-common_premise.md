Phase1（LINE DryRun接続）を開始します。

最優先:
- AGENTS.md に厳密に従う
- task/ のPhase1タスクに従う（Phase0のDoD方式：pytest PASS / evidence保存 / diff提示）
- 本番送信は禁止。dry_run=true のみ。外部へ実メッセージ送信しない。

DryRunの定義:
- LINE Messaging API の「Validate message objects」系エンドポイントを用いて、
  送信payloadの妥当性を検証する（push/narrowcast/broadcast等のvalidate）。
- validate成功=DryRun成功。送信API（push/broadcast等）は叩かない。

共通DoD:
- pytest -v を実行し全テストPASS
- 実行ログを test/evidence/{task_id}_test_result.txt に保存
- Pythonファイルには日本語docstring必須
- diff を提示してから次へ進む

まず、Phase1で追加/変更するファイル一覧を短く箇条書きで提示してから実装に入ってください。