import inflect

p = inflect.engine()
lines = []
for i in range(49):
    one = p.number_to_words(i)
    for y in range(49):
        two = p.number_to_words(y)
        res = i+y
        lines.append(f"\nWhat is {one} plus {two}? : {p.number_to_words(res)}, {res}".lower())

with open(r"challenges.txt", "a") as f:
    f.writelines(lines)