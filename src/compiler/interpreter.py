# src/compiler/interpreter.py
from typing import Any
import compiler.custom_ast as ast
from compiler.tokenizer import tokenizer
from compiler.parser import parse
from compiler.synmbol_table import SymTab

type Value = int | bool | None


def interpret(node: ast.Expression, symbol_table) -> Value:
    match node:
        case ast.Literal():
            return node.value

        case ast.BinaryOp():
            a: Any = interpret(node.left, symbol_table)
            b: Any = interpret(node.right, symbol_table)
            operator = node.op.symbol
            match operator:
                case "+":
                    return a + b
                case "<":
                    return a < b
                case _:
                    raise ...

        case ast.VariableDeclaration():
            identifier: Any = node.identifier.name
            value: Any = interpret(node.initializer, symbol_table)
            symbol_table.add_symbol(identifier, value)
            return value
        
        case ast.Block():
            statements = node.statements
            block_symbol_table = SymTab(symbol_table)
            for statement in statements:
                interpret(statement, block_symbol_table)
            return_value = interpret(node.result_expression, block_symbol_table)
            return return_value

        
        case ast.TernaryOp():
            if interpret(node.cond):
                return interpret(node.then_)
            else:
                return interpret(node.else_)


if __name__ == "__main__":

    code = "{var a = {2 + 3; 2}}"
    tokens = tokenizer(code)
    parsed = parse(tokens)
    symbol_table = SymTab()
    interpreted = interpret(parsed, symbol_table)
    print(f"interpreted value: {interpreted}")
