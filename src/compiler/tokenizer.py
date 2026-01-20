import re
from dataclasses import dataclass, field


@dataclass
class SourceLocation:
    line: int
    column: int
    _testing: bool = field(default=False, init=False, repr=False)

    def __eq__(self, other):
        if self._testing or other._testing:
            return True
        return (self.line, self.column) == (other.line, other.column)


@dataclass
class Token:
    text: str
    type: str
    location: SourceLocation


def tokenizer(source_code: str = "") -> list[Token]:
    identifier = get_regex_for_token("identifier")
    int_literal = get_regex_for_token("int_literal")
    white_space = get_regex_for_token("white_space")
    operator = get_regex_for_token("operator")
    punctuation = get_regex_for_token("punctuation")

    identifier_re = re.compile(identifier)
    int_literal_re = re.compile(int_literal)
    white_space_re = re.compile(white_space)
    operator_re = re.compile(operator)
    punctuation_re = re.compile(punctuation)

    regular_expressions = [
        identifier_re,
        int_literal_re,
        white_space_re,
        operator_re,
        punctuation_re,
    ]
    previous_match_end = 0
    tokens: list[str] = []
    require_white_space_after = False
    token_line = 1
    while previous_match_end < len(source_code):
        for regex in regular_expressions:
            match = regex.search(source_code, previous_match_end)
            if match and match.start() == previous_match_end:
                previous_match_end = match.end()
                if regex == white_space_re:
                    token_line += match[0].count("\n")
                    require_white_space_after = False
                elif require_white_space_after:
                    raise Exception(f"Invalid syntax. Could not tokenize {source_code}")

                elif regex == identifier_re:
                    token = Token(
                        match[0],
                        "identifier",
                        SourceLocation(token_line, match.start() + 1),
                    )
                    tokens.append(token)
                elif regex == operator_re:
                    token = Token(
                        match[0],
                        "operator",
                        SourceLocation(token_line, match.start() + 1),
                    )
                    tokens.append(token)
                elif regex == punctuation_re:
                    token = Token(
                        match[0],
                        "punctuation",
                        SourceLocation(token_line, match.start() + 1),
                    )
                    tokens.append(token)
                
                elif regex == int_literal_re:
                    require_white_space_after = True
                    token = Token(
                        match[0],
                        "int_literal",
                        SourceLocation(token_line, match.start() + 1),
                    )
                    tokens.append(token)
                break
        else:
            raise Exception(f"Invalid syntax. Could not tokenize {source_code}")

    return tokens


def get_regex_for_token(regex: str) -> str:
    tokenizer_regexes = {
        "identifier": r"[a-zA-Z|_][a-zA-Z|_|0-9]*",
        "int_literal": r"[0-9]+",
        "white_space": r"[\n|\t| ]+",
        "operator": r"\+|-|\*|\\|%|==|!=|=|<=|>=|<|>",
        "punctuation": r"\(",
    }
    return tokenizer_regexes[regex]


if __name__ == "__main__":
    print(tokenizer("+"))
