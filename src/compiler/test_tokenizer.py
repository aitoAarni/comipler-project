from .tokenizer import tokenizer

def test_empty_input() -> None:
    assert tokenizer() == []