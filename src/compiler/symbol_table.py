from __future__ import annotations
from compiler.types import FunType
from collections.abc import Callable
from typing import Any, Literal, overload

type SymTabReturnType = FunType | Callable[..., Any]


class SymTab[T: SymTabReturnType]:
    def __init__(self, parent: SymTab | None = None):
        self.symbols: dict[str, T] = {}
        self.parent = parent

    def add_symbol(self, identifier: str, value: Any) -> None:
        self.symbols[identifier] = value

    def update_symbol(self, identifier: str, value: Any) -> None:
        if identifier in self.symbols:
            return self.add_symbol(identifier, value)
        elif self.parent:
            return self.parent.update_symbol(identifier, value)
        raise Exception(f"'{identifier}' is not assignable in this scope")

    def get_symbol(self, symbol: str) -> T:
        if symbol in self.symbols:
            return self.symbols[symbol]
        elif self.parent:
            return self.parent.get_symbol(symbol)
        else:
            raise Exception(f"There is no variable '{symbol}' declared")

    def __str__(self) -> str:
        return "Symbol table with variables: " + ", ".join(
            [f"{pair[0]}: {pair[1]}" for pair in self.symbols.items()]
        )

type SymTabFactoryArgs = Literal["types", "variables"]

@overload
def symbol_table_factory(symbol_table_type: Literal["types"]) -> SymTab[FunType]:...

@overload
def symbol_table_factory(symbol_table_type: Literal["variables"]) -> SymTab[Callable[..., Any]]:...


def symbol_table_factory(symbol_table_type: SymTabFactoryArgs) -> SymTab[Callable[..., Any]] | SymTab[FunType]:
    match symbol_table_type:
        case "types":
            return SymTab[FunType]()
        case "variables":
            return SymTab[Callable[..., Any]]()
        case _:
            raise ValueError("Error: SymTabFactory doesn't have that type defined")