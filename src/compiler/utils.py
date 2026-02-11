import compiler.custom_ast as ast
def get_keywords() -> list[str]:
    return ["if", "while", "var"]

def conditional_ends_with_block(statement: ast.ConditionalStatement) -> bool:
    statement_type = type(statement)
    if statement_type == ast.WhileStatement:
        if type(statement.body) == ast.Block:
            return True
        return False
    elif statement_type == ast.TernaryOp:
        if type(statement.else_) == ast.Block:
            return True
        elif statement.else_ is None and type(statement.then_) == ast.Block:
            return True
        return False

    raise Exception(f"Error: expected {statement} to be "
                    f"of type {ast.ConditionalStatement},"
                    f" it is {type(statement)}")

def convert_boolean_literal(literal: str):
    if literal == "true":
        return True
    elif literal == "false":
        return False
    raise Exception(f"Error: expected type boolean literal but got {literal}")


if __name__ == "__main__":
    from compiler.tokenizer import tokenizer
    from compiler.parser import parse
    tokens = "while a do {b}"
    print(conditional_ends_with_block(parse(tokenizer(tokens))))
