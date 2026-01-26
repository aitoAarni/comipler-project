import pytest
from compiler.tokenizer import Token, SourceLocation
from compiler.parser import parse 
import compiler.custom_ast as ast


def get_tokens():
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
    expression = ast.BinaryOp(one, "+", one )
    tokens = get_tokens()
    parsed = parse(tokens)
    assert parsed == expression