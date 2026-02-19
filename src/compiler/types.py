from dataclasses import dataclass


@dataclass
class PrimitiveType:
    type: str

    def __str__(self):
        return str(self.type)

    def __repr__(self):
        return str(self.type)

Int = PrimitiveType("Int")
Bool = PrimitiveType("Bool")
Unit = PrimitiveType(None)

@dataclass
class FunType:
    arg_types: list[PrimitiveType]
    return_type: PrimitiveType
