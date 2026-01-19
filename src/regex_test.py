import re

r = re.compile(r"bro[\n|\t| ]+?")

match = r.match("ro   ")

print()
print(match)

search = r.search("the abc book, abbbbc!")

print(search)

findall = r.findall("the abc book, abbbbbc!")

print(findall)