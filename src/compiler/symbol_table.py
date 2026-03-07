from __future__ import annotations
from compiler.types import FunType
from collections.abc import Callable
from typing import Any, Literal, overload
from compiler.ir import IRVar

type SymTabReturnType = FunType | Callable[..., Any] | IRVar


class SymTab[T: SymTabReturnType]:
    def __init__(self, parent: SymTab | None = None):
        self.symbols: dict[str, T] = {}
        self.parent = parent
        self.locals: list[T] = []

    def add_symbol(self, identifier: str, value: T) -> None:
        self.symbols[identifier] = value

    def update_symbol(self, identifier: str, value: T) -> None:
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

    def contains_symbol(self, symbol: str) -> bool:
        return symbol in self.symbols.keys()

    def add_local(self, identifier: T) -> None:
        if self.parent:
            self.parent.add_local(identifier)
        else:
            self.locals.append(identifier)

    def __str__(self) -> str:
        return "Symbol table with variables: " + ", ".join(
            [f"{pair[0]}: {pair[1]}" for pair in self.symbols.items()]
        )


type SymTabFactoryArgs = Literal["types", "variables"]


@overload
def symbol_table_factory(
    symbol_table_type: Literal["types"],
    parent_symbol_table: None | SymTab = None) -> SymTab[FunType]: ...


@overload
def symbol_table_factory(
    symbol_table_type: Literal["variables"],
    parent_symbol_table: None | SymTab = None) -> SymTab[Callable[..., Any]]: ...


def symbol_table_factory(symbol_table_type: SymTabFactoryArgs,
                         parent_symbol_table: None | SymTab = None) -> SymTab[Callable[...,
                                                                                       Any]] | SymTab[FunType]:
    match symbol_table_type:
        case "types":
            return SymTab[FunType](parent_symbol_table)
        case "variables":
            return SymTab[Callable[..., Any]](parent_symbol_table)
        case _:
            raise ValueError(
                "Error: SymTabFactory doesn't have that type defined")
