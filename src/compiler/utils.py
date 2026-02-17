import compiler.custom_ast as ast
from compiler.synmbol_table import SymTab
import operator as o 

def get_keywords() -> list[str]:
    return ["if", "while", "var"]

def search_last_expression(statement: ast.ConditionalStatement) -> bool:
    statement_type = type(statement)
    if statement_type == ast.WhileStatement:
        return statement.body
            
    elif statement_type == ast.TernaryOp:
        if statement.else_ is None:
            return statement.then_
        return statement.else_

def expression_ends_with_block(expression: ast.Expression) -> bool:
    while True:
        expression_type = type(expression)
        if issubclass(expression_type, ast.ConditionalStatement):
            expression = search_last_expression(expression)
        elif expression_type in [ast.UnaryOp, ast.BinaryOp]:
            expression = expression.right

        elif expression_type == ast.VariableDeclaration:
            expression = expression.initializer
        
        else:
            break
    return type(expression) == ast.Block
    
def create_top_level_symbol_table():
    st = SymTab()
    st.add_symbol("unary_-", o.neg)
    st.add_symbol("unary_not", o.not_)
    st.add_symbol("+", o.add)
    st.add_symbol("-", o.sub)
    st.add_symbol("*", o.mul)
    st.add_symbol("/", o.truediv)
    st.add_symbol("%", o.mod)
    st.add_symbol("==", o.eq)
    st.add_symbol("!=", o.ne)
    st.add_symbol("<", o.lt)
    st.add_symbol("<=", o.le)
    st.add_symbol(">", o.gt)
    st.add_symbol(">=", o.ge)
    st.add_symbol("and", lambda a, b: a and b)
    st.add_symbol("or", lambda a, b: a or b)
    st.add_symbol("print_int", print)
    st.add_symbol("print_bool", print)
    return st
    


def convert_boolean_literal(literal: str):
    if literal == "true":
        return True
    elif literal == "false":
        return False
    raise Exception(f"Error: expected type boolean literal but got {literal}")


if __name__ == "__main__":
    from compiler.tokenizer import tokenizer
    from compiler.parser import parse
    tokens = "{a = {a} b}"
    parsed = parse(tokenizer(tokens))
    print(parsed)

    print(expression_ends_with_block(parsed))
