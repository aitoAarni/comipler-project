import pytest
from collections.abc import Sequence
from compiler.tokenizer import Token, SourceLocation
from compiler.parser import parse
import compiler.custom_ast as ast

t = ["int_literal", "identifier", "punctuation", "operator"]


def create_tokens(*token_args: Sequence[str | int]) -> list[Token]:
    tokens = []
    for args in token_args:
        token = Token(str(args[0]), args[1], SourceLocation(0, 0))
        token.location._testing = True
        tokens.append(token)
    return tokens


def test_parse_plus_operation():
    one = ast.Literal(1)
    expression = ast.BinaryOp(one, ast.Operator("+"), one)
    tokens = create_tokens([1, t[0]], ["+", t[3]], [1, t[0]])
    print(tokens)
    parsed = parse(tokens)
    assert parsed == expression


def test_operators_work_with_variables():
    a = ast.Identifier("a")
    correct_expression = ast.BinaryOp(a, ast.Operator("+"), a)
    tokens = create_tokens(["a", t[1]], ["+", t[3]], ["a", t[1]])
    parsed = parse(tokens)

    assert parsed == correct_expression


def test_wrong_syntax_throws_error():
    tokens = create_tokens(["a", t[1]], ["+", t[3]], ["a", t[1]], ["a", t[1]])
    tokens[3].location.line = 1
    tokens[3].location.column = 4
    with pytest.raises(Exception, match=rf"Invalid syntax at \(1, 4\)"):
        parse(tokens)


def test_parse_term():
    a = ast.Identifier("a")
    tokens = create_tokens(
        ["a", t[1]], ["+", t[3]], ["a", t[1]], ["*", t[3]], [2, t[0]]
    )
    correct_expresion = ast.BinaryOp(
        a, ast.Operator("+"), ast.BinaryOp(a, ast.Operator("*"), ast.Literal(2))
    )
    parsed = parse(tokens)
    assert parsed == correct_expresion


def test_parse_with_parenthesis():
    a = ast.Identifier("a")
    tokens = create_tokens(
        ["(", t[2]],
        ["a", t[1]],
        ["+", t[3]],
        ["a", t[1]],
        [")", t[2]],
        ["*", t[3]],
        [2, t[0]],
    )
    correct_expresion = ast.BinaryOp(
        ast.BinaryOp(a, ast.Operator("+"), a), ast.Operator("*"), ast.Literal(2)
    )
    parsed = parse(tokens)
    assert parsed == correct_expresion


def test_empty_input_on_parser():
    parsed = parse([])
    assert parsed == None


def test_invalid_operation():
    tokens = create_tokens([2, t[0]], ["+", t[3]])
    with pytest.raises(
        Exception,
        match=r"SourceLocation\(line=0, column=0\):"
        r" expected \"\(\", an integer literal or an identifier",
    ):
        print(parse(tokens))


def test_ternary_operator():
    two = ast.Literal(2)
    three = ast.Literal(3)
    right_answer = ast.TernaryOp(two, three, None)
    tokens = create_tokens(["if", t[1]], [2, t[0]], ["then", t[1]], [3, t[0]])
    parsed = parse(tokens)
    assert parsed == right_answer


def test_ternary_operator_with_else():
    if_ = ast.Literal(1)
    then_ = ast.Literal(2)
    else_ = ast.Literal(3)

    right_answer = ast.TernaryOp(if_, then_, else_)
    tokens = create_tokens(
        ["if", t[1]], [1, t[0]], ["then", t[1]], [2, t[0]], ["else", t[1]], [3, t[0]]
    )
    parsed = parse(tokens)
    assert parsed == right_answer


def test_ternary_operator_expressions():
    expr1 = ast.BinaryOp(ast.Literal(2), ast.Operator("-"), ast.Identifier("a"))
    expr2 = ast.BinaryOp(ast.Literal(3), ast.Operator("+"), ast.Literal(4))
    expr3 = ast.Identifier("b")
    correct_answer = ast.BinaryOp(
        ast.Literal(2), ast.Operator("*"), ast.TernaryOp(expr1, expr2, expr3)
    )

    tokens = create_tokens(
        [2, t[0]],
        ["*", t[3]],
        ["if", t[1]],
        ["2", t[0]],
        ["-", t[3]],
        ["a", t[1]],
        ["then", t[1]],
        [3, t[0]],
        ["+", t[3]],
        [4, t[0]],
        ["else", t[1]],
        ["b", t[1]],
    )
    parsed = parse(tokens)
    assert parsed == correct_answer


def test_nexted_if_statement():
    ternary_expr = ast.TernaryOp(ast.Identifier("a"), ast.Literal(1), ast.Literal(2))
    correct_answer = ast.TernaryOp(ast.Identifier("a"), ternary_expr, ast.Literal(1))
    tokens = create_tokens(
        ["if", t[1]],
        ["a", t[1]],
        ["then", t[1]],
        ["if", t[1]],
        ["a", t[1]],
        ["then", t[1]],
        [1, t[0]],
        ["else", t[1]],
        [2, t[0]],
        ["else", t[1]],
        [1, t[0]],
    )
    parsed = parse(tokens)
    assert parsed == correct_answer


def test_function_call():
    correct_answer = ast.FunctionCall(ast.Identifier("f"), [ast.Literal(1)])
    tokens = create_tokens(["f", t[1]], ["(", t[2]], [1, t[0]], [")", t[2]])
    parsed = parse(tokens)
    assert parsed == correct_answer


def test_function_call_multiple_args():

    correct_answer = ast.FunctionCall(
        ast.Identifier("f"),
        [
            ast.BinaryOp(ast.Literal(1), ast.Operator("/"), ast.Identifier("b")),
            ast.Literal(2),
        ],
    )
    tokens = create_tokens(
        ["f", t[1]],
        ["(", t[2]],
        [1, t[0]],
        ["/", t[3]],
        ["b", t[1]],
        [",", t[2]],
        [2, t[0]],
        [")", t[2]],
    )
    parsed = parse(tokens)
    assert parsed == correct_answer


def test_invalid_function_syntax():
    tokens = create_tokens(
        ["f", t[1]], ["(", t[2]], [1, t[0]], [",", t[2]], [")", t[2]]
    )
    with pytest.raises(
        Exception,
        match='SourceLocation\\(line=0, column=0\\): expected "\\(", an integer literal or an identifier',
    ):
        parse(tokens)

    tokens2 = create_tokens(["f", t[1]], ["(", t[2]], [1, t[0]])
    with pytest.raises(Exception, match="SourceLocation\\(line=0, column=0\\): expected \"\\)\""):
        parse(tokens2)