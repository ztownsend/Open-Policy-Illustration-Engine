"""Conformance test runner for canonical cases."""

from __future__ import annotations

import platform
import subprocess
import sys
from dataclasses import dataclass
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from opie import run_illustration
from opie.conformance.compare import ComparisonResult, compare_payloads
from opie.core.ledger import dumps_json
from opie.core.types import IllustrationRequest
from opie.core.versioning import CALC_VERSION, ROUNDING_POLICY_ID, SCHEMA_VERSION


@dataclass(frozen=True)
class EnvironmentMetadata:
    calc_version: str
    schema_version: str
    rounding_policy_id: str
    python_version: str
    platform: str
    timestamp: str
    git_sha: str | None
    git_dirty: bool | None


def _gather_environment() -> EnvironmentMetadata:
    git_sha: str | None = None
    git_dirty: bool | None = None
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if sha.returncode == 0:
            git_sha = sha.stdout.strip()
        dirty = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if dirty.returncode == 0:
            git_dirty = len(dirty.stdout.strip()) > 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return EnvironmentMetadata(
        calc_version=CALC_VERSION,
        schema_version=SCHEMA_VERSION,
        rounding_policy_id=ROUNDING_POLICY_ID,
        python_version=sys.version,
        platform=platform.platform(),
        timestamp=datetime.now(timezone.utc).isoformat(),
        git_sha=git_sha,
        git_dirty=git_dirty,
    )


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
class DiffPointer:
    case: str
    scenario: str
    expected_path: str
    first_diff: str | None


@dataclass(frozen=True)
class ConformanceSummary:
    passed: bool
    total_cases: int
    failed_cases: int
    diff_pointer: DiffPointer | None


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
    summary: ConformanceSummary
    diff_pointer: DiffPointer | None
    environment: EnvironmentMetadata
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
    env = _gather_environment()
    specs = load_case_specs(manifest_path)
    case_results: list[CaseResult] = []
    first_pointer: DiffPointer | None = None

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
            if not passed and first_pointer is None:
                first_pointer = DiffPointer(
                    case=spec.name,
                    scenario=scenario_name,
                    expected_path=str(expected_path),
                    first_diff=comparison.first_diff if comparison else None,
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
    passed = failed_cases == 0
    summary = ConformanceSummary(
        passed=passed,
        total_cases=len(case_results),
        failed_cases=failed_cases,
        diff_pointer=first_pointer,
    )
    report = ConformanceReport(
        passed=passed,
        total_cases=len(case_results),
        failed_cases=failed_cases,
        summary=summary,
        diff_pointer=first_pointer,
        environment=env,
        cases=case_results,
    )
    return report
