for x in range(1,101):
    hit = False
    if x % 3 == 0:
        print("fizz", end="")
        hit = True
    if x % 5 ==0:
        print("buzz", end="")
        hit = True
    if hit:
        print("")
    else:
        print(x)