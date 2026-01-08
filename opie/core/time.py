"""Time indexing utilities for monthly projections."""

from __future__ import annotations


def policy_year_for_month(t: int) -> int:
    return (t - 1) // 12 + 1


def attained_age_for_month(issue_age: int, t: int) -> int:
    return issue_age + (t - 1) // 12
