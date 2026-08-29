"""AST mutation-operator library (docs/IMPLEMENTATION_PLAN.md §6, Phase 2, R1).

Two generic operator families so far, neither specific to any one
challenge's structure (application code must not branch on
fixture-specific prose, memory/semantic/architecture.md):

- Comparison-operator replacement: swaps a `Compare` node's operator for a
  standard mutation-testing replacement (Eq<->NotEq, Lt<->GtE, Gt<->LtE,
  In<->NotIn, Is<->IsNot).
- Integer-constant boundary mutation: +1/-1 on numeric literals, the
  classic off-by-one bug generator. Skips `bool` (an `int` subclass in
  Python) since `True`/`False` aren't boundary values in this sense.

This is the operator library only. Kill-ratio filtering and
equivalent-mutant tolerance (§6 Phase 2) are not implemented here yet --
callers classify a mutant by running its source through
`app.domain.sandbox.execute_repair` and checking the resulting property
results, same as any submitted repair.
"""

from __future__ import annotations

import ast
import copy
import hashlib
from dataclasses import dataclass

_OPERATOR_MUTATIONS: dict[type[ast.cmpop], type[ast.cmpop]] = {
    ast.Eq: ast.NotEq,
    ast.NotEq: ast.Eq,
    ast.Lt: ast.GtE,
    ast.GtE: ast.Lt,
    ast.Gt: ast.LtE,
    ast.LtE: ast.Gt,
    ast.In: ast.NotIn,
    ast.NotIn: ast.In,
    ast.Is: ast.IsNot,
    ast.IsNot: ast.Is,
}


@dataclass(frozen=True)
class Mutant:
    mutant_id: str
    operator: str
    description: str
    mutated_source: str


def _compare_nodes(tree: ast.AST) -> list[ast.Compare]:
    return [node for node in ast.walk(tree) if isinstance(node, ast.Compare)]


def generate_comparison_mutants(source: str) -> list[Mutant]:
    tree = ast.parse(source)
    original_nodes = _compare_nodes(tree)
    mutants = []

    for node_index, node in enumerate(original_nodes):
        for op_index, op in enumerate(node.ops):
            replacement = _OPERATOR_MUTATIONS.get(type(op))
            if replacement is None:
                continue

            mutant_tree = copy.deepcopy(tree)
            mutant_node = _compare_nodes(mutant_tree)[node_index]
            mutant_node.ops[op_index] = replacement()
            ast.fix_missing_locations(mutant_tree)
            mutated_source = ast.unparse(mutant_tree)

            description = f"{type(op).__name__}->{replacement.__name__} at compare #{node_index}.{op_index}"
            mutant_id = hashlib.sha256(f"comparison_operator_replacement:{description}".encode()).hexdigest()[:16]
            mutants.append(
                Mutant(
                    mutant_id=mutant_id,
                    operator="comparison_operator_replacement",
                    description=description,
                    mutated_source=mutated_source,
                )
            )

    return mutants


def _int_constant_nodes(tree: ast.AST) -> list[ast.Constant]:
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and type(node.value) is int
    ]


def generate_constant_mutants(source: str) -> list[Mutant]:
    tree = ast.parse(source)
    original_nodes = _int_constant_nodes(tree)
    mutants = []

    for node_index, node in enumerate(original_nodes):
        original_value = node.value
        assert type(original_value) is int  # narrows for mypy; _int_constant_nodes already filtered this
        for delta in (1, -1):
            new_value = original_value + delta

            mutant_tree = copy.deepcopy(tree)
            mutant_node = _int_constant_nodes(mutant_tree)[node_index]
            mutant_node.value = new_value
            ast.fix_missing_locations(mutant_tree)
            mutated_source = ast.unparse(mutant_tree)

            description = f"{original_value}->{new_value} at constant #{node_index}"
            mutant_id = hashlib.sha256(f"integer_constant_boundary:{description}".encode()).hexdigest()[:16]
            mutants.append(
                Mutant(
                    mutant_id=mutant_id,
                    operator="integer_constant_boundary",
                    description=description,
                    mutated_source=mutated_source,
                )
            )

    return mutants
