# src/compiler/interpreter.py
from typing import Any
import compiler.custom_ast as ast
from compiler.tokenizer import tokenizer
from compiler.parser import parse
from compiler.symbol_table import SymTab, symbol_table_factory
from compiler.utils import create_top_level_variable_symbol_table

type Value = int | bool | None


def interpret(node: ast.Expression | None, symbol_table: SymTab) -> Value:
    match node:
        case ast.Literal():
            return node.value
        case ast.UnaryOp():
            a: Any = interpret(node.right, symbol_table)
            symbol_name = "unary_" + node.op.symbol
            operator_function = symbol_table.get_symbol(symbol_name)
            return operator_function(a)
        case ast.BinaryOp():
            a1: Any = interpret(node.left, symbol_table)
            b: Any = interpret(node.right, symbol_table)
            operator = node.op.symbol
            if operator == "=":
                if not isinstance(node.left, ast.Identifier):
                    raise Exception(
                        f"Error: assignment only works with variables, "
                        f"you tried to assign to {node.left}")
                variable = node.left.name
                value1 = interpret(node.right, symbol_table)
                symbol_table.update_symbol(variable, value1)
            else:
                operator_function = symbol_table.get_symbol(node.op.symbol)
                return operator_function(a1, b)

        case ast.TernaryOp():
            if interpret(node.cond, symbol_table):
                return interpret(node.then_, symbol_table)
            else:
                return interpret(node.else_, symbol_table)

        case ast.VariableDeclaration():
            identifier: str = node.identifier.name
            value: Any = interpret(node.initializer, symbol_table)
            symbol_table.add_symbol(identifier, value)

            return value

        case ast.FunctionCall():
            function_name = node.function_name.name
            func = symbol_table.get_symbol(function_name)
            evaluated = []
            for arg in node.args or []:
                value = interpret(arg, symbol_table)
                evaluated.append(value)
            return func(*evaluated)

        case ast.Block():
            statements = node.statements
            block_symbol_table = symbol_table_factory("variables", symbol_table)
            for statement in statements:
                interpret(statement, block_symbol_table)
            return_value = interpret(node.result_expression, block_symbol_table)
            return return_value
    return None


if __name__ == "__main__":

    code = "if 0 then 2+2 else 5 *2"
    tokens = tokenizer(code)
    parsed = parse(tokens)
    symbol_table = create_top_level_variable_symbol_table()
    interpreted = interpret(parsed, symbol_table)
    print(f"interpreted value: {interpreted}")
