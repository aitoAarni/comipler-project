import re

def tokenizer(source_code: str="") -> list[str]:
    r = re.compile(r"[1-9]+")

    tokens: list[str] = r.findall(source_code)
    return tokens
