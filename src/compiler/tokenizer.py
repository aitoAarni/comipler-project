import re

def add_whitespace_match(regex: str) -> str:
    white_space = r"[\n|\t| ]"
    return white_space + regex + white_space

def get_regex_for_token(regex: str) -> str:
    tokenizer_regexes = {
        "identifier": r"[a-zA-Z|_][a-zA-Z|_|0-9]*",
        "positive_integer" : r"[0-9]+",
    }
    return add_whitespace_match(tokenizer_regexes[regex])
    

def tokenizer(source_code: str="") -> list[str]:
    identifier = get_regex_for_token("identifier")
    positive_integer = get_regex_for_token("positive_integer")
    r = re.compile(rf"{identifier}|{positive_integer}")
    source_code_spaced =  " " + source_code + " "
    previous_match_end = 0
    tokens: list[str] = []
    while (True):
        match = r.search(source_code_spaced, previous_match_end)
        if (not match): break
        print("match:", match)

        previous_match_end = match.end() - 1
        tokens.append(match[0].strip())
    print("break")
    return tokens

if __name__ == "__main__":
    print(tokenizer("if \nwhile _var1 2not_ok .not_ok\nOk_2"))