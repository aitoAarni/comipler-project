import compiler.ir as ir


class Locals:
    """Knows the memory location of every local variable."""
    _var_to_location: dict[ir.IRVar, str]
    _stack_used: int

    def __init__(self, variables: list[ir.IRVar]) -> None:
        self._var_to_location = {
            x: f"-{(i + 1) * 8}(%rbp)" for i, x in enumerate(variables)}
        self._stack_used = len(variables) * 8

    def get_ref(self, v: ir.IRVar, plain: bool = True) -> str:
        """Returns an Assembly reference like `-24(%rbp)`
        for the memory location that stores the given variable"""
        if v.name == "unit":
            return "$0"
        elif v.name == "print_int":
            return "print_int" if plain else "$print_int"
        elif v.name == "print_bool":
            return "print_bool" if plain else "$print_bool"
        elif v.name == "read_int":
            return "read_int" if plain else "$read_int"
        return self._var_to_location[v]

    def stack_used(self) -> int:
        """Returns the number of bytes of stack space needed for the local variables."""
        return self._stack_used


def generate_assembly(
        instruction_dict: dict[str, list[ir.Instruction]], local_vars: list[ir.IRVar]) -> str:
    lines: list[str] = []
    def emit(line: str) -> None: lines.append(line)

    locals = Locals(
        local_vars
    )
    instructions = instruction_dict["main"]
    call_regs = "rdi rsi rdx rcx r8 r9".split()

    # ... Emit initial declarations and stack setup here ...
    emit(".extern print_int")
    emit(".extern print_bool")
    emit(".extern read_int")
    emit(".global main")
    emit(".type main, @function")

    emit(".section .text")
    emit("main:")

    emit("pushq %rbp")
    emit("movq %rsp, %rbp")
    emit(f"subq  ${locals._stack_used}, %rsp")

    for insn in instructions:
        emit('\n# ' + str(insn))
        match insn:
            case ir.Label():
                emit("")
                # ".L" prefix marks the symbol as "private".
                # This makes GDB backtraces look nicer too:
                # https://stackoverflow.com/a/26065570/965979
                emit(f'.L{insn.name}:')
                continue
            case ir.LoadIntConst():
                if -2**31 <= insn.value < 2**31:
                    emit(f'movq ${insn.value}, {locals.get_ref(insn.dest)}')
                else:
                    emit(f'movabsq ${insn.value}, %rax')
                    emit(f'movq %rax, {locals.get_ref(insn.dest)}')
                continue

            case ir.LoadBoolConst():
                emit(
                    f"movq $"
                    f"{1 if insn.value else 0}, "
                    f"{locals.get_ref(insn.dest)}")
                continue
            case ir.Copy():
                emit(f"movq {locals.get_ref(insn.source, False)}, %rax")
                emit(f"movq %rax, {locals.get_ref(insn.dest)}")
                continue

            case ir.CondJump():
                emit(f"cmpq $0, {locals.get_ref(insn.cond)}")
                emit(f"jne .L{insn.then_label.name}")
                emit(f"jmp .L{insn.else_label.name}")
                continue
            case ir.Jump():
                emit(f'jmp .L{insn.label.name}')
                continue
            case ir.Call():
                args = [locals.get_ref(arg) for arg in insn.args]
                result = locals.get_ref(insn.dest)
                match insn.fun.name:
                    case "unary_-":
                        emit(f"movq {args[0]}, %rax")
                        emit(f"negq %rax")
                        emit(f"movq %rax, {result}")
                        continue

                    case "unary_not":
                        emit(f"movq {args[0]}, %rax")
                        emit(f"xorq $1, %rax")
                        emit(f"movq %rax, {result}")
                        continue
                    case "+":
                        emit(f"movq {args[0]}, %rax")
                        emit(f"addq {args[1]}, %rax")
                        emit(f"movq %rax, {result}")
                        continue
                    case "-":
                        emit(f"movq {args[0]}, %rax")
                        emit(f"subq {args[1]}, %rax")
                        emit(f"movq %rax, {result}")
                        continue
                    case "*":
                        emit(f"movq {args[0]}, %rax")
                        emit(f"imulq {args[1]}, %rax")
                        emit(f"movq %rax, {result}")
                        continue
                    case "/":
                        emit(f"movq {args[0]}, %rax")
                        emit(f"cqto")
                        emit(f"idivq {args[1]}")
                        emit(f"movq %rax, {result}")
                        continue
                    case "%":
                        emit(f"movq {args[0]}, %rax")
                        emit(f"cqto")
                        emit(f"idivq {args[1]}")
                        emit(f"movq %rdx, %rax")
                        emit(f"movq %rax, {result}")
                        continue
                    case "<":
                        emit(f"xor %rax, %rax")
                        emit(f"movq {args[0]}, %rdx")
                        emit(f"cmpq {args[1]}, %rdx")
                        emit(f"setl %al")
                        emit(f"movq %rax, {result}")
                        continue
                    case ">":
                        emit(f"xor %rax, %rax")
                        emit(f"movq {args[0]}, %rdx")
                        emit(f"cmpq {args[1]}, %rdx")
                        emit(f"setg %al")
                        emit(f"movq %rax, {result}")
                        continue
                    case "<=":
                        emit(f"xor %rax, %rax")
                        emit(f"movq {args[0]}, %rdx")
                        emit(f"cmpq {args[1]}, %rdx")
                        emit(f"setle %al")
                        emit(f"movq %rax, {result}")
                        continue
                    case ">=":
                        emit(f"xor %rax, %rax")
                        emit(f"movq {args[0]}, %rdx")
                        emit(f"cmpq {args[1]}, %rdx")
                        emit(f"setge %al")
                        emit(f"movq %rax, {result}")
                        continue
                    case "!=":
                        emit(f"xor %rax, %rax")
                        emit(f"movq {args[0]}, %rdx")
                        emit(f"cmpq {args[1]}, %rdx")
                        emit(f"setne %al")
                        emit(f"movq %rax, {result}")
                        continue
                    case "==":
                        emit(f"xor %rax, %rax")
                        emit(f"movq {args[0]}, %rdx")
                        emit(f"cmpq {args[1]}, %rdx")
                        emit(f"sete %al")
                        emit(f"movq %rax, {result}")
                        continue
                    case _:
                        for i, arg in enumerate(args):
                            emit(f"movq {arg}, %{call_regs[i]}")
                        emit(f"callq {locals.get_ref(insn.fun)}")
                        emit(f"movq %rax, {result}")

    emit(f"")
    emit(f"movq $0, %rax")
    emit(f"movq %rbp, %rsp")
    emit(f"popq %rbp")
    emit(f"ret")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":

    from compiler.tokenizer import tokenizer
    from compiler.parser import parse
    from compiler.type_checker import typecheck
    from compiler.utils import GLOBAL_VARS
    from compiler.ir_generator import IrGenerator
    from compiler.utils import create_top_level_type_symbol_table

    code = "var x = print_int; x(4)"
    tokens = tokenizer(code)
    parsed = parse(tokens)
    type_table = create_top_level_type_symbol_table()
    typecheck(parsed, type_table)
    if parsed:
        ir_gen = IrGenerator(set(GLOBAL_VARS), parsed)
        intermediate_representation = ir_gen.generate_ir()
        assembly = generate_assembly(
            intermediate_representation,
            ir_gen.get_locals())

        print(assembly)
        # for line in assembly:
        # print(line)
