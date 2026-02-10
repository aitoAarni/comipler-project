from compiler.tokenizer import Token
from compiler.tokenizer import tokenizer
import compiler.custom_ast as ast
from collections.abc import Callable
from compiler.utils import get_keywords


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
            raise Exception(f"{token.location}: expected one of: {comma_separated}")
        self.pos += 1
        return token

    def parse_int_literal(self) -> ast.Literal:
        if self.peek().type != "int_literal":
            raise Exception(f"{self.peek().location}: expected an integer literal")
        token = self.consume()
        return ast.Literal(int(token.text))

    def parse_identifier(self) -> ast.Identifier | ast.Expression:
        if self.peek().type != "identifier":
            raise Exception(
                f"{self.peek().location}: expected an identifier (variable)"
            )
        elif self.peek().text in get_keywords():
            return self.parse_keyword()
        token = self.consume()
        identifier = ast.Identifier(token.text)
        if self.peek().text == "(":
            return self.parse_function_call(identifier)
        return identifier

    def parse_function_call(self, identifier: ast.Identifier) -> ast.FunctionCall:
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
        return ast.FunctionCall(identifier, args if args else None)

    def parse_expression(self, allow_var_declaration: bool = False) -> ast.Expression:
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
            operator = ast.Operator(operator_token.text)
            if left_associative:
                right_operand = next_func()
            else:
                right_operand = self.parse_expression()
            left_operand = ast.BinaryOp(left_operand, operator, right_operand)
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
        return self.parse_binary_operator(["<", "<=", ">", ">="], self.parse_level_6)

    def parse_level_6(self) -> ast.Expression:
        return self.parse_binary_operator(["+", "-"], self.parse_level_7)

    def parse_level_7(self) -> ast.Expression:
        return self.parse_binary_operator(["*", "/", "%"], self.parse_level_8)

    def parse_level_8(self) -> ast.Expression:
        if self.peek().text in ["not", "-"]:
            operator_token = self.consume(["not", "-"])
            operator = ast.Operator(operator_token.text)
            right = self.parse_level_8()
            return ast.UnaryOp(operator, right)
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

    def parse_keyword(self):
        if self.peek().text == "if":
            parse
            return self.parse_if_statement()
        elif self.peek().text == "while":
            return self.parse_while_statement()
        elif self.peek().text == "var":
            return self.parse_var_declaration()
        else:
            raise Exception(f"Keyowrd {self.peek().text} is not handled in parser")

    def parse_if_statement(self) -> ast.TernaryOp:
        self.consume("if")
        if_ = self.parse_expression()
        self.consume("then")
        then_ = self.parse_expression()
        else_ = None
        if self.peek().text == "else":
            self.consume("else")
            else_ = self.parse_expression()
        return ast.TernaryOp(if_, then_, else_)

    def parse_while_statement(self) -> ast.WhileStatement:
        self.consume("while")
        cond = self.parse_expression()
        self.consume("do")
        body = self.parse_expression()
        return ast.WhileStatement(cond, body)

    def parse_var_declaration(self) -> ast.VariableDeclaration:
        if not self.allow_var_declaration:
            raise Exception(
                'Error "var" is only allowed directy inside blocks {} and '
                "in top-level expressions"
            )
        self.consume("var")
        identifier = self.parse_identifier()
        if type(identifier) != ast.Identifier:
            raise Exception(f"Variable must be of type identifier")
        self.consume("=")
        initializer = self.parse_expression()
        return ast.VariableDeclaration(identifier, initializer)

    def parse_parenthesized(self) -> ast.Expression:
        self.consume("(")
        expr = self.parse_expression()
        self.consume(")")
        return expr

    def parse_block(self) -> ast.Block:
        self.consume("{")
        statements: list[ast.Expression] = []
        result_expression = None
        while self.peek().text != "}":
            statement = self.parse_expression(True)
            next_token = self.peek().text
            if next_token == "}":
                result_expression = statement
                break
            else:
                statements.append(statement)
                self.consume(";")

        self.consume("}")
        return ast.Block(
            statements, result_expression if result_expression else ast.Literal(None)
        )

    def parse(self):
        if not bool(self.tokens):
            return None
        expression = self.parse_expression(True)
        if self.pos != self.token_length:
            loc = self.peek().location
            raise Exception(
                f"Invalid syntax at ({loc.line}, {loc.column}), token: {self.peek().text}"
            )
        return expression


def parse(tokens: list[Token]) -> ast.Expression:
    parser = Parser(tokens)
    return parser.parse()


def check_is_identifier(expression: ast.Expression, Error_msg=None) -> None:
    if Error_msg == None:
        Error_msg = "Expected an Identifier"
    if type(expression) != ast.Identifier:
        raise Exception(Error_msg)


if __name__ == "__main__":
    tokens = tokenizer(
        """var a = 2
                """
    )
    parsed = parse(tokens)
    print(parsed)
