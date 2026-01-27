from compiler.tokenizer import Token
from compiler.tokenizer import tokenizer
import compiler.custom_ast as ast


def parse(tokens: list[Token]) -> ast.Expression:
    if not bool(tokens):
        return None

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
        if peek().type != "identifier":
            raise Exception(f"{peek().location}: expected a identifier (variable)")
        if peek().text in ["if"]:
            return parse_if()
        token = consume()
        return ast.Identifier(token.text)

    def parse_expression() -> ast.Expression:
        left = parse_term()
        while peek().text in ['+', '-']:
            operator_token = consume()
            operator = ast.Operator(operator_token.text)
            right = parse_term()
            left = ast.BinaryOp(
                left,
                operator,
                right
            )
        return left

    def parse_term() -> ast.Expression:
        left = parse_factor()
        while peek().text in ['*', '/']:
            operator_token = consume()
            operator = ast.Operator(operator_token.text)
            right = parse_factor()
            left = ast.BinaryOp(
                left,
                operator,
                right
            )
        return left

    def parse_factor() -> ast.Expression:
        if peek().text == '(':
            return parse_parenthesized()
        elif peek().type == 'int_literal':
            return parse_int_literal()
        elif peek().type == 'identifier':
            return parse_identifier()
        else:
            raise Exception(f'{peek().location}: expected "(", an integer literal or an identifier')

    def parse_if() -> ast.TernaryOp:
        consume("if")         
        if_ = parse_expression()
        consume("then")
        then_ = parse_expression()
        else_ = None
        if peek().text == "else":
            consume("else")
            else_ = parse_expression()

        return ast.TernaryOp(if_, then_, else_)

    def parse_parenthesized() -> ast.Expression:
        consume('(')
        expr = parse_expression()
        consume(')')
        return expr

    expression = parse_expression()
    if pos != len(tokens):
        loc = peek().location
        raise Exception(f"Invalid syntax at ({loc.line}, {loc.column})") 
    return expression

if __name__ == "__main__":
    tokens = tokenizer("if 2 then 3")
    parsed = parse(tokens)
    print(parsed)

