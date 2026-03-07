# タスク分解 v2（テスト付き実装ガイド）
## Phase 0：社内モック

> **完了定義（全タスク共通）**
> ルートで `pytest` を実行し、全テストが PASS した時点でタスク完了。
> エビデンスは `test/evidence/{task_id}_test_result.txt` に保存。

---

## リポジトリ構造（前提）

```
subjective-agent-architecture/
  docs/
    whitepaper.md
  task/
    task-breakdown-v2.md        ← 本ファイル
  test/
    contracts/
      test_state_intent_schema.py
    agents/
      test_reader.py
      test_validator.py
      test_generator.py
      test_orchestrator.py
      test_orchestrator_audit.py
    integration/
      test_health.py
      test_convert_e2e.py
    evidence/
      T0-2-1_test_result.txt
      ...
  src/
    contracts/
      state_intent.schema.json
      presets.json
    services/
      inference/
        reader.py
        validator.py
        generator.py
        orchestrator.py
        audit_store.py
  conftest.py                   ← sys.path解決
  pytest.ini                    ← testpaths = test
  LICENSE
  README.md
```

**conftest.py（ルート）**
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))
```

**pytest.ini（ルート）**
```ini
[pytest]
testpaths = test
```

---

## 変更サマリ（v1 → v2）

| # | 変更内容 | 理由 |
|---|---------|------|
| 追加 | T0-2-1に `action_bindings` フィールドを追加 | stateを業務プリミティブに接続する設計の基盤 |
| 追加 | T0-3-4（Orchestrator）にAudit Logテストを追加 | 再現性・監査可能性の技術的証明 |
| 変更 | スキーマの `rollback_plan` をトップレベル必須に昇格 | E2Eで検証済みの実績を構造に反映 |
| 変更 | エビデンスにT0-3-4aを追加（Audit Log専用） | Audit LogはOrchestratorと独立して証明する |

---

## T0-2｜出力スキーマ固定

### T0-2-1：state_intent.schema.json の作成

**実装内容**
`src/contracts/state_intent.schema.json` を作成する。

**完了条件**
- JSON Schema として文法的に正しい
- 必須項目（state, intent, next_actions, confidence, trace_id, rollback_plan, action_bindings）が定義されている
- `state` は minItems: 3、`next_actions` は minItems: 3 が定義されている
- `action_bindings` の各要素が `action / api / dry_run` を持つ

**スキーマ構造（参考）**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["state", "intent", "next_actions", "confidence", "trace_id", "rollback_plan", "action_bindings"],
  "properties": {
    "state": { "type": "array", "items": { "type": "string" }, "minItems": 3 },
    "intent": { "type": "string" },
    "next_actions": { "type": "array", "items": { "type": "string" }, "minItems": 3 },
    "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
    "trace_id": { "type": "string" },
    "rollback_plan": { "type": "string" },
    "action_bindings": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["action", "api", "dry_run"],
        "properties": {
          "action": { "type": "string" },
          "api": { "type": "string" },
          "dry_run": { "type": "boolean" }
        }
      },
      "minItems": 1
    }
  }
}
```

**テストコード** → `test/contracts/test_state_intent_schema.py`
```python
import json
import pytest
from pathlib import Path
import jsonschema

SCHEMA_PATH = Path(__file__).parent.parent.parent / "src/contracts/state_intent.schema.json"

@pytest.fixture
def schema():
    return json.loads(SCHEMA_PATH.read_text())

def test_schema_file_exists():
    assert SCHEMA_PATH.exists()

def test_schema_is_valid_json_schema(schema):
    jsonschema.Draft7Validator.check_schema(schema)

def test_required_fields_defined(schema):
    required = schema.get("required", [])
    for field in ["state", "intent", "next_actions", "confidence", "trace_id", "rollback_plan", "action_bindings"]:
        assert field in required

def test_state_min_items(schema):
    assert schema["properties"]["state"]["minItems"] == 3

def test_next_actions_min_items(schema):
    assert schema["properties"]["next_actions"]["minItems"] == 3

def test_confidence_range(schema):
    conf = schema["properties"]["confidence"]
    assert conf["minimum"] == 0
    assert conf["maximum"] == 1

def test_action_bindings_min_items(schema):
    assert schema["properties"]["action_bindings"]["minItems"] == 1

def test_action_bindings_item_required_fields(schema):
    item_required = schema["properties"]["action_bindings"]["items"]["required"]
    for field in ["action", "api", "dry_run"]:
        assert field in item_required

def test_valid_payload_passes(schema):
    payload = {
        "state": ["来店頻度低下", "価格感度低", "限定感志向"],
        "intent": "再来店動機付け",
        "next_actions": ["限定LINE配信案", "会員限定イベント", "期間限定特典"],
        "confidence": 0.82,
        "trace_id": "test-uuid-001",
        "rollback_plan": "配信停止→通常施策に戻す",
        "action_bindings": [
            {"action": "LINE配信", "api": "line.broadcast", "dry_run": True}
        ]
    }
    jsonschema.validate(payload, schema)

def test_invalid_payload_missing_intent_fails(schema):
    payload = {
        "state": ["来店頻度低下", "価格感度低", "限定感志向"],
        "next_actions": ["A", "B", "C"],
        "confidence": 0.5,
        "trace_id": "x",
        "rollback_plan": "戻す",
        "action_bindings": [{"action": "A", "api": "a.b", "dry_run": True}]
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, schema)

def test_invalid_state_too_few_items_fails(schema):
    payload = {
        "state": ["来店頻度低下"],
        "intent": "再来店",
        "next_actions": ["A", "B", "C"],
        "confidence": 0.5,
        "trace_id": "x",
        "rollback_plan": "戻す",
        "action_bindings": [{"action": "A", "api": "a.b", "dry_run": True}]
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, schema)

def test_invalid_action_bindings_missing_dry_run_fails(schema):
    payload = {
        "state": ["来店頻度低下", "価格感度低", "限定感志向"],
        "intent": "再来店動機付け",
        "next_actions": ["A", "B", "C"],
        "confidence": 0.5,
        "trace_id": "x",
        "rollback_plan": "戻す",
        "action_bindings": [{"action": "LINE配信", "api": "line.broadcast"}]
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, schema)
```

**エビデンス保存**
```bash
pytest test/contracts/test_state_intent_schema.py -v > test/evidence/T0-2-1_test_result.txt
```

---

## T0-3｜エージェント差し替え

### T0-3-1：Reader の実装

**実装内容** → `src/services/inference/reader.py`

**テストコード** → `test/agents/test_reader.py`
```python
import pytest
from unittest.mock import patch
from services.inference.reader import Reader, ReaderError

@pytest.fixture
def reader():
    return Reader()

def test_reader_returns_state_list(reader):
    with patch.object(reader, "_call_llm", return_value=["来店頻度低下", "価格感度低", "限定感志向"]):
        result = reader.extract("最近来店が減っている。値引きには反応しないが、限定感には反応する。")
    assert isinstance(result, list)
    assert len(result) >= 1

def test_reader_returns_at_least_one_state(reader):
    with patch.object(reader, "_call_llm", return_value=["来店頻度低下"]):
        result = reader.extract("何か変化があった")
    assert len(result) >= 1

def test_reader_raises_on_llm_failure(reader):
    with patch.object(reader, "_call_llm", side_effect=Exception("LLM error")):
        with pytest.raises(ReaderError):
            reader.extract("テスト入力")

def test_reader_raises_on_empty_input(reader):
    with pytest.raises(ValueError):
        reader.extract("")

def test_reader_raises_on_none_input(reader):
    with pytest.raises(ValueError):
        reader.extract(None)
```

**エビデンス保存**
```bash
pytest test/agents/test_reader.py -v > test/evidence/T0-3-1_test_result.txt
```

---

### T0-3-2：Validator の実装

**実装内容** → `src/services/inference/validator.py`

**テストコード** → `test/agents/test_validator.py`
```python
import pytest
from services.inference.validator import Validator, ValidationResult

@pytest.fixture
def validator():
    return Validator()

VALID_PAYLOAD = {
    "state": ["来店頻度低下", "価格感度低", "限定感志向"],
    "intent": "再来店動機付け",
    "next_actions": ["限定LINE配信案", "会員限定イベント", "期間限定特典"],
    "confidence": 0.82,
    "trace_id": "test-001",
    "rollback_plan": "配信停止→通常施策に戻す",
    "action_bindings": [
        {"action": "LINE配信", "api": "line.broadcast", "dry_run": True}
    ]
}

def test_valid_payload_passes(validator):
    result = validator.validate(VALID_PAYLOAD)
    assert result.ok is True
    assert result.issues == []

def test_missing_intent_fails(validator):
    payload = {**VALID_PAYLOAD}
    del payload["intent"]
    result = validator.validate(payload)
    assert result.ok is False
    assert any("intent" in issue for issue in result.issues)

def test_state_too_few_fails(validator):
    payload = {**VALID_PAYLOAD, "state": ["来店頻度低下", "価格感度低"]}
    result = validator.validate(payload)
    assert result.ok is False
    assert any("state" in issue for issue in result.issues)

def test_next_actions_too_few_fails(validator):
    payload = {**VALID_PAYLOAD, "next_actions": ["A", "B"]}
    result = validator.validate(payload)
    assert result.ok is False

def test_confidence_out_of_range_fails(validator):
    payload = {**VALID_PAYLOAD, "confidence": 1.5}
    result = validator.validate(payload)
    assert result.ok is False

def test_duplicate_state_detected(validator):
    payload = {**VALID_PAYLOAD, "state": ["来店頻度低下", "来店頻度低下", "価格感度低"]}
    result = validator.validate(payload)
    assert result.ok is False
    assert any("重複" in issue for issue in result.issues)

def test_empty_action_bindings_fails(validator):
    payload = {**VALID_PAYLOAD, "action_bindings": []}
    result = validator.validate(payload)
    assert result.ok is False
    assert any("action_bindings" in issue for issue in result.issues)

def test_empty_payload_fails(validator):
    result = validator.validate({})
    assert result.ok is False
```

**エビデンス保存**
```bash
pytest test/agents/test_validator.py -v > test/evidence/T0-3-2_test_result.txt
```

---

### T0-3-3：Generator の実装

**実装内容** → `src/services/inference/generator.py`

**テストコード** → `test/agents/test_generator.py`
```python
import pytest
import json
import jsonschema
from pathlib import Path
from datetime import datetime
from services.inference.generator import Generator, GeneratorError
from services.inference.validator import ValidationResult

SCHEMA_PATH = Path(__file__).parent.parent.parent / "src/contracts/state_intent.schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text())

@pytest.fixture
def generator():
    return Generator()

VALID_INPUT = {
    "state": ["来店頻度低下", "価格感度低", "限定感志向"],
    "intent": "再来店動機付け",
    "next_actions": ["限定LINE配信案", "会員限定イベント", "期間限定特典"],
    "confidence": 0.82,
    "rollback_plan": "配信停止→通常施策に戻す",
    "action_bindings": [
        {"action": "LINE配信", "api": "line.broadcast", "dry_run": True}
    ]
}

def test_generator_output_passes_schema(generator):
    result = generator.generate(VALID_INPUT, ValidationResult(ok=True, issues=[]))
    jsonschema.validate(result, SCHEMA)

def test_generator_adds_trace_id(generator):
    result = generator.generate(VALID_INPUT, ValidationResult(ok=True, issues=[]))
    assert "trace_id" in result
    assert len(result["trace_id"]) > 0

def test_trace_id_is_uuid_format(generator):
    import re
    result = generator.generate(VALID_INPUT, ValidationResult(ok=True, issues=[]))
    uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    assert re.match(uuid_pattern, result["trace_id"])

def test_generator_adds_generated_at(generator):
    result = generator.generate(VALID_INPUT, ValidationResult(ok=True, issues=[]))
    assert "generated_at" in result
    datetime.fromisoformat(result["generated_at"])

def test_generator_output_contains_action_bindings(generator):
    result = generator.generate(VALID_INPUT, ValidationResult(ok=True, issues=[]))
    assert "action_bindings" in result
    assert len(result["action_bindings"]) >= 1

def test_generator_action_bindings_dry_run_is_true(generator):
    result = generator.generate(VALID_INPUT, ValidationResult(ok=True, issues=[]))
    for binding in result["action_bindings"]:
        assert binding["dry_run"] is True

def test_generator_output_contains_rollback_plan(generator):
    result = generator.generate(VALID_INPUT, ValidationResult(ok=True, issues=[]))
    assert "rollback_plan" in result
    assert len(result["rollback_plan"]) > 0

def test_generator_raises_on_validation_failure(generator):
    with pytest.raises(GeneratorError):
        generator.generate(VALID_INPUT, ValidationResult(ok=False, issues=["intent が不足"]))

def test_generator_output_contains_no_free_text(generator):
    result = generator.generate(VALID_INPUT, ValidationResult(ok=True, issues=[]))
    text_fields = [v for v in result.values() if isinstance(v, str) and len(v) > 100]
    assert text_fields == []
```

**エビデンス保存**
```bash
pytest test/agents/test_generator.py -v > test/evidence/T0-3-3_test_result.txt
```

---

### T0-3-4：Orchestrator（Retry Loop）の実装

**実装内容** → `src/services/inference/orchestrator.py`

**テストコード** → `test/agents/test_orchestrator.py`
```python
import pytest
from unittest.mock import MagicMock
from services.inference.orchestrator import Orchestrator, MaxRetryError
from services.inference.validator import ValidationResult

VALID_OUTPUT = {
    "state": ["来店頻度低下", "価格感度低", "限定感志向"],
    "intent": "再来店動機付け",
    "next_actions": ["限定LINE配信案", "会員限定イベント", "期間限定特典"],
    "confidence": 0.82,
    "trace_id": "test-uuid-001",
    "generated_at": "2026-02-28T00:00:00",
    "rollback_plan": "配信停止→通常施策に戻す",
    "action_bindings": [
        {"action": "LINE配信", "api": "line.broadcast", "dry_run": True}
    ]
}

@pytest.fixture
def orchestrator():
    return Orchestrator()

def test_success_on_first_attempt(orchestrator):
    orchestrator.reader.extract = MagicMock(return_value=["A", "B", "C"])
    orchestrator.validator.validate = MagicMock(return_value=ValidationResult(ok=True, issues=[]))
    orchestrator.generator.generate = MagicMock(return_value=VALID_OUTPUT)
    result = orchestrator.run("テスト入力")
    assert result == VALID_OUTPUT
    assert orchestrator.reader.extract.call_count == 1

def test_retry_once_on_first_validation_failure(orchestrator):
    orchestrator.reader.extract = MagicMock(return_value=["A", "B", "C"])
    orchestrator.validator.validate = MagicMock(side_effect=[
        ValidationResult(ok=False, issues=["state不足"]),
        ValidationResult(ok=True, issues=[])
    ])
    orchestrator.generator.generate = MagicMock(return_value=VALID_OUTPUT)
    result = orchestrator.run("テスト入力")
    assert orchestrator.reader.extract.call_count == 2
    assert result == VALID_OUTPUT

def test_raises_max_retry_error_after_two_failures(orchestrator):
    orchestrator.reader.extract = MagicMock(return_value=["A"])
    orchestrator.validator.validate = MagicMock(return_value=ValidationResult(ok=False, issues=["state不足"]))
    orchestrator.generator.generate = MagicMock(return_value=VALID_OUTPUT)
    with pytest.raises(MaxRetryError):
        orchestrator.run("テスト入力")
    assert orchestrator.reader.extract.call_count == 3

def test_generator_not_called_on_validation_failure(orchestrator):
    orchestrator.reader.extract = MagicMock(return_value=["A"])
    orchestrator.validator.validate = MagicMock(return_value=ValidationResult(ok=False, issues=["state不足"]))
    orchestrator.generator.generate = MagicMock(return_value=VALID_OUTPUT)
    with pytest.raises(MaxRetryError):
        orchestrator.run("テスト入力")
    orchestrator.generator.generate.assert_not_called()

def test_execution_order_is_reader_validator_generator(orchestrator):
    call_order = []
    orchestrator.reader.extract = MagicMock(
        side_effect=lambda x: call_order.append("reader") or ["A", "B", "C"]
    )
    orchestrator.validator.validate = MagicMock(
        side_effect=lambda x: call_order.append("validator") or ValidationResult(ok=True, issues=[])
    )
    orchestrator.generator.generate = MagicMock(
        side_effect=lambda x, y: call_order.append("generator") or VALID_OUTPUT
    )
    orchestrator.run("テスト入力")
    assert call_order == ["reader", "validator", "generator"]
```

**エビデンス保存**
```bash
pytest test/agents/test_orchestrator.py -v > test/evidence/T0-3-4_test_result.txt
```

---

### T0-3-4a：Orchestrator Audit Log テスト

**実装内容** → `src/services/inference/audit_store.py`

**テストコード** → `test/agents/test_orchestrator_audit.py`
```python
import pytest
from datetime import datetime
from unittest.mock import MagicMock
from services.inference.orchestrator import Orchestrator, MaxRetryError
from services.inference.validator import ValidationResult

VALID_OUTPUT = {
    "state": ["来店頻度低下", "価格感度低", "限定感志向"],
    "intent": "再来店動機付け",
    "next_actions": ["限定LINE配信案", "会員限定イベント", "期間限定特典"],
    "confidence": 0.82,
    "trace_id": "audit-test-uuid-001",
    "generated_at": "2026-02-28T00:00:00",
    "rollback_plan": "配信停止→通常施策に戻す",
    "action_bindings": [
        {"action": "LINE配信", "api": "line.broadcast", "dry_run": True}
    ]
}

@pytest.fixture
def orchestrator():
    return Orchestrator()

def test_orchestrator_saves_audit_log(orchestrator):
    orchestrator.reader.extract = MagicMock(return_value=["A", "B", "C"])
    orchestrator.validator.validate = MagicMock(return_value=ValidationResult(ok=True, issues=[]))
    orchestrator.generator.generate = MagicMock(return_value=VALID_OUTPUT)
    result = orchestrator.run("テスト入力")
    audit = orchestrator.audit_store.last()
    assert audit is not None
    assert audit["trace_id"] == result["trace_id"]

def test_audit_log_contains_state(orchestrator):
    orchestrator.reader.extract = MagicMock(return_value=["A", "B", "C"])
    orchestrator.validator.validate = MagicMock(return_value=ValidationResult(ok=True, issues=[]))
    orchestrator.generator.generate = MagicMock(return_value=VALID_OUTPUT)
    orchestrator.run("テスト入力")
    assert "state" in orchestrator.audit_store.last()

def test_audit_log_contains_input_text(orchestrator):
    orchestrator.reader.extract = MagicMock(return_value=["A", "B", "C"])
    orchestrator.validator.validate = MagicMock(return_value=ValidationResult(ok=True, issues=[]))
    orchestrator.generator.generate = MagicMock(return_value=VALID_OUTPUT)
    orchestrator.run("テスト入力")
    assert orchestrator.audit_store.last()["input_text"] == "テスト入力"

def test_audit_log_contains_timestamp(orchestrator):
    orchestrator.reader.extract = MagicMock(return_value=["A", "B", "C"])
    orchestrator.validator.validate = MagicMock(return_value=ValidationResult(ok=True, issues=[]))
    orchestrator.generator.generate = MagicMock(return_value=VALID_OUTPUT)
    orchestrator.run("テスト入力")
    audit = orchestrator.audit_store.last()
    assert "timestamp" in audit
    datetime.fromisoformat(audit["timestamp"])

def test_audit_log_saved_on_max_retry_error(orchestrator):
    """失敗時もAuditが残ること＝説明責任の担保"""
    orchestrator.reader.extract = MagicMock(return_value=["A"])
    orchestrator.validator.validate = MagicMock(return_value=ValidationResult(ok=False, issues=["state不足"]))
    orchestrator.generator.generate = MagicMock(return_value=VALID_OUTPUT)
    with pytest.raises(MaxRetryError):
        orchestrator.run("失敗入力")
    audit = orchestrator.audit_store.last()
    assert audit is not None
    assert audit["status"] == "failed"
    assert "error" in audit
```

**エビデンス保存**
```bash
pytest test/agents/test_orchestrator_audit.py -v > test/evidence/T0-3-4a_test_result.txt
```

---

## T0-4｜デモUI整備

### T0-4-1：プリセット入力の実装

**実装内容** → `src/contracts/presets.json`

**テストコード** → `test/contracts/test_presets.py`
```python
import json
import pytest
from pathlib import Path

PRESETS_PATH = Path(__file__).parent.parent.parent / "src/contracts/presets.json"

def test_presets_file_exists():
    assert PRESETS_PATH.exists()

def test_presets_has_at_least_one_entry():
    presets = json.loads(PRESETS_PATH.read_text())
    assert len(presets) >= 1

def test_each_preset_has_label_and_text():
    presets = json.loads(PRESETS_PATH.read_text())
    for p in presets:
        assert "label" in p
        assert "text" in p
        assert len(p["text"]) > 0

def test_preset_text_is_not_empty_string():
    presets = json.loads(PRESETS_PATH.read_text())
    for p in presets:
        assert p["text"].strip() != ""
```

**エビデンス保存**
```bash
pytest test/contracts/test_presets.py -v > test/evidence/T0-4-1_test_result.txt
```

---

## T0-5｜デプロイ確認

### T0-5-1：ヘルスチェックエンドポイントのテスト

**テストコード** → `test/integration/test_health.py`
```python
import pytest
import requests
import os

BASE_URL = os.environ.get("DEMO_URL", "http://localhost:8080")

def test_health_endpoint_returns_200():
    resp = requests.get(f"{BASE_URL}/health")
    assert resp.status_code == 200

def test_health_response_has_status_ok():
    resp = requests.get(f"{BASE_URL}/health")
    assert resp.json().get("status") == "ok"
```

**エビデンス保存**
```bash
pytest test/integration/test_health.py -v > test/evidence/T0-5-1_test_result.txt
```

---

### T0-5-2：/convert エンドポイントの E2E テスト

**テストコード** → `test/integration/test_convert_e2e.py`
```python
import pytest
import requests
import json
import jsonschema
import os
from pathlib import Path

BASE_URL = os.environ.get("DEMO_URL", "http://localhost:8080")
SCHEMA_PATH = Path(__file__).parent.parent.parent / "src/contracts/state_intent.schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text())

PRESET_INPUT = "最近来店が減っている。値引きには反応しないが、限定感には反応する。"

def test_convert_returns_200():
    resp = requests.post(f"{BASE_URL}/convert", json={"text": PRESET_INPUT})
    assert resp.status_code == 200

def test_convert_output_passes_schema():
    resp = requests.post(f"{BASE_URL}/convert", json={"text": PRESET_INPUT})
    jsonschema.validate(resp.json(), SCHEMA)

def test_convert_state_has_three_or_more_items():
    resp = requests.post(f"{BASE_URL}/convert", json={"text": PRESET_INPUT})
    assert len(resp.json()["state"]) >= 3

def test_convert_output_has_trace_id():
    resp = requests.post(f"{BASE_URL}/convert", json={"text": PRESET_INPUT})
    assert "trace_id" in resp.json()

def test_convert_output_has_rollback_plan():
    resp = requests.post(f"{BASE_URL}/convert", json={"text": PRESET_INPUT})
    assert "rollback_plan" in resp.json()

def test_convert_output_has_action_bindings():
    resp = requests.post(f"{BASE_URL}/convert", json={"text": PRESET_INPUT})
    body = resp.json()
    assert "action_bindings" in body
    assert len(body["action_bindings"]) >= 1

def test_convert_action_bindings_all_dry_run():
    """Phase 0 制約：全 binding が dry_run=true であること"""
    resp = requests.post(f"{BASE_URL}/convert", json={"text": PRESET_INPUT})
    for binding in resp.json()["action_bindings"]:
        assert binding["dry_run"] is True

def test_convert_empty_input_returns_400():
    resp = requests.post(f"{BASE_URL}/convert", json={"text": ""})
    assert resp.status_code == 400

def test_convert_stable_output_10_times():
    """10回実行して8回以上 schema を通過すること"""
    pass_count = 0
    for _ in range(10):
        resp = requests.post(f"{BASE_URL}/convert", json={"text": PRESET_INPUT})
        try:
            jsonschema.validate(resp.json(), SCHEMA)
            pass_count += 1
        except Exception:
            pass
    assert pass_count >= 8, f"安定率不足: {pass_count}/10"
```

**エビデンス保存**
```bash
pytest test/integration/test_convert_e2e.py -v > test/evidence/T0-5-2_test_result.txt
```

---

## タスク実施順序

```
T0-2-1  src/contracts/state_intent.schema.json 作成
    ↓
T0-3-1  src/services/inference/reader.py 実装
    ↓
T0-3-2  src/services/inference/validator.py 実装
    ↓
T0-3-3  src/services/inference/generator.py 実装
    ↓
T0-3-4  src/services/inference/orchestrator.py 実装
    ↓
T0-3-4a src/services/inference/audit_store.py 実装
    ↓
T0-4-1  src/contracts/presets.json 実装
    ↓
T0-5-1  ヘルスチェック確認（デプロイ後）
    ↓
T0-5-2  /convert E2E テスト（デプロイ後）
```

---

## エビデンス保存ルール

```bash
# 各タスク完了時に実行
pytest test/contracts/test_state_intent_schema.py -v > test/evidence/T0-2-1_test_result.txt
pytest test/agents/test_reader.py             -v > test/evidence/T0-3-1_test_result.txt
pytest test/agents/test_validator.py          -v > test/evidence/T0-3-2_test_result.txt
pytest test/agents/test_generator.py          -v > test/evidence/T0-3-3_test_result.txt
pytest test/agents/test_orchestrator.py       -v > test/evidence/T0-3-4_test_result.txt
pytest test/agents/test_orchestrator_audit.py -v > test/evidence/T0-3-4a_test_result.txt
pytest test/contracts/test_presets.py         -v > test/evidence/T0-4-1_test_result.txt
pytest test/integration/test_health.py        -v > test/evidence/T0-5-1_test_result.txt
pytest test/integration/test_convert_e2e.py   -v > test/evidence/T0-5-2_test_result.txt
```

---

## Phase 0 → Phase 1 接続準備チェックリスト

- [ ] 全テスト PASS、`test/evidence/` にエビデンス保存済み
- [ ] `src/contracts/state_intent.schema.json` に `action_bindings` 定義済み
- [ ] `src/services/inference/audit_store.py` インメモリ実装済み（Phase 1でDB永続化に差し替え）
- [ ] `dry_run: true` が全件強制されている（Phase 1で `false` に切り替えるだけ）
- [ ] `/convert` E2E 安定率 8/10 以上
