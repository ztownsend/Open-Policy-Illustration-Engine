"""Conformance test runner for canonical cases."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from opie import run_illustration
from opie.conformance.compare import ComparisonResult, compare_payloads
from opie.core.ledger import dumps_json
from opie.core.types import IllustrationRequest


@dataclass(frozen=True)
class CaseSpec:
    name: str
    request_path: Path
    expected_current: Path
    expected_guaranteed: Path


@dataclass(frozen=True)
class ScenarioResult:
    scenario: str
    passed: bool
    comparison: ComparisonResult | None


@dataclass(frozen=True)
class CaseResult:
    name: str
    passed: bool
    scenarios: dict[str, ScenarioResult]


@dataclass(frozen=True)
class ConformanceReport:
    passed: bool
    total_cases: int
    failed_cases: int
    cases: list[CaseResult]


def _resolve_path(base: Path, value: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    return (base / candidate).resolve()


def load_case_specs(manifest_path: Path) -> list[CaseSpec]:
    payload = json.loads(manifest_path.read_text())
    cases = payload.get("cases", [])
    base = manifest_path.parent
    specs: list[CaseSpec] = []
    for entry in cases:
        specs.append(
            CaseSpec(
                name=entry["name"],
                request_path=_resolve_path(base, entry["request"]),
                expected_current=_resolve_path(base, entry["expected_current"]),
                expected_guaranteed=_resolve_path(base, entry["expected_guaranteed"]),
            )
        )
    return specs


def _compare_expected(
    actual_payload: dict[str, Any],
    expected_path: Path,
) -> tuple[bool, ComparisonResult | None]:
    expected_text = expected_path.read_text()
    actual_text = dumps_json(actual_payload)
    if actual_text == expected_text:
        return True, None
    expected_payload = json.loads(expected_text)
    actual_payload_norm = json.loads(actual_text)
    comparison = compare_payloads(actual_payload_norm, expected_payload)
    return False, comparison


def run_conformance(manifest_path: Path) -> ConformanceReport:
    specs = load_case_specs(manifest_path)
    case_results: list[CaseResult] = []

    for spec in specs:
        payload = json.loads(spec.request_path.read_text())
        request = IllustrationRequest.model_validate(payload)
        result = run_illustration(request)

        scenarios: dict[str, ScenarioResult] = {}
        for scenario_name, expected_path in (
            ("current", spec.expected_current),
            ("guaranteed", spec.expected_guaranteed),
        ):
            actual_payload = {
                "product_code": result.product_code,
                "scenario": scenario_name,
                "metadata": result.metadata,
                "ledger": result.ledgers[scenario_name],
            }
            passed, comparison = _compare_expected(actual_payload, expected_path)
            scenarios[scenario_name] = ScenarioResult(
                scenario=scenario_name,
                passed=passed,
                comparison=comparison,
            )

        case_passed = all(item.passed for item in scenarios.values())
        case_results.append(
            CaseResult(
                name=spec.name,
                passed=case_passed,
                scenarios=scenarios,
            )
        )

    failed_cases = sum(1 for case in case_results if not case.passed)
    report = ConformanceReport(
        passed=failed_cases == 0,
        total_cases=len(case_results),
        failed_cases=failed_cases,
        cases=case_results,
    )
    return report
