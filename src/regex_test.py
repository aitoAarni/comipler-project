import re

r = re.compile(r"ab+c")

match = r.fullmatch('abbbbbbbbbbc')

print(match)

search = r.search("the abc book, abbbbc!")

print(search)

findall = r.findall("the abc book, abbbbbc!")

print(findall)