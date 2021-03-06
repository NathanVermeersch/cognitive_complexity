import ast

from typing import Callable, Tuple

from cognitive_complexity.common_types import AnyFuncdef


def has_recursive_calls(funcdef: AnyFuncdef) -> bool:
    return bool([
        n for n in ast.walk(funcdef)
        if (
            isinstance(n, ast.Call)
            and isinstance(n.func, ast.Name)
            and n.func.id == funcdef.name
        )
    ])


def process_child_nodes(
    node: ast.AST,
    increment_by: int,
    verbose: bool,
    complexity_calculator: Callable,
) -> int:
    child_complexity = 0
    child_nodes = ast.iter_child_nodes(node)

    for node_num, child_node in enumerate(child_nodes):
        if isinstance(node, ast.Try):
            if node_num == 1:
                # add +1 for all try nodes except body
                increment_by += 1
            if node_num:
                child_complexity += max(1, increment_by)
        child_complexity += complexity_calculator(
            child_node,
            increment_by=increment_by,
            verbose=verbose,
        )
    return child_complexity


def process_node_itself(
    node: ast.AST,
    increment_by: int,
) -> Tuple[int, int, bool]:
    control_flow_breakers = (
        ast.If,
        ast.For,
        ast.While,
        ast.IfExp,
    )
    incrementers_nodes = (
        ast.FunctionDef,
        ast.AsyncFunctionDef,
        ast.Lambda,
    )

    if isinstance(node, control_flow_breakers):
        increment_by += 1
        return increment_by, max(1, increment_by), True
    elif isinstance(node, incrementers_nodes):
        increment_by += 1
        return increment_by, 0, True
    elif isinstance(node, ast.BoolOp):
        inner_boolops_amount = len([n for n in ast.walk(node) if isinstance(n, ast.BoolOp)])
        base_complexity = inner_boolops_amount * max(increment_by, 1)
        return increment_by, base_complexity, False
    elif isinstance(node, (ast.Break, ast.Continue)):
        return increment_by, max(1, increment_by), True
    return increment_by, 0, True
