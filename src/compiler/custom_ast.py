from dataclasses import dataclass, field
from compiler.location import SourceLocation


def create_test_location():
    loc = SourceLocation(0, 0)
    loc._testing = True
    return loc


@dataclass
class Expression:
    """Base class for AST nodes representing expressions."""


@dataclass
class Literal(Expression):
    value: int | bool | None
    location: SourceLocation | None = None

@dataclass
class Identifier(Expression):
    name: str
    location: SourceLocation | None = None

@dataclass
class Operator(Expression):
    symbol: str
    location: SourceLocation | None = None


@dataclass
class Punctuation(Expression):
    name: str
    location: SourceLocation | None = None


@dataclass
class FunctionCall(Expression):
    function_name: Identifier
    args: list[Expression] | None


@dataclass
class UnaryOp(Expression):
    op: Operator
    right: Expression


@dataclass
class BinaryOp(Expression):
    """AST node for a binary operation like `A + B`"""

    left: Expression
    op: Expression
    right: Expression


@dataclass
class ConditionalStatement(Expression):
    """Class for conditional statements"""

    cond: Expression


@dataclass
class TernaryOp(ConditionalStatement):
    then_: Expression
    else_: Expression | None = None


@dataclass
class WhileStatement(ConditionalStatement):
    body: Expression


@dataclass
class Block(Expression):
    statements: list[Expression]
    result_expression: Expression = field(default_factory=lambda: Literal(None))


@dataclass
class VariableDeclaration(Expression):
    identifier: Identifier
    initializer: Expression
