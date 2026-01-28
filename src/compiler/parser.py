from compiler.tokenizer import Token
from compiler.tokenizer import tokenizer
import compiler.custom_ast as ast


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.pos = 0
        self.token_length = len(tokens)

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

    def parse_identifier(self) -> ast.Identifier:
        if self.peek().type != "identifier":
            raise Exception(f"{self.peek().location}: expected a identifier (variable)")
        if self.peek().text == "if":
            return self.parse_if()
        token = self.consume()
        identifier = ast.Identifier(token.text)
        if self.peek().text == "(":
            return self.parse_function_call(identifier)
        return identifier

    def parse_function_call(self, identifier: ast.Identifier) -> ast.FunctionCall:
        self.consume("(")
        args: list[ast.Expression] = []
        while True:
            arg = self.parse_expression()
            args.append(arg)
            if self.peek().text != ",":
                break
            self.consume(",")
        self.consume(")")
        return ast.FunctionCall(identifier, args)

    def parse_expression(self) -> ast.Expression:
        return self.parse_level_1()

    def parse_level_1(self):
        left = self.parse_level_2()
        return left

    def parse_level_2(self):
        left = self.parse_level_3()
        return left

    def parse_level_3(self):
        left = self.parse_level_4()
        return left

    def parse_level_4(self):
        left = self.parse_level_5()
        return left

    def parse_level_5(self):
        left = self.parse_level_6()
        return left

    def parse_level_6(self):
        left = self.parse_level_7()
        while self.peek().text in ["+", "-"]:
            operator_token = self.consume()
            operator = ast.Operator(operator_token.text)
            right = self.parse_level_7()
            left = ast.BinaryOp(left, operator, right)
        return left

    def parse_level_7(self) -> ast.Expression:
        left = self.parse_level_8()
        while self.peek().text in ["*", "/", "%"]:
            operator_token = self.consume()
            operator = ast.Operator(operator_token.text)
            right = self.parse_level_8()
            left = ast.BinaryOp(left, operator, right)
        return left

    def parse_level_8(self) -> ast.Expression:
        if self.peek().text == "(":
            return self.parse_parenthesized()
        elif self.peek().type == "int_literal":
            return self.parse_int_literal()
        elif self.peek().type == "identifier":
            return self.parse_identifier()
        else:
            raise Exception(
                f'{self.peek().location}: expected "(", an integer literal or an identifier'
            )

    def parse_if(self) -> ast.TernaryOp:
        self.consume("if")
        if_ = self.parse_expression()
        self.consume("then")
        then_ = self.parse_expression()
        else_ = None
        if self.peek().text == "else":
            self.consume("else")
            else_ = self.parse_expression()
        return ast.TernaryOp(if_, then_, else_)

    def parse_parenthesized(self) -> ast.Expression:
        self.consume("(")
        expr = self.parse_expression()
        self.consume(")")
        return expr

    def parse(self):
        if not bool(self.tokens):
            return None
        expression = self.parse_expression()
        print(expression)
        if self.pos != self.token_length:
            loc = self.peek().location
            raise Exception(f"Invalid syntax at ({loc.line}, {loc.column})")
        return expression


def parse(tokens: list[Token]) -> ast.Expression:
    parser = Parser(tokens)
    return parser.parse()


if __name__ == "__main__":
    tokens = tokenizer("1 + 1")
    parsed = parse(tokens)
    print(parsed)
