import pytest
from collections.abc import Sequence
from compiler.tokenizer import Token, SourceLocation
from compiler.parser import parse
import compiler.custom_ast as ast

t = ["int_literal", "identifier", "punctuation"]

def create_tokens(*token_args: Sequence[str | int]) -> list[Token]:
    tokens = []
    for args in token_args:
        token = Token(str(args[0]), args[1], SourceLocation(0, 0))
        token.location._testing = True
        tokens.append(token)
    return tokens


def get_tokens() -> list[Token]:
    tokens = [
        Token("1", "int_literal", SourceLocation(0, 0)),
        Token("+", "identifier", SourceLocation(0, 0)),
        Token("1", "int_literal", SourceLocation(0, 0)),
    ]
    for token in tokens:
        token.location._testing = True
    return tokens


def test_parse_plus_operation():
    one = ast.Literal(1)
    expression = ast.BinaryOp(one, "+", one)
    tokens = create_tokens([1, t[0]], ["+", t[1]], [1, t[0]])
    print(tokens)
    parsed = parse(tokens)
    assert parsed == expression


def test_operators_work_with_variables():
    a = ast.Identifier("a")
    correct_expression = ast.BinaryOp(a, "+", a)
    tokens = create_tokens(["a", t[1]], ["+", t[1]], ["a", t[1]])
    parsed = parse(tokens)

    assert parsed == correct_expression


def test_wrong_syntax_throws_error():
    tokens = create_tokens(["a", t[1]], ["+", t[1]], ["a", t[1]], ["a", t[1]])
    tokens[3].location.line = 1
    tokens[3].location.column = 4
    with pytest.raises(Exception, match=rf"Invalid syntax at \(1, 4\)"):
        parse(tokens)


def test_parse_term():
    a = ast.Identifier("a")
    tokens = create_tokens(
        ["a", t[1]], ["+", t[1]], ["a", t[1]], ["*", t[1]], [2, t[0]]
    )
    correct_expresion = ast.BinaryOp(a, "+", ast.BinaryOp(a, "*", ast.Literal(2)))
    parsed = parse(tokens)
    assert parsed == correct_expresion

def test_parse_with_parenthesis():
    a = ast.Identifier("a")
    tokens = create_tokens(
        ["(", t[2]],["a", t[1]], ["+", t[1]], ["a", t[1]], [")", t[2]],
        ["*", t[1]], [2, t[0]] 
    )
    correct_expresion = ast.BinaryOp(ast.BinaryOp(a, "+", a), "*", ast.Literal(2))
    parsed = parse(tokens)
    assert parsed == correct_expresion

def test_empty_input_on_parser():
    parsed = parse([])
    assert parsed == None

def test_invalid_operation():
    tokens = create_tokens([2, t[0]], ["+", t[1]])
    with pytest.raises(Exception, match=
                       r"SourceLocation\(line=0, column=0\):"
                       r" expected \"\(\", an integer literal or an identifier"
                       ):
        print(parse(tokens))