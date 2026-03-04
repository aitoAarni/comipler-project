from dataclasses import dataclass

type Type = PrimitiveType | FunType

@dataclass
class PrimitiveType:
    type: str | None
    name: str

    def __str__(self) -> str:
        return str(self.name)

    def __repr__(self) -> str:
        return str(self.name)

Int = PrimitiveType("Int", "Int")
Bool = PrimitiveType("Bool", "Bool")
Unit = PrimitiveType(None, "Unit")

@dataclass
class FunType:
    arg_types: list[PrimitiveType]
    return_type: PrimitiveType
