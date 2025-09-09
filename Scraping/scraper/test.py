tokens = ["this", "is-a", "test"]
for t in range(len(tokens)):
    print(t)
    if len(tokens[t]) <= 1 or tokens[t] == "\n":
        continue
    splitTokens = tokens[t].split("-")
    print(tokens)
    if len(splitTokens) > 1:
        del tokens[t]
        for token in range(len(splitTokens)-1,-1,-1):
            if len(splitTokens[token]) > 0:
                tokens.insert(t, splitTokens[token])

print(tokens)