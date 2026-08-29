"""Phase 2 (docs/IMPLEMENTATION_PLAN.md §3.1): the declarative property DSL.

A property spec never contains executable code -- only a reference to a
predefined, reviewed property constructor. This is what lets Evidence
Engine let the host model *select* a property from a catalog without ever
running model-authored code (I8's execution boundary would otherwise be a
direct code-injection path)."""

from __future__ import annotations

import pytest

from app.domain.contracts import PropertySpec
from app.domain.properties import UnknownPropertyError, evaluate_property


def test_output_equals_reference_passes_when_outputs_match() -> None:
    spec = PropertySpec(function="bfs", property="output_equals_reference", oracle="reference_implementation_v1")

    result = evaluate_property(spec, submitted_output=["A", "B", "C"], reference_output=["A", "B", "C"])

    assert result.passed is True


def test_output_equals_reference_fails_when_outputs_diverge() -> None:
    spec = PropertySpec(function="bfs", property="output_equals_reference", oracle="reference_implementation_v1")

    result = evaluate_property(spec, submitted_output=["A", "C", "B"], reference_output=["A", "B", "C"])

    assert result.passed is False
    assert "A" in result.detail or "C" in result.detail or "B" in result.detail


def test_output_is_permutation_passes_when_same_elements_different_order() -> None:
    spec = PropertySpec(function="bfs", property="output_is_permutation", oracle="reference_implementation_v1")

    result = evaluate_property(spec, submitted_output=["C", "A", "B"], reference_output=["A", "B", "C"])

    assert result.passed is True


def test_output_is_permutation_fails_when_elements_differ() -> None:
    spec = PropertySpec(function="bfs", property="output_is_permutation", oracle="reference_implementation_v1")

    result = evaluate_property(spec, submitted_output=["A", "B", "B"], reference_output=["A", "B", "C"])

    assert result.passed is False


def test_unknown_property_name_raises_rather_than_silently_passing() -> None:
    spec = PropertySpec(function="bfs", property="not_a_real_property", oracle="reference_implementation_v1")

    with pytest.raises(UnknownPropertyError):
        evaluate_property(spec, submitted_output=["A"], reference_output=["A"])


def test_property_spec_rejects_empty_function_name() -> None:
    with pytest.raises(ValueError, match="function"):
        PropertySpec(function="", property="output_equals_reference", oracle="reference_implementation_v1")


def test_property_spec_carries_no_executable_code_fields() -> None:
    spec = PropertySpec(function="bfs", property="output_equals_reference", oracle="reference_implementation_v1")

    # The whole point of the DSL: nothing on the spec is ever passed to
    # exec/eval. Every field must be a plain string or list of strings.
    assert isinstance(spec.function, str)
    assert isinstance(spec.property, str)
    assert isinstance(spec.oracle, str)
    assert all(isinstance(arg, str) for arg in spec.arguments)
