T0-3-1 を実施してください。

内容:
- src/services/inference/reader.py を実装
- Reader.extract(text) を実装
- 空文字/None は ValueError
- LLM失敗時は ReaderError をraise
- list[str] を返す

テスト:
- test/agents/test_reader.py をPASSさせる
- LLMはモック可能にする（_call_llm を分離）

完了後:
- test/evidence/T0-3-1_test_result.txt 保存
- diff提示