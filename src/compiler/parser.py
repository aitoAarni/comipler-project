from compiler.tokenizer import Token
from compiler.tokenizer import tokenizer
import compiler.custom_ast as ast


def parse(tokens: list[Token]) -> ast.Expression:
    pos = 0

    def peek() -> Token:
        if pos < len(tokens):
            return tokens[pos]
        else:
            return Token(
                location=tokens[-1].location,
                type="end",
                text="",
            )

    def consume(expected: str | list[str] | None = None) -> Token:
        nonlocal pos
        token = peek()
        if isinstance(expected, str) and token.text != expected:
            raise Exception(f'{token.location}: expected "{expected}"')
        if isinstance(expected, list) and token.text not in expected:
            comma_separated = ", ".join([f'"{e}"' for e in expected])
            raise Exception(f"{token.location}: expected one of: {comma_separated}")
        pos += 1
        return token

    def parse_int_literal() -> ast.Literal:
        if peek().type != "int_literal":
            raise Exception(f"{peek().location}: expected an integer literal")
        token = consume()
        return ast.Literal(int(token.text))

    def parse_identifier() -> ast.Identifier:
        pass

    def parse_term() -> ast.Expression:
        if peek().type == "int_literal":
            return parse_int_literal()
        elif peek().type == "identifier":
            return parse_identifier()
        else:
            raise Exception(
                f"{peek().location}: expected an integer literal or an identifier"
            )

    def parse_expression() -> ast.BinaryOp:
        left = parse_term()
        while peek().text in ['+', '-']:
            # Move past the '+' or '-'.
            operator_token = consume()
            operator = operator_token.text

            # Parse the operator on the right.
            right = parse_term()

            # Combine it with the stuff we've
            # accumulated on the left so far.
            left = ast.BinaryOp(
                left,
                operator,
                right
            )
        
        return left

    return parse_expression()


if __name__ == "__main__":
    tokens = tokenizer("2 + 2")
    parsed = parse(tokens)
    print(parsed)
