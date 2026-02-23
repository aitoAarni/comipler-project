import pytest
from compiler.type_checker import typecheck
from compiler.parser import parse
from compiler.tokenizer import tokenizer
import compiler.custom_ast as ast
from compiler.utils import create_top_level_type_symbol_table
from compiler.symbol_table import SymTab
from compiler.types import Int, Bool, Unit

@pytest.fixture
def type_table() -> SymTab:
    return create_top_level_type_symbol_table()

def create_ast(text: str) -> ast.Expression:
    tokens = tokenizer(text)
    abstract_syntax_tree = parse(tokens)
    return abstract_syntax_tree



def test_int_type(type_table: SymTab):
    parsed = create_ast("328")
    assert typecheck(parsed, type_table) == Int

def test_bool_type(type_table: SymTab):
    parsed = create_ast("false")
    assert typecheck(parsed, type_table) == Bool

def test_variable_declaration(type_table: SymTab):
    parsed = create_ast("var x = 4")
    typecheck(parsed, type_table)
    assert type_table.get_symbol("x") == Int

def test_block_statement_type(type_table: SymTab):
    parsed = create_ast("32; {32; true}")
    assert typecheck(parsed, type_table) == Bool

def test_variable_type(type_table: SymTab):
    parsed = create_ast("var x = false; 2; x")
    assert typecheck(parsed, type_table) == Bool

def test_assignmnent_type(type_table: SymTab):
    parsed = create_ast("var x = 3; x = 45")
    assert typecheck(parsed, type_table) == Unit

def test_wrong_scope_throws(type_table: SymTab):
    parsed = create_ast("{var x = 2}; x * 2")
    with pytest.raises(Exception, match="There is no variable 'x' declared"):
        typecheck(parsed, type_table)

def test_nested_variable_works(type_table: SymTab):
    parsed = create_ast("var x = 2; {var b = x; x / 2; {x + b + 2}}")
    assert typecheck(parsed, type_table) == Int

def test_binary_opeartor_types(type_table: SymTab):
    lt = create_ast("(1 < 3) == false")
    assert typecheck(lt, type_table) == Bool

# def test_function_call_type(type_table: SymTab):
#     parsed = create_ast("print_int(2, 3, 4)")
#     assert typecheck(parsed, type_table) == Unit