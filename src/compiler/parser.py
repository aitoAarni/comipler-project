from compiler.tokenizer import Token
from compiler.tokenizer import tokenizer
import compiler.custom_ast as ast
from compiler.location import Location as Loc
from collections.abc import Callable
from compiler.utils import (
    get_keywords,
    expression_ends_with_block,
    convert_boolean_literal,
    convert_token_to_type
)
from compiler.types import PrimitiveType, FunType, Unit


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.pos = 0
        self.token_length = len(tokens)
        # allow only on top-level or in inside blocks {}
        self.allow_var_declaration = False

    def peek(self) -> Token:
        if self.pos < self.token_length:
            return self.tokens[self.pos]
        else:
            return Token(
                location=self.tokens[-1].location,
                type="end",
                text="",
            )

    def consume(self, expected: str | list[str] | None = None) -> Token:
        self.pos
        token = self.peek()
        if isinstance(expected, str) and token.text != expected:
            raise Exception(f'{token.location}: expected "{expected}"')
        if isinstance(expected, list) and token.text not in expected:
            comma_separated = ", ".join([f'"{e}"' for e in expected])
            raise Exception(
                f"{token.location}: expected one of: {comma_separated}")
        self.pos += 1
        return token

    def parse_int_literal(self) -> ast.Literal:
        if self.peek().type != "int_literal":
            raise Exception(
                f"{self.peek().location}: expected an integer literal")
        token = self.consume()
        return ast.Literal(
            token.location.new(),
            (
                int(token.text)
                if token.text.isnumeric()
                else convert_boolean_literal(token.text)
            ),
        )

    def parse_identifier(self) -> ast.Identifier | ast.Expression:
        if self.peek().type != "identifier":
            raise Exception(
                f"{self.peek().location}: expected an identifier (variable)"
            )
        elif self.peek().text in get_keywords():
            return self.parse_keyword()
        token = self.consume()
        identifier = ast.Identifier(token.location.new(), token.text)
        if self.peek().text == "(":
            return self.parse_function_call(identifier)
        return identifier

    def parse_function_call(
            self,
            identifier: ast.Identifier) -> ast.FunctionCall:
        self.consume("(")
        args: list[ast.Expression] = []
        if self.peek().text != ")":
            while True:
                arg = self.parse_expression()
                args.append(arg)
                if self.peek().text != ",":
                    break
                self.consume(",")
        self.consume(")")
        return ast.FunctionCall(
            None if identifier.location is None else identifier.location.new(),
            identifier,
            args)

    def parse_top_level(self) -> ast.Expression | ast.Block:
        statements = []
        result_expression: ast.Expression = ast.Literal(Loc(), None)
        while self.peek().type != "end" and not (self.peek().text == "fun"):
            expression = self.parse_expression(True)

            if self.peek().type == "end" and not (self.peek().text == "fun"):
                result_expression = expression
                break
            statements.append(expression)
            if not expression_ends_with_block(
                    expression) or self.peek().text == ";":
                self.consume(";")
        if not statements:
            return result_expression
        return ast.Block(
            None if result_expression.location is None else result_expression.location.new(),
            statements,
            result_expression)

    def parse_expression(
            self,
            allow_var_declaration: bool = False) -> ast.Expression:
        initial_state = self.allow_var_declaration
        self.allow_var_declaration = allow_var_declaration
        expression = self.parse_level_1()
        self.allow_var_declaration = initial_state
        return expression

    def parse_binary_operator(
        self,
        operators: list[str],
        next_func: Callable[[], ast.Expression],
        left_associative: bool = True,
        left_operand_check: None | Callable[..., None] = None,
    ) -> ast.Expression:
        left_operand = next_func()
        while self.peek().text in operators:
            if left_operand_check:
                left_operand_check(left_operand)
            operator_token = self.consume(operators)
            operator = ast.Operator(
                operator_token.location.new(),
                operator_token.text)
            if left_associative:
                right_operand = next_func()
            else:
                right_operand = self.parse_expression()
            left_operand = ast.BinaryOp(
                None if operator.location is None else operator.location.new(),
                left_operand,
                operator,
                right_operand)
        return left_operand

    def parse_level_1(self) -> ast.Expression:
        return self.parse_binary_operator(
            ["="],
            self.parse_level_2,
            left_associative=False,
            left_operand_check=lambda left: check_is_identifier(
                left,
                "Left operand of assignment operator '=' needs to be an Identifier",
            ),
        )

    def parse_level_2(self) -> ast.Expression:
        return self.parse_binary_operator(["or"], self.parse_level_3)

    def parse_level_3(self) -> ast.Expression:
        return self.parse_binary_operator(["and"], self.parse_level_4)

    def parse_level_4(self) -> ast.Expression:
        return self.parse_binary_operator(["!=", "=="], self.parse_level_5)

    def parse_level_5(self) -> ast.Expression:
        return self.parse_binary_operator(
            ["<", "<=", ">", ">="], self.parse_level_6)

    def parse_level_6(self) -> ast.Expression:
        return self.parse_binary_operator(["+", "-"], self.parse_level_7)

    def parse_level_7(self) -> ast.Expression:
        return self.parse_binary_operator(["*", "/", "%"], self.parse_level_8)

    def parse_level_8(self) -> ast.Expression:
        if self.peek().text in ["not", "-"]:
            operator_token = self.consume(["not", "-"])
            operator = ast.Operator(
                operator_token.location.new(),
                operator_token.text)
            right = self.parse_level_8()
            return ast.UnaryOp(
                None if operator.location is None else operator.location.new(),
                operator,
                right)
        else:
            return self.parse_level_9()

    def parse_level_9(self) -> ast.Expression:
        if self.peek().text == "(":
            return self.parse_parenthesized()
        elif self.peek().text == "{":
            return self.parse_block()
        elif self.peek().type == "int_literal":
            return self.parse_int_literal()
        elif self.peek().type == "identifier":
            return self.parse_identifier()
        else:
            raise Exception(
                f'{self.peek().location}: expected "(", an integer literal or an identifier'
            )

    def parse_keyword(
            self) -> ast.TernaryOp | ast.WhileStatement | ast.VariableDeclaration | ast.ContinueStatement | ast.BreakStatement:
        if self.peek().text == "if":
            parse
            return self.parse_if_statement()
        elif self.peek().text == "while":
            return self.parse_while_statement()
        elif self.peek().text == "var":
            return self.parse_var_declaration()
        elif self.peek().text == "break":
            return self.parse_break_statement()
        elif self.peek().text == "continue":
            return self.parse_continue_statement()
        else:
            raise Exception(
                f"Keyowrd "
                f"{self.peek().text} is not handled in parser")

    def parse_if_statement(self) -> ast.TernaryOp:
        self.consume("if")
        if_ = self.parse_expression()
        self.consume("then")
        then_ = self.parse_expression()
        else_ = None
        if self.peek().text == "else":
            self.consume("else")
            else_ = self.parse_expression()
        return ast.TernaryOp(
            None if if_.location is None else if_.location.new(),
            if_,
            then_,
            else_)

    def parse_while_statement(self) -> ast.WhileStatement:
        self.consume("while")
        cond = self.parse_expression()
        self.consume("do")
        body = self.parse_expression()
        return ast.WhileStatement(
            None if cond.location is None else cond.location.new(), cond, body)

    def parse_break_statement(self) -> ast.BreakStatement:
        statement = self.consume("break")
        return ast.BreakStatement(statement.location)

    def parse_continue_statement(self) -> ast.ContinueStatement:
        statement = self.consume("continue")
        return ast.ContinueStatement(statement.location)

    def _parse_variable_type(self) -> FunType | PrimitiveType:
        self.consume(":")
        if self.peek().text != "(":
            return convert_token_to_type(self.consume())

        # Must be a function declaration
        self.consume("(")
        function_args: list[PrimitiveType] = []
        while self.peek().text != ")":
            arg_token = self.consume()
            arg_type = convert_token_to_type(arg_token)
            function_args.append(arg_type)
        self.consume(")")
        self.consume("=")
        self.consume(">")
        function_return_token = self.consume()
        function_return_type = convert_token_to_type(function_return_token)
        return FunType(function_args, function_return_type)

    def parse_var_declaration(self) -> ast.VariableDeclaration:
        if not self.allow_var_declaration:
            raise Exception(
                'Error "var" is only allowed directy inside blocks {} and '
                "in top-level expressions"
            )
        self.consume("var")
        identifier = self.parse_identifier()
        if not isinstance(identifier, ast.Identifier):
            raise Exception(f"Variable must be of type identifier")

        var_type: FunType | PrimitiveType | None = None
        if self.peek().text == ":":
            var_type = self._parse_variable_type()

        self.consume("=")
        initializer = self.parse_expression()
        return ast.VariableDeclaration(
            None if identifier.location is None else identifier.location.new(),
            identifier,
            initializer, var_type)

    def parse_parenthesized(self) -> ast.Expression:
        self.consume("(")
        expr = self.parse_expression()
        self.consume(")")
        return expr

    def parse_block(self) -> ast.Block:
        self.consume("{")
        location, statements, result_expression = self.parse_inside_block()
        self.consume("}")
        return ast.Block(location, statements, result_expression)

    def parse_inside_block(self) -> tuple[Loc | None,
                                          list[ast.Expression],
                                          ast.Expression]:
        statements: list[ast.Expression] = []
        result_expression: ast.Expression = ast.Literal(Loc(), None)
        while self.peek().text != "}":
            statement = self.parse_expression(True)
            next_token = self.peek().text
            if next_token == "}":
                result_expression = statement
                break
            elif next_token == "{" and isinstance(statement, ast.Block):
                statements.append(statement)
                self.consume("{")
                nested_block = self.parse_expression(True)
                self.consume("}")
                next_token = self.peek().text
                if next_token != "}":
                    statements.append(
                        ast.Block(
                            None if nested_block.location is None else nested_block.location.new(),
                            [],
                            nested_block))
                    if next_token == ";":
                        self.consume(";")
                else:
                    result_expression = ast.Block(
                        None if nested_block.location is None else nested_block.location.new(),
                        [],
                        nested_block)
            else:
                statements.append(statement)
                if not expression_ends_with_block(
                        statement) or next_token == ";":
                    self.consume(";")
        return None if result_expression.location is None else result_expression.location.new(
        ), statements, result_expression

    def parse_func_definition(self) -> ast.FunctionDefinition:
        self.consume("fun")
        func_name_token = self.consume()
        assert func_name_token.type == "identifier"
        func_name = func_name_token.text
        self.consume("(")
        func_params: list[ast.FunDefArg] = []
        while self.peek().text != ")":
            if func_params:
                self.consume(",")
            arg_name_token = self.consume()
            assert arg_name_token.type == "identifier"
            self.consume(":")
            arg_type_token = self.consume(["Int", "Bool", "Unit"])
            arg_type = convert_token_to_type(arg_type_token)
            func_params.append(ast.FunDefArg(arg_name_token.text, arg_type))

        self.consume(")")
        self.consume(":")
        result_type = convert_token_to_type(
            self.consume(["Int", "Bool", "Unit"]))
        func_body = self.parse_block()
        return ast.FunctionDefinition(
            func_name, func_body, func_params, result_type)

    def parse(self) -> ast.Module:
        if not bool(self.tokens):
            return ast.Module([])
        main_parsed = False
        functions: list[ast.FunctionDefinition] = []
        while self.pos != self.token_length:
            if self.peek().text == "fun":
                function = self.parse_func_definition()
                functions.append(function)
            elif not main_parsed:
                expression = self.parse_top_level()
                main_parsed = True
                functions.append(
                    ast.FunctionDefinition(
                        "main", expression, [], Unit))
            else:
                loc = self.peek().location
                raise Exception(
                    f"Invalid syntax at "
                    f"({loc.line}, {loc.column})"
                    f", token: {self.peek().text}")
        return ast.Module(functions)


def parse(tokens: list[Token]) -> ast.Module:
    parser = Parser(tokens)
    return parser.parse()


def check_is_identifier(
        expression: ast.Expression,
        Error_msg: str = "") -> None:
    if not len(Error_msg):
        Error_msg = "Expected an Identifier"
    if not isinstance(expression, ast.Identifier):
        raise Exception(Error_msg)


if __name__ == "__main__":
    tokens = tokenizer("""
1+1;
fun square(x: Int, b: Bool, c: Unit): Int {
    1+1; 2+2;
}
""")
    parsed = parse(tokens)
    print(parsed)
