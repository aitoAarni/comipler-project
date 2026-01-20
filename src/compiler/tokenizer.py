import re


def tokenizer(source_code: str="") -> list[str]:
    identifier = get_regex_for_token("identifier")
    positive_integer = get_regex_for_token("positive_integer")
    white_space = get_regex_for_token("white_space")

    identifier_re = re.compile(identifier)
    positive_integer_re = re.compile(positive_integer)
    white_space_re = re.compile(white_space)
    regular_expressions = [identifier_re, positive_integer_re, white_space_re]
    previous_match_end = 0
    tokens: list[str] = []
    require_white_space_after = False

    while (previous_match_end < len(source_code)):
        for regex in regular_expressions:
            match = regex.search(source_code, previous_match_end)
            if match and match.start() == previous_match_end:
                previous_match_end = match.end()
                if regex == white_space_re:
                    require_white_space_after = False
                elif require_white_space_after:
                    raise Exception(f"Invalid syntax. Could not tokenize {source_code}")
                elif regex == identifier_re:
                    tokens.append(match[0])
                elif regex == positive_integer_re:
                    require_white_space_after = True
                    tokens.append(match[0])
                break
        else:
            raise Exception(f"Invalid syntax. Could not tokenize {source_code}")

    return tokens

def get_regex_for_token(regex: str) -> str:
    tokenizer_regexes = {
        "identifier": r"[a-zA-Z|_][a-zA-Z|_|0-9]*",
        "positive_integer" : r"[0-9]+",
        "white_space" : r"[\n|\t| ]+"
    }
    return tokenizer_regexes[regex]
    
if __name__ == "__main__":
    print(tokenizer("if \nwhile _var1 not_ok not_ok\nOk_2"))