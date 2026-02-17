from __future__ import annotations

class SymTab:
    def __init__(self, parent: SymTab = None):
        self.symbols = {}
        self.parent = parent

    def add_symbol(self, identifier, value):
        self.symbols[identifier] = value

    def get_symbol(self, symbol: str):
        if symbol in self.symbols:
            return self.symbols[symbol]
        elif self.parent:
            return self.parent.get_symbol(symbol) 
        else:
            raise Exception(f"There is no variable '{symbol}' declared")

    def __str__(self):
        return "Symbol table with variables: " + ", ".join(
            [f"{pair[0]}: {pair[1]}" for pair in self.symbols.items()]
        )
