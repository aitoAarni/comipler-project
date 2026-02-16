import pytest
from collections.abc import Sequence
from compiler.tokenizer import Token, Location
from compiler.parser import parse
import compiler.custom_ast as ast
from compiler.utils import get_keywords
from compiler.tokenizer import tokenizer

t = ["int_literal", "identifier", "punctuation", "operator"]
loc_stub = Location(None, None)
loc_stub._testing = True


def create_tokens(*token_args: Sequence[str | int]) -> list[Token]:
    tokens = []
    for args in token_args:
        token = Token(str(args[0]), args[1], Location(0, 0))
        token.location._testing = True
        tokens.append(token)
    return tokens


def Literal(*args):
    return ast.Literal(loc_stub, *args)


def Identifier(*args):
    return ast.Identifier(loc_stub, *args)


def Operator(*args):
    return ast.Operator(loc_stub, *args)


def Punctuation(*args):
    return ast.Punctuation(loc_stub, *args)


def FunctionCall(*args, **kwargs):
    return ast.FunctionCall(loc_stub, *args, **kwargs)


def UnaryOp(*args):
    return ast.UnaryOp(loc_stub, *args)


def BinaryOp(*args):
    return ast.BinaryOp(loc_stub, *args)


def TernaryOp(*args):
    return ast.TernaryOp(loc_stub, *args)


def WhileStatement(*args):
    return ast.WhileStatement(loc_stub, *args)


def Block(*args):
    return ast.Block(loc_stub, *args)


def VariableDeclaration(*args):
    return ast.VariableDeclaration(loc_stub, *args)


def test_parse_plus_operation():
    one = Literal(1)
    expression = BinaryOp(one, Operator("+"), one)
    tokens = create_tokens([1, t[0]], ["+", t[3]], [1, t[0]])

    print(tokens)
    parsed = parse(tokens)
    assert parsed == expression


def test_operators_work_with_variables():
    a = Identifier("a")
    correct_expression = BinaryOp(a, Operator("+"), a)
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
    a = Identifier("a")
    tokens = create_tokens(
        ["a", t[1]], ["+", t[3]], ["a", t[1]], ["*", t[3]], [2, t[0]]
    )
    correct_expresion = BinaryOp(
        a, Operator("+"), BinaryOp(a, Operator("*"), Literal(2))
    )
    parsed = parse(tokens)
    assert parsed == correct_expresion


def test_parse_with_parenthesis():
    a = Identifier("a")
    tokens = create_tokens(
        ["(", t[2]],
        ["a", t[1]],
        ["+", t[3]],
        ["a", t[1]],
        [")", t[2]],
        ["*", t[3]],
        [2, t[0]],
    )
    correct_expresion = BinaryOp(
        BinaryOp(a, Operator("+"), a), Operator("*"), Literal(2)
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
        match=r"\(0, 0\):" r" expected \"\(\", an integer literal or an identifier",
    ):
        print(parse(tokens))


def test_ternary_operator():
    two = Literal(2)
    three = Literal(3)
    right_answer = TernaryOp(two, three, None)
    tokens = create_tokens(["if", t[1]], [2, t[0]], ["then", t[1]], [3, t[0]])
    parsed = parse(tokens)
    assert parsed == right_answer


def test_ternary_operator_with_else():
    if_ = Literal(1)
    then_ = Literal(2)
    else_ = Literal(3)

    right_answer = TernaryOp(if_, then_, else_)
    tokens = create_tokens(
        ["if", t[1]], [1, t[0]], ["then", t[1]], [2, t[0]], ["else", t[1]], [3, t[0]]
    )
    parsed = parse(tokens)
    assert parsed == right_answer


def test_ternary_operator_expressions():
    expr1 = BinaryOp(Literal(2), Operator("-"), Identifier("a"))
    expr2 = BinaryOp(Literal(3), Operator("+"), Literal(4))
    expr3 = Identifier("b")
    correct_answer = BinaryOp(Literal(2), Operator("*"), TernaryOp(expr1, expr2, expr3))

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
    ternary_expr = TernaryOp(Identifier("a"), Literal(1), Literal(2))
    correct_answer = TernaryOp(Identifier("a"), ternary_expr, Literal(1))
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
    correct_answer = FunctionCall(Identifier("f"), [Literal(1)])
    tokens = create_tokens(["f", t[1]], ["(", t[2]], [1, t[0]], [")", t[2]])
    parsed = parse(tokens)
    assert parsed == correct_answer


def test_function_call_multiple_args():

    correct_answer = FunctionCall(
        Identifier("f"),
        [
            BinaryOp(Literal(1), Operator("/"), Identifier("b")),
            Literal(2),
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
        match=r'\(0, 0\): expected "\(", an integer literal or an identifier',
    ):
        parse(tokens)

    tokens2 = create_tokens(["f", t[1]], ["(", t[2]], [1, t[0]])
    with pytest.raises(Exception, match=r'\(0, 0\): expected "\)"'):
        parse(tokens2)


def test_remainder_operator():
    correct_answer = BinaryOp(Literal(1), Operator("%"), Identifier("a"))

    tokens = create_tokens(["1", t[0]], ["%", t[3]], ["a", t[1]])
    parsed = parse(tokens)
    assert parsed == correct_answer


def test_equal_operator():
    correct_answer = BinaryOp(Literal(1), Operator("=="), Literal(1))
    tokens = create_tokens(["1", t[0]], ["==", t[3]], [1, t[0]])
    parsed = parse(tokens)
    assert parsed == correct_answer


def test_not_equal_operator():
    correct_answer = BinaryOp(Literal(1), Operator("!="), Literal(1))
    tokens = create_tokens(["1", t[0]], ["!=", t[3]], [1, t[0]])
    parsed = parse(tokens)
    assert parsed == correct_answer


def test_less_than_operator():
    correct_answer = BinaryOp(Literal(1), Operator("<"), Literal(1))
    tokens = create_tokens(["1", t[0]], ["<", t[3]], [1, t[0]])
    parsed = parse(tokens)
    assert parsed == correct_answer


def test_less_than_or_equal_operator():
    correct_answer = BinaryOp(Literal(1), Operator("<="), Literal(1))
    tokens = create_tokens(["1", t[0]], ["<=", t[3]], [1, t[0]])
    parsed = parse(tokens)
    assert parsed == correct_answer


def test_greater_than_operator():
    correct_answer = BinaryOp(Literal(1), Operator(">"), Literal(1))
    tokens = create_tokens(["1", t[0]], [">", t[3]], [1, t[0]])
    parsed = parse(tokens)
    assert parsed == correct_answer


def test_greater_than_or_equal_operator():
    correct_answer = BinaryOp(Literal(1), Operator(">="), Literal(1))
    tokens = create_tokens(["1", t[0]], [">=", t[3]], [1, t[0]])
    parsed = parse(tokens)
    assert parsed == correct_answer


def test_and_operator():
    correct_answer = BinaryOp(Literal(1), Operator("and"), Literal(1))
    tokens = create_tokens(["1", t[0]], ["and", t[3]], [1, t[0]])
    parsed = parse(tokens)
    assert parsed == correct_answer


def test_or_operator():
    correct_answer = BinaryOp(Literal(1), Operator("or"), Literal(1))
    tokens = create_tokens(["1", t[0]], ["or", t[3]], [1, t[0]])
    parsed = parse(tokens)
    assert parsed == correct_answer


def test_not_operator():
    correct_answer = UnaryOp(Operator("not"), UnaryOp(Operator("not"), Literal(1)))
    tokens = create_tokens(["not", t[3]], ["not", t[3]], [1, t[0]])
    parsed = parse(tokens)
    assert parsed == correct_answer


def test_unary_minus_operator():
    correct_answer = UnaryOp(Operator("-"), UnaryOp(Operator("-"), Literal(1)))
    tokens = create_tokens(["-", t[3]], ["-", t[3]], [1, t[0]])
    parsed = parse(tokens)
    assert parsed == correct_answer


def test_ast_structure():
    correct_answer = BinaryOp(
        BinaryOp(Identifier("a"), Operator("-"), Identifier("b")),
        Operator("+"),
        BinaryOp(Identifier("c"), Operator("*"), Identifier("d")),
    )
    tokens = create_tokens(
        ["a", t[1]],
        ["-", t[3]],
        ["b", t[1]],
        ["+", t[3]],
        ["c", t[1]],
        ["*", t[3]],
        ["d", t[1]],
    )
    parsed = parse(tokens)
    assert parsed == correct_answer


def test_assignment_operator():
    correct_answer = BinaryOp(
        Identifier("a"),
        Operator("="),
        BinaryOp(Identifier("b"), Operator("="), Identifier("c")),
    )
    tokens = create_tokens(
        ["a", t[1]], ["=", t[3]], ["b", t[1]], ["=", t[3]], ["c", t[1]]
    )
    parsed = parse(tokens)
    assert parsed == correct_answer


def test_assignment_only_to_identifier():
    tokens = create_tokens([3, t[0]], ["=", t[3]], [3, t[0]])
    with pytest.raises(
        Exception,
        match="Left operand of assignment operator '=' needs to be an Identifier",
    ):
        parse(tokens)


def test_while_do_statment():
    correct_answer = WhileStatement(
        Identifier("x"), FunctionCall(Identifier("print"), args=None)
    )
    tokens = create_tokens(
        ["while", t[1]],
        ["x", t[1]],
        ["do", t[1]],
        ["print", t[1]],
        ["(", t[2]],
        [")", t[2]],
    )

    parsed = parse(tokens)
    assert parsed == correct_answer


def test_parse_simple_block():
    correct_answer = Block([Identifier("a")], Literal(None))
    tokens = create_tokens(["{", t[2]], ["a", t[1]], [";", t[2]], ["}", t[2]])
    parsed = parse(tokens)
    assert parsed == correct_answer


def test_parse_multiple_expressions_block():
    correct_answer = Block(
        [
            Identifier("a"),
            BinaryOp(Identifier("a"), Operator("="), Literal(2)),
        ]
    )
    tokens = create_tokens(
        ["{", t[2]],
        ["a", t[1]],
        [";", t[2]],
        ["a", t[1]],
        ["=", t[3]],
        ["2", t[0]],
        [";", t[2]],
        ["}", t[2]],
    )
    parsed = parse(tokens)
    assert parsed == correct_answer


def test_parse_block_with_result_expression_block():
    correct_answer = Block(
        [
            Identifier("a"),
        ],
        BinaryOp(Identifier("a"), Operator("="), Literal(2)),
    )
    tokens = create_tokens(
        ["{", t[2]],
        ["a", t[1]],
        [";", t[2]],
        ["a", t[1]],
        ["=", t[3]],
        ["2", t[0]],
        ["}", t[2]],
    )
    parsed = parse(tokens)
    assert parsed == correct_answer


def test_block_works_with_assignment():

    correct_answer = BinaryOp(
        Identifier("b"),
        Operator("="),
        Block(
            [
                Identifier("a"),
            ],
            BinaryOp(Identifier("a"), Operator("="), Literal(2)),
        ),
    )
    tokens = create_tokens(
        ["b", t[1]],
        ["=", t[3]],
        ["{", t[2]],
        ["a", t[1]],
        [";", t[2]],
        ["a", t[1]],
        ["=", t[3]],
        ["2", t[0]],
        ["}", t[2]],
    )
    parsed = parse(tokens)
    assert parsed == correct_answer


def test_block_where_missin_semicolon():

    tokens = create_tokens(
        ["{", t[2]],
        ["a", t[1]],
        ["a", t[1]],
        ["=", t[3]],
        ["2", t[0]],
        [";", t[2]],
        ["}", t[2]],
    )
    with pytest.raises(Exception, match=r"\(0, 0\): expected \";\""):
        parse(tokens)


def test_parse_var():
    correct_answer = VariableDeclaration(Identifier("x"), Literal(1))
    tokens = create_tokens(["var", t[1]], ["x", t[1]], ["=", t[3]], ["1", t[0]])
    parsed = parse(tokens)
    assert parsed == correct_answer


def test_keyword_as_var_throws():
    for keyword in get_keywords():
        if keyword == "var":
            continue
        tokens = create_tokens(["var", t[1]], [keyword, t[1]], ["=", t[3]], ["1", t[0]])
        with pytest.raises(
            Exception,
            match=r"\(0, 0\): expected \"\(\", an integer literal or an identifier",
        ):
            parse(tokens)


def test_function_as_var_throws():
    tokens = create_tokens(
        ["var", t[1]], ["f", t[1]], ["(", t[2]], [")", t[2]], ["=", t[3]], ["1", t[0]]
    )
    with pytest.raises(Exception, match="Variable must be of type identifier"):
        parse(tokens)


def test_declare_var_inside_block():
    correct_answer = TernaryOp(
        Literal(1),
        Block([], VariableDeclaration(Identifier("x"), Literal(1))),
    )
    tokens = create_tokens(
        ["if", t[1]],
        ["1", t[0]],
        ["then", t[1]],
        ["{", t[2]],
        ["var", t[1]],
        ["x", t[1]],
        ["=", t[3]],
        ["1", t[0]],
        ["}", t[2]],
    )
    parsed = parse(tokens)
    assert parsed == correct_answer


def test_allow_var_declaration_in_block_or_top_level():

    tokens = create_tokens(
        ["if", t[1]],
        ["1", t[0]],
        ["then", t[1]],
        ["var", t[1]],
        ["x", t[1]],
        ["=", t[3]],
        ["1", t[0]],
    )
    with pytest.raises(
        Exception,
        match='Error "var" is only allowed directy inside blocks {} and '
        "in top-level expressions",
    ):
        parse(tokens)


def test_code_block_without_semicolon():
    correct_answer = Block([Block([], Identifier("a"))], Block([], Identifier("b")))
    tokens = tokenizer("{ { a } { b } }")
    parsed = parse(tokens)
    assert parsed == correct_answer


def test_nested_blocks():
    correct_answer = Block(
        [Block([], Identifier("a")), Block([], Identifier("b"))],
        Literal(None),
    )
    tokens = tokenizer("{ { a } { b }; }")
    parsed = parse(tokens)
    assert parsed == correct_answer


def test_nested_blocks_with_ternary_operator():
    correct_answer = Block(
        [
            TernaryOp(
                Literal(True),
                Block([], Identifier("a")),
                Block([], Identifier("b")),
            )
        ],
        Identifier("c"),
    )
    tokens = tokenizer("{ if true then { a } else { b } c }")
    parsed = parse(tokens)
    assert parsed == correct_answer


def test_missing_semicolons_in_blocks_throws():
    tokens = tokenizer("{ if true then { a } b c }")
    with pytest.raises(Exception, match=r"\(1, 24\): expected \";\""):
        parse(tokens)

# def test_multiple_top_level_expressions():
#     correct_answer = Block([Identifier("a"), Identifier("b")], Identifier("c"))
#     tokens = tokenizer("a; b; c")
#     parsed = parse(tokens)
#     assert parsed == correct_answer

