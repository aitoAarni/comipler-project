from __future__ import annotations
from typing import Self
from dataclasses import dataclass, field


@dataclass
class Location:
    line: int | None = None
    column: int | None = None
    _testing: bool = field(default=False, init=False, repr=False)

    def new(self) -> Location:
        new_source_location = Location(self.line, self.column)
        new_source_location._testing = self._testing
        return new_source_location

    def __eq__(self: Self, other: object) -> bool:
        if not isinstance(other, Location): return False
        if self._testing or other._testing:
            return True
        return (self.line, self.column) == (other.line, other.column)

    def __str__(self) -> str:
        return f"({self.line}, {self.column})"

    def __repr__(self) -> str:
        return f"({self.line}, {self.column})"