import re
from dataclasses import dataclass, field
from compiler.location import Location


@dataclass
class Token:
    text: str
    type: str
    location: Location


def tokenize_line(source_code: str, line_number: int) -> list[Token]:
    identifier = get_regex_for_token("identifier")
    int_literal = get_regex_for_token("int_literal")
    white_space = get_regex_for_token("white_space")
    operator = get_regex_for_token("operator")
    punctuation = get_regex_for_token("punctuation")
    comment = get_regex_for_token("comment")

    identifier_re = re.compile(identifier)
    int_literal_re = re.compile(int_literal)
    white_space_re = re.compile(white_space)
    operator_re = re.compile(operator)
    punctuation_re = re.compile(punctuation)
    comment_re = re.compile(comment)

    regular_expressions = [
        comment_re,
        int_literal_re,
        identifier_re,
        white_space_re,
        operator_re,
        punctuation_re,
    ]
    previous_match_end = 0
    tokens: list[Token] = []
    reqiure_non_identifier_char_after = False
    while previous_match_end < len(source_code):
        for regex in regular_expressions:
            match = regex.search(source_code, previous_match_end)
            if match and match.start() == previous_match_end:
                previous_match_end = match.end()

                if reqiure_non_identifier_char_after and regex in [
                    identifier_re,
                    int_literal_re,
                ]:

                    raise Exception(
                        f"Invalid syntax. Could not tokenize {source_code}")
                else:
                    reqiure_non_identifier_char_after = False

                if regex == identifier_re:
                    token = Token(
                        match[0],
                        "identifier",
                        Location(line_number, match.start() + 1),
                    )
                    tokens.append(token)
                elif regex == operator_re:
                    token = Token(
                        match[0],
                        "operator",
                        Location(line_number, match.start() + 1),
                    )
                    tokens.append(token)
                elif regex == punctuation_re:
                    token = Token(
                        match[0],
                        "punctuation",
                        Location(line_number, match.start() + 1),
                    )
                    tokens.append(token)

                elif regex == int_literal_re:
                    reqiure_non_identifier_char_after = True
                    token = Token(
                        match[0],
                        "int_literal",
                        Location(line_number, match.start() + 1),
                    )
                    tokens.append(token)
                break
        else:
            raise Exception(f"Invalid syntax. Could not tokenize {source_code}")

    return tokens


def get_regex_for_token(regex: str) -> str:
    tokenizer_regexes = {
        "identifier": r"[a-zA-Z|_][a-zA-Z|_|0-9]*",
        "int_literal": r"[0-9]+|true|false",
        "white_space": r"[\n|\t| ]+",
        "operator": r"\+|-|\*|/|%|==|!=|=|<=|>=|<|>",
        "punctuation": r"\(|\)|\{|\}|,|;|:",
        "comment": r"(//|#)[^\n]*",
    }
    return tokenizer_regexes[regex]


def tokenizer(source_code: str = "") -> list[Token]:
    tokens = []
    lines = source_code.split("\n")
    for i, line in enumerate(lines):
        line_tokens = tokenize_line(line, i + 1)
        tokens.extend(line_tokens)
    return tokens


if __name__ == "__main__":
    code = "var x : = 2"
    print(tokenizer(code))
