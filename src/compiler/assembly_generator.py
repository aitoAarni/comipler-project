import compiler.ir as ir


class Locals:
    """Knows the memory location of every local variable."""
    _var_to_location: dict[ir.IRVar, str]
    _stack_used: int

    def __init__(self, variables: list[ir.IRVar]) -> None:
        self._var_to_location = {
            x: f"-{(i + 1) * 8}(%rbp)" for i, x in enumerate(variables)}
        self._stack_used = len(variables) * 8 

    def get_ref(self, v: ir.IRVar) -> str:
        """Returns an Assembly reference like `-24(%rbp)`
        for the memory location that stores the given variable"""
        return self._var_to_location[v]

    def stack_used(self) -> int:
        """Returns the number of bytes of stack space needed for the local variables."""
        return self._stack_used


if __name__ == "__main__":
    from compiler.tokenizer import tokenizer
    from compiler.parser import parse
    from compiler.type_checker import typecheck
    from compiler.ir_generator import generate_ir
    from compiler.utils import GLOBAL_VARS, create_top_level_type_symbol_table
    from compiler.symbol_table import SymTab
    from compiler.ir import IRVar

    code = """
    var x = 1; var y = 2; {var x = 2; var z = 3;}
    """
    tokens = tokenizer(code)
    parsed = parse(tokens)
    type_table = create_top_level_type_symbol_table()
    typecheck(parsed, type_table)
    if parsed:
        ir_sym_tab = SymTab[IRVar](parent=None)
        intermediate_representation = generate_ir(
            set(GLOBAL_VARS), parsed, ir_sym_tab)
        locs = Locals(ir_sym_tab.locals) 
        print(locs._var_to_location)
        print(locs.stack_used())