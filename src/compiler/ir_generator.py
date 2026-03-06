from compiler import custom_ast as ast, ir
from compiler.symbol_table import SymTab
from compiler.types import Bool, Int, Unit
from compiler.ir import IRVar, Label
from compiler.utils import create_top_level_type_symbol_table
from typing import Generator
# TODO test multiple var declarations in same scope throws


def generate_ir(
    # 'reserved_names' should contain all global names
    # like 'print_int' and '+'. You can get them from
    # the global symbol table of your interpreter or type checker.
    reserved_names: set[str],
    root_expr: ast.Expression
) -> list[ir.Instruction]:
    # 'var_unit' is used when an expression's type is 'Unit'.
    var_unit = IRVar('unit')

    def new_var_generator() -> Generator[IRVar, None, None]:
        # Create a new unique IR variable
        num = 1
        while True:
            var_name = "x" + str(num) if num != 1 else "x"
            ir_var = IRVar(var_name)
            yield ir_var
            num += 1

    new_var = new_var_generator()

    label_generator = ir.LabelGenerator()

    # We collect the IR instructions that we generate
    # into this list.
    ins: list[ir.Instruction] = []

    # This function visits an AST node,
    # appends IR instructions to 'ins',
    # and returns the IR variable where
    # the emitted IR instructions put the result.
    #
    # It uses a symbol table to map local variables
    # (which may be shadowed) to unique IR variables.
    # The symbol table will be updated in the same way as
    # in the interpreter and type checker.
    def visit(st: SymTab[IRVar], expr: ast.Expression) -> IRVar:
        loc = expr.location
        if not loc:
            raise Exception("Location not defined")
        match expr:
            case ast.Literal():
                # Create an IR variable to hold the value,
                # and emit the correct instruction to
                # load the constant value.
                match expr.value:
                    case bool():
                        var = next(new_var)
                        ins.append(ir.LoadBoolConst(
                            loc, expr.value, var))
                    case int():
                        var = next(new_var)
                        ins.append(ir.LoadIntConst(
                            loc, expr.value, var))
                    case None:
                        var = var_unit
                    case _:
                        raise Exception(
                            f"{loc}: unsupported literal: "
                            f"{type(expr.value)}")

                # Return the variable that holds
                # the loaded value.
                return var

            case ast.Identifier():
                # Look up the IR variable that corresponds to
                # the source code variable.
                return st.get_symbol(expr.name)

            case ast.VariableDeclaration():
                if st.contains_symbol(expr.identifier.name):
                    raise Exception(
                        f"Error: Variable already declared in this scope: "
                        f"{expr.identifier.name}")
                var_initializer = visit(st, expr.initializer)
                var_result = next(new_var)
                ins.append(ir.Copy(loc, var_initializer, var_result))
                st.add_symbol(expr.identifier.name, var_result)

            case ast.UnaryOp():
                var_op = st.get_symbol("unary_" + expr.op.symbol)
                var_right = visit(st, expr.right)
                var_result = next(new_var)
                ins.append(ir.Call(
                    loc, var_op, [var_right], var_result))
                return var_result

            case ast.BinaryOp():
                # Ask the symbol table to return the variable that refers
                # to the operator to call.
                var_op = st.get_symbol(expr.op.symbol)
                # Recursively emit instructions to calculate the operands.
                var_left = visit(st, expr.left)
                var_right = visit(st, expr.right)
                # Generate variable to hold the result.
                var_result = next(new_var)
                # Emit a Call instruction that writes to that variable.
                if expr.op.symbol == "=":
                    # TODO
                    pass
                else:
                    ins.append(ir.Call(
                        loc, var_op, [var_left, var_right], var_result))
                return var_result

            case ast.TernaryOp():
                l_then = label_generator.get_then_label(loc)
                l_end = label_generator.get_if_end_label(loc)
                l_else: Label | None = None
                if expr.else_ is not None:
                    l_else = label_generator.get_else_label(loc)
                var_cond = visit(st, expr.cond)

                if expr.else_ is None:
                    # Create (but don't emit) some jump targets.

                    # Recursively emit instructions for
                    # evaluating the condition.
                    # Emit a conditional jump instruction
                    # to jump to 'l_then' or 'l_end',
                    # depending on the content of 'var_cond'.
                    ins.append(ir.CondJump(loc, var_cond, l_then, l_end))

                    # Emit the label that marks the beginning of
                    # the "then" branch.
                    ins.append(l_then)
                    # Recursively emit instructions for the "then" branch.
                    visit(st, expr.then_)

                    # Emit the label that we jump to
                    # when we don't want to go to the "then" branch.
                else:
                    assert l_else is not None
                    ins.append(ir.CondJump(loc, var_cond, l_then, l_else))
                    ins.append(l_then)
                    visit(st, expr.then_)
                    ins.append(l_else)
                    visit(st, expr.else_)

                ins.append(l_end)

                # An if-then expression doesn't return anything, so we
                # return a special variable "unit".
                return var_unit

            case ast.WhileStatement():
                l_while_start = label_generator.get_while_start_label(loc)
                l_while_body = label_generator.get_while_body_label(loc)
                l_while_end = label_generator.get_while_end_label(loc)
                ins.append(l_while_start)
                var_cond = visit(st, expr.cond)
                ins.append(
                    ir.CondJump(
                        loc,
                        var_cond,
                        l_while_body,
                        l_while_end))
                ins.append(l_while_body)
                visit(st, expr.body)
                ins.append(ir.Jump(loc, l_while_start))
                ins.append(l_while_end)

                return var_unit

            case ast.FunctionCall():
                func_args: list[IRVar] = []
                for arg in expr.args:
                    func_args.append(visit(st, arg))
                return_val = next(new_var)
                
                ins.append(ir.Call(loc, st.get_symbol(expr.function_name.name), func_args, return_val))

                return return_val

            case _:
                raise ValueError("Not implemented")
             # Other AST node cases (see below)

    # We start with a SymTab that maps all available global names
    # like 'print_int' to IR variables of the same name.
    # In the Assembly generator stage, we will give
    # actual implementations for these globals. For now,
    # they just need to exist so the variable lookups work,
    # and clashing variable names can be avoided.
    root_symtab = SymTab[IRVar](parent=None)
    for name in reserved_names:
        root_symtab.add_symbol(name, IRVar(name))

    # Start visiting the AST from the root.
    var_final_result = visit(root_symtab, root_expr)

    # Add IR code to print the result, based on the type assigned earlier
    # by the type checker.
    if root_expr.type == Int:
        r_val = next(new_var)
        ins.append(
            ir.Call(
                ins[0].location,
                root_symtab.get_symbol("print_int"),
                [var_final_result],
                r_val))

    elif root_expr.type == Bool:
        r_val = next(new_var)
        ins.append(
            ir.Call(
                ins[0].location,
                root_symtab.get_symbol("print_bool"),
                [var_final_result],
                r_val))

    return ins


global_vars = "unary_- unary_not + - * / % < <= > >= != == and or print_int print_bool =".split()

if __name__ == "__main__":
    from compiler.tokenizer import tokenizer
    from compiler.parser import parse
    from compiler.type_checker import typecheck

    code = "print_int(3+4, 3)"
    tokens = tokenizer(code)
    parsed = parse(tokens)
    type_table = create_top_level_type_symbol_table()
    typecheck(parsed, type_table)
    if parsed:

        intermediate_representation = generate_ir(set(global_vars), parsed)
        for command in intermediate_representation:
            print(command)
