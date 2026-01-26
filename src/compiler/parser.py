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
        print(peek())
        if peek().type != 'int_literal':
            raise Exception(f'{peek().location}: expected an integer literal')
        token = consume()
        return ast.Literal(int(token.text))

    # This is our main parsing function for this example.
    # To parse "integer + integer" expressions,
    # it uses `parse_int_literal` to parse the first integer,
    # then it checks that there's a supported operator,
    # and finally it uses `parse_int_literal` to parse the
    # second integer.
    def parse_expression() -> ast.BinaryOp:
        left = parse_int_literal()
        operator_token = consume(['+', '-'])
        right = parse_int_literal()
        return ast.BinaryOp(
            left,
            operator_token.text,
            right
        )

    return parse_expression()

if __name__ == "__main__":
    tokens = tokenizer("2 + 2")
    parsed = parse(tokens)
    print(parsed)