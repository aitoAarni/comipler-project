from dataclasses import dataclass, field


@dataclass
class SourceLocation:
    line: int | None = None
    column: int | None = None
    _testing: bool = field(default=False, init=False, repr=False)

    def new(self):
        new_source_location = SourceLocation(self.line, self.column)
        new_source_location._testing = self._testing
        return new_source_location

    def __eq__(self, other):
        if self._testing or other._testing:
            return True
        return (self.line, self.column) == (other.line, other.column)

    def __str__(self):
        return f"({self.line}, {self.column})"

    def __repr__(self):
        return f"({self.line}, {self.column})"