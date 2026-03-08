from compiler import custom_ast as ast, ir
from compiler.symbol_table import SymTab
from compiler.types import Bool, Int, Unit
from compiler.ir import IRVar, Label
from compiler.utils import create_top_level_type_symbol_table
from typing import Generator
import dataclasses

# TODO add 'and' and 'or' keyowrds to work properly


class IrGenerator:
    def __init__(self, reserved_names: set[str], root_expr: ast.Expression):
        self.reserved_names = reserved_names
        self.root_expr = root_expr
        self.root_symtab = SymTab[IRVar]()

    def get_locals(self) -> list[IRVar]:
        return self.root_symtab.get_locals()

    def generate_ir(self) -> list[ir.Instruction]:
        var_unit = IRVar('unit')

        def new_var_generator() -> Generator[IRVar, None, None]:
            num = 1
            while True:
                var_name = "x" + str(num) if num != 1 else "x"
                ir_var = IRVar(var_name)
                self.root_symtab.add_local(ir_var)
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
                    if expr.op.symbol == "=":
                        var_right = visit(st, expr.right)
                        assert isinstance(expr.left, ast.Identifier)
                        var_left = st.get_symbol(expr.left.name)
                        ins.append(ir.Copy(loc, var_right, var_left))
                        return var_left

                    elif expr.op.symbol == "or":
                        result_var = next(new_var)
                        left_var = visit(st, expr.left)
                        l_or_skip = label_generator.get_or_skip_label(loc)
                        l_or_right = label_generator.get_or_right_label(loc)
                        l_or_end = label_generator.get_or_end_label(loc)
                        ins.append(
                            ir.CondJump(
                                loc,
                                left_var,
                                l_or_skip,
                                l_or_right))

                        ins.append(l_or_right)
                        var_right = visit(st, expr.right)
                        ins.append(ir.Copy(loc, var_right, result_var))
                        ins.append(ir.Jump(loc, l_or_end))

                        ins.append(l_or_skip)
                        ins.append(ir.Copy(loc, left_var, result_var))
                        ins.append(ir.Jump(loc, l_or_end))

                        ins.append(l_or_end)
                        return result_var
                    elif expr.op.symbol == "and":
                        result_var = next(new_var)
                        left_var = visit(st, expr.left)
                        l_and_right = label_generator.get_and_right_label(loc)
                        l_and_skip = label_generator.get_and_skip_label(loc)
                        l_and_end = label_generator.get_and_end_label(loc)
                        ins.append(
                            ir.CondJump(
                                loc,
                                left_var,
                                l_and_right,
                                l_and_skip))
                        ins.append(l_and_right)
                        right_var = visit(st, expr.right)
                        ins.append(ir.Copy(loc, right_var, result_var))
                        ins.append(ir.Jump(loc, l_and_end))

                        ins.append(l_and_skip)
                        ins.append(ir.Copy(loc, left_var, result_var))
                        ins.append(ir.Jump(loc, l_and_end))

                        ins.append(l_and_end)

                        return result_var
                    else:
                        # Recursively emit instructions to calculate the
                        # operands.
                        var_left = visit(st, expr.left)
                        var_right = visit(st, expr.right)
                        # Generate variable to hold the result.
                        var_result = next(new_var)
                        # Emit a Call instruction that writes to that variable.

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

                    ins.append(
                        ir.Call(
                            loc,
                            st.get_symbol(
                                expr.function_name.name),
                            func_args,
                            return_val))

                    return return_val

                case ast.Block():
                    block_symbol_table = SymTab[IRVar](st)
                    for arg in expr.statements:
                        visit(block_symbol_table, arg)
                    return visit(block_symbol_table, expr.result_expression)

                case None:
                    return var_unit
                case _:
                    raise ValueError("Not implemented")

        for name in self.reserved_names:
            self.root_symtab.add_symbol(name, IRVar(name))

        var_final_result = visit(self.root_symtab, self.root_expr)
        if self.root_expr.type == Int:
            r_val = next(new_var)
            ins.append(
                ir.Call(
                    ins[0].location,
                    self.root_symtab.get_symbol("print_int"),
                    [var_final_result],
                    r_val))

        elif self.root_expr.type == Bool:
            r_val = next(new_var)
            ins.append(
                ir.Call(
                    ins[0].location,
                    self.root_symtab.get_symbol("print_bool"),
                    [var_final_result],
                    r_val))

        return ins


def get_all_ir_variables(instructions: list[ir.Instruction]) -> list[ir.IRVar]:
    result_list: list[ir.IRVar] = []
    result_set: set[ir.IRVar] = set()

    def add(v: ir.IRVar) -> None:
        if v not in result_set:
            result_list.append(v)
            result_set.add(v)

    for insn in instructions:
        for field in dataclasses.fields(insn):
            value = getattr(insn, field.name)
            if isinstance(value, ir.IRVar):
                add(value)
            elif isinstance(value, list):
                for v in value:
                    if isinstance(v, ir.IRVar):
                        add(v)
    return result_list


if __name__ == "__main__":
    from compiler.tokenizer import tokenizer
    from compiler.parser import parse
    from compiler.type_checker import typecheck
    from compiler.utils import GLOBAL_VARS

    code = """
    1 + 1
    """
    tokens = tokenizer(code)
    parsed = parse(tokens)
    type_table = create_top_level_type_symbol_table()
    typecheck(parsed, type_table)
    ir_gen = IrGenerator(set(GLOBAL_VARS), parsed)
    intermediate_representation = ir_gen.generate_ir()
    for command in intermediate_representation:
        print(command)
    print("locals", ir_gen.get_locals())
    print(f"vars: {get_all_ir_variables(intermediate_representation)}")
