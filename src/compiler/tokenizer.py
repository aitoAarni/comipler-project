import re

def tokenizer(source_code: str="") -> list[str]:
    white_space = r"[\n|\t| ]"
    identifier = r"[a-zA-Z|_][a-zA-Z|_|0-9]*"
    positive_integer = r"[0-9]+"
    r = re.compile(rf"{white_space}{identifier}{white_space}|"
                   rf"{white_space}{positive_integer}{white_space}")

    source_code_spaced =  " " + source_code + " "
    previous_match_end = 0
    tokens: list[str] = []
    while (True):
        match = r.search(source_code_spaced, previous_match_end)
        if (not match): break
        print("match:", match[0])

        previous_match_end = match.end() - 1
        tokens.append(match[0].strip())
    print("break")
    return tokens

if __name__ == "__main__":
    print(tokenizer("if \nwhile _var1 2not_ok .not_ok\nOk_2"))