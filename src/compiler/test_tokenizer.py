from .tokenizer import tokenizer

def test_empty_input():
    assert tokenizer() == []