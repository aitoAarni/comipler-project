import re

r = re.compile(r"hello +there!*?")

match = r.fullmatch("")

print(match)

search = r.search("llo")

print(search)

findall = r.findall("Just a text hello! here to say 'llo' or helnah ! hell")

print(findall)