import pytest
from compiler.type_checker import typecheck
from compiler.parser import parse
from compiler.tokenizer import tokenizer
import compiler.custom_ast as ast
from compiler.utils import create_top_level_type_symbol_table
from compiler.synmbol_table import SymTab
from compiler.types import Int, Bool, Unit

@pytest.fixture
def type_table():
    return create_top_level_type_symbol_table()

def create_ast(text: str) -> ast.Expression:
    tokens = tokenizer(text)
    abstract_syntax_tree = parse(tokens)
    return abstract_syntax_tree



def test_int_check(type_table):
    parsed = create_ast("328")
    assert typecheck(parsed, type_table) == Int