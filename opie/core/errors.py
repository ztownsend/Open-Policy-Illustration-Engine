"""Custom exception types for OPIE."""

from __future__ import annotations

from typing import Any


class OPIEError(Exception):
    def __init__(
        self,
        message: str,
        *,
        product_code: str | None = None,
        scenario: str | None = None,
        t: int | None = None,
        values: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.product_code = product_code
        self.scenario = scenario
        self.t = t
        self.values = values or {}
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        parts = [self.message]
        if self.product_code:
            parts.append(f"product_code={self.product_code}")
        if self.scenario:
            parts.append(f"scenario={self.scenario}")
        if self.t is not None:
            parts.append(f"t={self.t}")
        if self.values:
            parts.append(f"values={self.values}")
        return " | ".join(parts)


class AssumptionError(OPIEError):
    pass


class InvariantViolation(OPIEError):
    pass


class EngineError(OPIEError):
    pass
