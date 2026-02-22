from compiler.types import Int, Bool, Unit, FunType, PrimitiveType
from compiler.tokenizer import tokenizer
from compiler.parser import parse
import compiler.custom_ast as ast
from compiler.synmbol_table import SymTab
from compiler.utils import create_top_level_type_symbol_table


def typecheck(node: ast.Expression, type_table: SymTab) -> PrimitiveType:
    match node:
        case ast.Literal():
            val_type = type(node.value)
            if val_type == int:
                return Int
            elif val_type == bool:
                return Bool
            else:
                return Unit
        case ast.Identifier():
            pass
        case ast.BinaryOp():
            t1 = typecheck(node.left, type_table)
            t2 = typecheck(node.right, type_table)
            function = type_table.get_symbol(node.op.symbol)

            if t1 != function.arg_types[0] or t2 != function.arg_types[1]:
                raise Exception(
                    f"Error: arguments to operator {node.op.symbol} must be of type"
                    f" {function.arg_types[0]} {node.op.symbol} {function.arg_types[1]}"
                    f", but they were {t1} {node.op.symbol} {t2}"
                )

            return function.return_type

        case ast.TernaryOp():
            pass
            # t1 = typecheck(node.condition, type_table)
            # if t1 is not Bool:
            #     raise ...
            # t2 = typecheck(node.then_branch, type_table)
            # t3 = typecheck(node.else_branch, type_table)
            # if t2 != t3:
            #     raise ...
            # return t2


if __name__ == "__main__":
    code = "1 + 1"
    tokens = tokenizer(code)
    parsed = parse(tokens)
    type_table = create_top_level_type_symbol_table()
    typed = typecheck(parsed, type_table)
    print(typed)
