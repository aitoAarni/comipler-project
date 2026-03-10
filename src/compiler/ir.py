from dataclasses import dataclass, fields
from typing import Any, Generator, Callable
from compiler.location import Location


@dataclass(frozen=True)
class IRVar:
    """Represents the name of a memory location or built-in."""
    name: str

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Instruction():
    """Base class for IR instructions."""
    location: Location

    def __str__(self) -> str:
        """Returns a string representation similar to
        our IR code examples, e.g. 'LoadIntConst(3, x1)'"""
        def format_value(v: Any) -> str:
            if isinstance(v, list):
                return f'[{", ".join(format_value(e) for e in v)}]'
            else:
                return str(v)
        args = ', '.join(
            format_value(getattr(self, field.name))
            for field in fields(self)
            if field.name != 'location'
        )
        return f'{type(self).__name__}({args})'

@dataclass(frozen=True)
class FunctionDefinition(Instruction):
    """Creates a function"""
    name: IRVar
    params: list[IRVar]

    def __str__(self) -> str:
        return f"{self.name}({", ".join([param.name for param in self.params])})"

    def __repr__(self) -> str:
        return f"{self.name}({", ".join([param.name for param in self.params])})"

@dataclass(frozen=True)
class LoadBoolConst(Instruction):
    """Loads a boolean constant value to `dest`."""
    value: bool
    dest: IRVar

@dataclass(frozen=True)
class Return(Instruction):
    """Returns from function"""
    return_val: IRVar

@dataclass(frozen=True)
class Label(Instruction):
    """Marks the destination of a jump instruction."""
    name: str


@dataclass(frozen=True)
class LoadIntConst(Instruction):
    """Loads a constant value to `dest`."""
    value: int
    dest: IRVar


@dataclass(frozen=True)
class Copy(Instruction):
    """Copies a value from one variable to another."""
    source: IRVar
    dest: IRVar


@dataclass(frozen=True)
class Call(Instruction):
    """Calls a function or built-in."""
    fun: IRVar
    args: list[IRVar]
    dest: IRVar


@dataclass(frozen=True)
class Jump(Instruction):
    """Unconditionally continues execution from the given label."""
    label: Label


@dataclass(frozen=True)
class CondJump(Instruction):
    """Continues execution from `then_label` if `cond` is true, otherwise from `else_label`."""
    cond: IRVar
    then_label: Label
    else_label: Label


class LabelGenerator:
    def __init__(self) -> None:
        self.__then_count = self.__new_label_generator("then")
        self.__else_count = self.__new_label_generator("else")
        self.__if_end_count = self.__new_label_generator("if_end")
        self.__while_start_count = self.__new_label_generator("while_start")
        self.__while_end_count = self.__new_label_generator("while_end")
        self.__while_body_count = self.__new_label_generator("while_body")
        self.__or_skip_count = self.__new_label_generator("or_skip")
        self.__or_right_count = self.__new_label_generator("or_right")
        self.__or_end_count = self.__new_label_generator("or_end")
        self.__and_right_count = self.__new_label_generator("and_right")
        self.__and_skip_count = self.__new_label_generator("and_skip")
        self.__and_end_count = self.__new_label_generator("and_end")

    @staticmethod
    def __new_label_generator(text: str) -> Generator[str, None, None]:
        # Create a new unique IR variable
        num = 1
        while True:
            var_name = text + str(num) if num != 1 else text
            yield var_name
            num += 1

    def __create_label(self,
                       loc: Location,
                       generator: Generator[str,
                                            None,
                                            None]) -> Label:
        name = next(generator)
        return Label(loc, name)

    def get_then_label(self, loc: Location) -> Label:
        return self.__create_label(loc, self.__then_count)

    def get_if_end_label(self, loc: Location) -> Label:
        return self.__create_label(loc, self.__if_end_count)

    def get_else_label(self, loc: Location) -> Label:
        return self.__create_label(loc, self.__else_count)

    def get_while_start_label(self, loc: Location) -> Label:
        return self.__create_label(loc, self.__while_start_count)

    def get_while_end_label(self, loc: Location) -> Label:
        return self.__create_label(loc, self.__while_end_count)

    def get_while_body_label(self, loc: Location) -> Label:
        return self.__create_label(loc, self.__while_body_count)

    def get_or_skip_label(self, loc: Location) -> Label:
        return self.__create_label(loc, self.__or_skip_count)

    def get_or_right_label(self, loc: Location) -> Label:
        return self.__create_label(loc, self.__or_right_count)

    def get_or_end_label(self, loc: Location) -> Label:
        return self.__create_label(loc, self.__or_end_count)

    def get_and_right_label(self, loc: Location) -> Label:
        return self.__create_label(loc, self.__and_right_count)

    def get_and_skip_label(self, loc: Location) -> Label:
        return self.__create_label(loc, self.__and_skip_count)

    def get_and_end_label(self, loc: Location) -> Label:
        return self.__create_label(loc, self.__and_end_count)
