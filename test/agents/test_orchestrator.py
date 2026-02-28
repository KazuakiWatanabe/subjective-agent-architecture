"""OrchestratorのRetry制御と実行順序を検証するテスト。"""

from unittest.mock import MagicMock

import pytest

from services.inference.orchestrator import MaxRetryError, Orchestrator
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
    ],
}


@pytest.fixture
def orchestrator():
    """テスト用Orchestratorインスタンスを返す。"""
    return Orchestrator()


def test_success_on_first_attempt(orchestrator):
    """初回で検証成功した場合に結果を返すことを確認する。"""
    orchestrator.reader.extract = MagicMock(return_value=["A", "B", "C"])
    orchestrator.validator.validate = MagicMock(
        return_value=ValidationResult(ok=True, issues=[])
    )
    orchestrator.generator.generate = MagicMock(return_value=VALID_OUTPUT)

    result = orchestrator.run("テスト入力")

    assert result == VALID_OUTPUT
    assert orchestrator.reader.extract.call_count == 1


def test_retry_once_on_first_validation_failure(orchestrator):
    """初回NG・2回目OKの場合に1回だけ再試行することを確認する。"""
    orchestrator.reader.extract = MagicMock(return_value=["A", "B", "C"])
    orchestrator.validator.validate = MagicMock(
        side_effect=[
            ValidationResult(ok=False, issues=["state不足"]),
            ValidationResult(ok=True, issues=[]),
        ]
    )
    orchestrator.generator.generate = MagicMock(return_value=VALID_OUTPUT)

    result = orchestrator.run("テスト入力")

    assert orchestrator.reader.extract.call_count == 2
    assert result == VALID_OUTPUT


def test_raises_max_retry_error_after_two_failures(orchestrator):
    """検証失敗が続いた場合にMaxRetryErrorを送出することを確認する。"""
    orchestrator.reader.extract = MagicMock(return_value=["A"])
    orchestrator.validator.validate = MagicMock(
        return_value=ValidationResult(ok=False, issues=["state不足"])
    )
    orchestrator.generator.generate = MagicMock(return_value=VALID_OUTPUT)

    with pytest.raises(MaxRetryError):
        orchestrator.run("テスト入力")

    # 初回 + retry 2回 = 合計3回
    assert orchestrator.reader.extract.call_count == 3


def test_generator_not_called_on_validation_failure(orchestrator):
    """Validatorが失敗し続ける場合はGeneratorを呼ばないことを確認する。"""
    orchestrator.reader.extract = MagicMock(return_value=["A"])
    orchestrator.validator.validate = MagicMock(
        return_value=ValidationResult(ok=False, issues=["state不足"])
    )
    orchestrator.generator.generate = MagicMock(return_value=VALID_OUTPUT)

    with pytest.raises(MaxRetryError):
        orchestrator.run("テスト入力")

    orchestrator.generator.generate.assert_not_called()


def test_execution_order_is_reader_validator_generator(orchestrator):
    """処理順序がReader→Validator→Generatorであることを確認する。"""
    call_order: list[str] = []
    orchestrator.reader.extract = MagicMock(
        side_effect=lambda x: call_order.append("reader") or ["A", "B", "C"]
    )
    orchestrator.validator.validate = MagicMock(
        side_effect=lambda x: call_order.append("validator")
        or ValidationResult(ok=True, issues=[])
    )
    orchestrator.generator.generate = MagicMock(
        side_effect=lambda x, y: call_order.append("generator") or VALID_OUTPUT
    )

    orchestrator.run("テスト入力")

    assert call_order == ["reader", "validator", "generator"]
