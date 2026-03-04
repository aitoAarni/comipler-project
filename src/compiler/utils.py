import compiler.custom_ast as ast
from compiler.symbol_table import symbol_table_factory, SymTab
import operator as o
from compiler.types import FunType, Int, Bool, Unit, PrimitiveType
from typing import Callable, Any
from compiler.tokenizer import Token


def get_keywords() -> list[str]:
    return ["if", "while", "var"]


def search_last_expression_of_conditional(
        statement: ast.ConditionalStatement) -> ast.Expression | None:
    if isinstance(statement, ast.WhileStatement):
        return statement.body

    elif isinstance(statement, ast.TernaryOp):
        if statement.else_ is None:
            return statement.then_
        return statement.else_
    else:
        return None


def expression_ends_with_block(expression: ast.Expression | None) -> bool:
    while True:
        if issubclass(type(expression), ast.ConditionalStatement):
            assert isinstance(expression, ast.ConditionalStatement)
            expression = search_last_expression_of_conditional(expression)

        elif isinstance(expression, (ast.UnaryOp, ast.BinaryOp)):
            expression = expression.right

        elif isinstance(expression, ast.VariableDeclaration):
            expression = expression.initializer
        elif isinstance(expression, ast.Block):
            return True
        else:
            return False


def create_top_level_variable_symbol_table() -> SymTab[Callable[..., Any]]:
    st = symbol_table_factory("variables")
    st.add_symbol("unary_-", o.inv)
    st.add_symbol("unary_not", o.not_)
    st.add_symbol("+", o.add)
    st.add_symbol("-", o.sub)
    st.add_symbol("*", o.mul)
    st.add_symbol("/", o.truediv)
    st.add_symbol("%", o.mod)
    st.add_symbol("==", o.eq)
    st.add_symbol("!=", o.ne)
    st.add_symbol("<", o.lt)
    st.add_symbol("<=", o.le)
    st.add_symbol(">", o.gt)
    st.add_symbol(">=", o.ge)
    st.add_symbol("and", lambda a, b: a and b)
    st.add_symbol("or", lambda a, b: a or b)
    st.add_symbol("print_int", print)
    st.add_symbol("print_bool", print)
    return st


def create_top_level_type_symbol_table() -> SymTab[FunType]:
    st = symbol_table_factory("types")
    st.add_symbol("unary_-", FunType([Int], Int))
    st.add_symbol("unary_not", FunType([Bool], Bool))
    st.add_symbol("+", FunType([Int, Int], Int))
    st.add_symbol("-", FunType([Int, Int], Int))
    st.add_symbol("*", FunType([Int, Int], Int))
    st.add_symbol("/", FunType([Int, Int], Int))
    st.add_symbol("%", FunType([Int, Int], Int))
    st.add_symbol("<", FunType([Int, Int], Bool))
    st.add_symbol("<=", FunType([Int, Int], Bool))
    st.add_symbol(">", FunType([Int, Int], Bool))
    st.add_symbol(">=", FunType([Int, Int], Bool))
    st.add_symbol("and", FunType([Bool, Bool], Bool))
    st.add_symbol("or", FunType([Bool, Bool], Bool))
    st.add_symbol("print_int", FunType([Int], Unit))
    st.add_symbol("print_bool", FunType([Bool], Unit))
    return st


def convert_boolean_literal(literal: str) -> bool:
    if literal == "true":
        return True
    elif literal == "false":
        return False
    raise Exception(f"Error: expected type boolean literal but got {literal}")

# def 

def convert_token_to_type(identifier: Token) -> PrimitiveType:
    match identifier.text:
        case "Int":
            return Int
        case "Bool":
            return Bool
        case "Unit":
            return Unit
        case _:
            raise ValueError("Error: type must be Int, Book or Unit.")
    


if __name__ == "__main__":
    from compiler.tokenizer import tokenizer
    from compiler.parser import parse

    tokens = "{a = {a} b}"
    parsed = parse(tokenizer(tokens))
    print(parsed)

    print(expression_ends_with_block(parsed))
