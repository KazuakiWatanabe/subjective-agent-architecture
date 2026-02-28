T1-2 を実施してください。

目的:
- LINE Messaging API の validate エンドポイントを叩くクライアントを実装する。
- 送信は禁止。validateのみ。

実装:
- src/services/line/line_client.py を新設
- LineClient.validate_messages(channel: str, messages: list[dict]) -> ValidateResult を実装
- HTTPは requests を使用（依存が既にあればそれに合わせる）
- 認証は環境変数 LINE_CHANNEL_ACCESS_TOKEN を参照（値はログに出さない）
- エラー時は LineClientError を raise
- レスポンスヘッダに request id があれば取得して返す（可能な範囲で）

テスト:
- test/services/test_line_client.py を追加
- requests をモックして:
  - 200 OKケース
  - 400系（validate NG）のケース
  - 500/timeout例外のケース
- secretsがログに出ないこと（print/ログ出力しない）

完了:
- pytest -v PASS
- test/evidence/T1-2_test_result.txt 保存
- diff提示