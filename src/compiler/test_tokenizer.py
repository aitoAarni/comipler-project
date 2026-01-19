from .tokenizer import tokenizer

def test_empty_input() -> None:
    assert tokenizer() == []

def test_ignore_white_space() -> None:
    assert tokenizer("  \n\t") == []

def test_tokenizes_positive_integers() -> None:
    assert tokenizer("12 34\t56\n78   9") == ["12", "34", "56", "78", "9"]

def test_tokenizes_identifiers() -> None:
    assert tokenizer("if \nwhile _var1 2not_ok .not_ok\nOk_2") == [
        "if", "while", "_var1", "Ok_2"
        ]