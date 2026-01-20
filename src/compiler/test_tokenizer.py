import pytest
from .tokenizer import tokenizer, Token, SourceLocation

def create_tokens(token_type: str, *values) -> list[Token]:
    lis: list[Token] = []
    for value in values:
        location = SourceLocation(0, 0)
        location._testing = True
        lis.append(Token(
            value if type(value) == str else str(value) , token_type, location
        ))
    return lis

def test_empty_input() -> None:
    assert tokenizer() == []

def test_ignore_white_space() -> None:
    assert tokenizer("  \n\t") == []

def test_tokenizes_positive_integers() -> None:
    correct_result = create_tokens(
        "int_literal",
        12, 34, 56, 78, 9
    )
    assert tokenizer("12 34\t56\n78   9") == correct_result

def test_tokenizes_identifiers() -> None:
    correct_results = create_tokens("identifier", "if", "while", "_var1", "Ok_2")
    assert tokenizer("if \nwhile _var1\nOk_2") == correct_results

def test_throws_error_on_invalid_identifiers() -> None:
    with pytest.raises(Exception, match="Invalid syntax. Could not tokenize 2var"):
        tokenizer("2var")
    with pytest.raises(Exception, match="Invalid syntax. Could not tokenize \\.var"):
        tokenizer(".var")