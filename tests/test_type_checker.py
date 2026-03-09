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


def create_ast(text: str) -> ast.Module:
    tokens = tokenizer(text)
    abstract_syntax_tree = parse(tokens)
    return abstract_syntax_tree


def test_int_type(type_table: SymTab) -> None:
    parsed = create_ast("328")
    assert typecheck(parsed, type_table)[0] == Int


def test_bool_type(type_table: SymTab) -> None:
    parsed = create_ast("false")
    assert typecheck(parsed, type_table)[0] == Bool


def test_variable_declaration(type_table: SymTab) -> None:
    parsed = create_ast("var x = 4")
    typecheck(parsed, type_table)
    assert type_table.get_symbol("x") == Int


def test_block_statement_type(type_table: SymTab) -> None:
    parsed = create_ast("32; {32; true}")
    assert typecheck(parsed, type_table)[0] == Bool


def test_variable_type(type_table: SymTab) -> None:
    parsed = create_ast("var x = false; 2; x")
    assert typecheck(parsed, type_table)[0] == Bool


def test_assignmnent_type(type_table: SymTab) -> None:
    parsed = create_ast("var x = 3; x = 45")
    assert typecheck(parsed, type_table)[0] == Int


def test_wrong_scope_throws(type_table: SymTab) -> None:
    parsed = create_ast("{var x = 2}; x * 2")
    with pytest.raises(Exception, match="There is no variable 'x' declared"):
        typecheck(parsed, type_table)


def test_nested_variable_works(type_table: SymTab) -> None:
    parsed = create_ast("var x = 2; {var b = x; x / 2; {x + b + 2}}")
    assert typecheck(parsed, type_table)[0] == Int


def test_binary_opeartor_types(type_table: SymTab) -> None:
    lt = create_ast("(1 < 3) == false")
    assert typecheck(lt, type_table)[0] == Bool


def test_function_call_type(type_table: SymTab) -> None:
    parsed = create_ast("print_int(2)")
    assert typecheck(parsed, type_table)[0] == Unit


def test_function_call_throws_w_too_many_args(type_table: SymTab) -> None:
    with pytest.raises(
        Exception,
        match=r"Error: function print_int takes 1 argument\(s\), but 2 were given.",
    ):
        typecheck(create_ast("print_int(2, 2)"), type_table)


def test_function_call_throws_w_wrong_args(type_table: SymTab) -> None:
    with pytest.raises(
        Exception,
        match=r"Error: function print_int expected paremater type Int, but got instead Bool: Literal\(location=\(1, 11\), type=Bool, value=True\).",
    ):
        typecheck(create_ast("print_int(true)"), type_table)


def test_unary_operation_type(type_table: SymTab) -> None:
    parsed = create_ast("-1")
    assert typecheck(parsed, type_table)[0] == Int


def test_unary_operation_throws_w_wrong_type(type_table: SymTab) -> None:
    parsed = create_ast("not 20")
    with pytest.raises(
        Exception,
        match=r"Error: argument to operator not must be of type Bool, but was of type Int",
    ):
        typecheck(parsed, type_table)


def test_ternary_operation_type(type_table: SymTab) -> None:
    parsed = create_ast("if 2 != 4 then 3 else 4")
    assert typecheck(parsed, type_table)[0] == Int


def test_ternary_operation_with_one_branch(type_table: SymTab) -> None:
    parsed = create_ast("if 2 != 4 then false")
    assert typecheck(parsed, type_table)[0] == Bool


def test_ternary_operator_with_1_branch(type_table: SymTab) -> None:
    parsed = create_ast("if 2 != 4 then false")
    assert typecheck(parsed, type_table)[0] == Bool


def test_ternary_opeartor_thorws_with_different_return_types(
        type_table: SymTab) -> None:
    parsed = create_ast("var x = 1; if 2 != 4 then false else x = 3")
    with pytest.raises(
        Exception,
        match=r"Error: If statement's else and then branch return values don't match Bool != Int",
    ):
        typecheck(parsed, type_table)


def test_while_statement_type(type_table: SymTab) -> None:
    parsed = create_ast("while true do {12 % 6}")
    assert typecheck(parsed, type_table)[0] == Int


def test_variable_declarations_with_type(type_table: SymTab) -> None:
    parsed = create_ast("var x : Int = 3; x")
    assert typecheck(parsed, type_table)[0] == Int


def test_wrong_variable_declarations_with_type_throws(
        type_table: SymTab) -> None:
    with pytest.raises(Exception, match="Error: you can only assign type Unit to x, but you tried to assign Int"):
        parsed = create_ast("var x : Unit = 3")
        typecheck(parsed, type_table)


def test_function_variable_declarations_with_type(type_table: SymTab) -> None:
    parsed = create_ast("var x : (Int) => Unit = print_int")
    assert typecheck(parsed, type_table)[0] == Unit


def test_wrong_function_variable_declarations_with_type_throws(
        type_table: SymTab) -> None:
    with pytest.raises(Exception, match=r"Error: you can only assign type "
                       r"FunType\(arg_types=\[Int\], "
                       r"return_type=Int\) to x, but you tried"
                       r" to assign FunType\(arg_types=\[Int\], return_type=Unit\)"
                       ):
        parsed = create_ast("var x : (Int) => Int = print_int;")
        typecheck(parsed, type_table)
