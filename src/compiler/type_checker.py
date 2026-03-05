from compiler.types import Int, Bool, Unit, PrimitiveType, FunType
from compiler.tokenizer import tokenizer
from compiler.parser import parse
import compiler.custom_ast as ast
from compiler.symbol_table import SymTab, symbol_table_factory
from compiler.utils import create_top_level_type_symbol_table


def typecheck(node: ast.Expression | None,
              type_table: SymTab) -> PrimitiveType | FunType:
    match node:
        case ast.Literal():
            val_type = type(node.value)
            if val_type == int:
                node.type = Int
                return Int
            elif val_type == bool:
                node.type = Bool
                return Bool
            else:
                node.type = Bool
                return Unit

        case ast.Identifier():
            identifier_type = type_table.get_symbol(node.name)
            return identifier_type

        case ast.VariableDeclaration():
            variable = node.identifier.name
            value = typecheck(node.initializer, type_table)
            node.type = value
            if node.var_type is not None:
                if not value == node.var_type:
                    raise Exception(
                        f"Error: you can only assign type " f"{
                            node.var_type} to " f"{
                            node.identifier.name}, but you tried to assign {value}")

            type_table.add_symbol(variable, value)
            return Unit
        case ast.UnaryOp():
            operand = typecheck(node.right, type_table)
            node.type = operand
            function = type_table.get_symbol("unary_" + node.op.symbol)
            if operand != function.arg_types[0]:
                raise Exception(
                    f"Error: argument to operator "
                    f"{node.op.symbol} must be of type"
                    f" {function.arg_types[0]}, but was of type {operand}")
            return function.return_type

        case ast.BinaryOp():
            t1 = typecheck(node.left, type_table)
            node.type = t1

            t2 = typecheck(node.right, type_table)

            if node.op.symbol in ["=", "==", "!="]:
                if t1 != t2:
                    raise Exception(
                        f"Error: arguments to operator"
                        " {node.op.symbol} must be of same type")
                if node.op.symbol == "=":
                    return Unit
                return Bool
            else:
                function = type_table.get_symbol(node.op.symbol)

                if t1 != function.arg_types[0] or t2 != function.arg_types[1]:
                    raise Exception(
                        f"Error: arguments to operator """
                        "{node.op.symbol} must be of type"
                        f" {function.arg_types[0]} {node.op.symbol}"
                        f" {function.arg_types[1]}"
                        f", but they were {t1} {node.op.symbol} {t2}")
                return function.return_type

        case ast.TernaryOp():
            t1 = typecheck(node.cond, type_table)
            if t1 is not Bool:
                raise Exception(f"Error: condition {node.cond} is not {Bool}")
            t2 = typecheck(node.then_, type_table)
            node.type = t2

            if node.else_ is not None:
                t3 = typecheck(node.else_, type_table)

            if node.else_ is None:
                return t2

            if t2 != t3:
                raise Exception(
                    f"Error: If statement's else and then branch return values"
                    f" don't match {t2} != {t3}"
                )
            return t2

        case ast.WhileStatement():
            t1 = typecheck(node.cond, type_table)
            if t1 is not Bool:
                raise Exception(f"Error: condition {node.cond} is not {Bool}")
            t2 = typecheck(node.body, type_table)
            node.type = t2
            return t2

        case ast.FunctionCall():
            args = node.args
            function = type_table.get_symbol(node.function_name.name)
            node.type = function.return_type
            if len(args) > len(function.arg_types):
                raise Exception(
                    f"Error: function {node.function_name.name} takes "
                    f"{len(function.arg_types)} argument(s), but {len(args)} were given."
                )
            for i, arg in enumerate(args):
                arg_type = typecheck(arg, type_table)
                if function.arg_types[i] == arg_type:
                    continue
                raise Exception(
                    f"Error: function """
                    f"{node.function_name.name} expected "
                    f"paremater type {function.arg_types[i]}"
                    f", but got instead {arg_type}: {arg}.")
            return function.return_type

        case ast.Block():
            statements = node.statements
            nested_type_table = symbol_table_factory("types", type_table)
            for statement in statements:
                typecheck(statement, nested_type_table)
            return_type = typecheck(node.result_expression, nested_type_table)
            node.type = return_type
            return return_type
        case _:
            raise ValueError(
                f"Error: type of {node} isn't defined in typechecker")


if __name__ == "__main__":
    code = "1+1"
    tokens = tokenizer(code)
    parsed = parse(tokens)
    type_table = create_top_level_type_symbol_table()
    typed = typecheck(parsed, type_table)
    print(parsed)
