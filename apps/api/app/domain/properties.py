"""The property DSL's evaluator catalog (docs/IMPLEMENTATION_PLAN.md §3.1).

Each entry is a predefined, reviewed comparison between a submitted
repair's output and a reference (oracle) implementation's output on the
same input. The host model may only *select* a property by name from this
catalog -- it never supplies executable comparison logic. Adding a new
property means adding a new reviewed function here, not accepting one
from a tool call.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from app.domain.contracts import PropertyCheckResult, PropertySpec


class UnknownPropertyError(ValueError):
    def __init__(self, property_name: str) -> None:
        super().__init__(f"Unknown property: {property_name!r}")
        self.property_name = property_name


def _output_equals_reference(submitted_output: Any, reference_output: Any) -> PropertyCheckResult:
    passed = submitted_output == reference_output
    detail = (
        "submitted output matches the reference implementation"
        if passed
        else f"expected {reference_output!r}, got {submitted_output!r}"
    )
    return PropertyCheckResult(passed=passed, detail=detail)


def _output_is_permutation(submitted_output: Any, reference_output: Any) -> PropertyCheckResult:
    try:
        submitted_sorted = sorted(submitted_output)
        reference_sorted = sorted(reference_output)
    except TypeError:
        return PropertyCheckResult(passed=False, detail="output is not a sortable sequence")
    passed = submitted_sorted == reference_sorted
    detail = (
        "submitted output is a permutation of the reference output"
        if passed
        else f"expected a permutation of {reference_output!r}, got {submitted_output!r}"
    )
    return PropertyCheckResult(passed=passed, detail=detail)


_PROPERTY_CATALOG: dict[str, Callable[[Any, Any], PropertyCheckResult]] = {
    "output_equals_reference": _output_equals_reference,
    "output_is_permutation": _output_is_permutation,
}


def evaluate_property(spec: PropertySpec, *, submitted_output: Any, reference_output: Any) -> PropertyCheckResult:
    evaluator = _PROPERTY_CATALOG.get(spec.property)
    if evaluator is None:
        raise UnknownPropertyError(spec.property)
    return evaluator(submitted_output, reference_output)
