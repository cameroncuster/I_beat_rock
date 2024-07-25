def int_to_base26(n):
    if n == 0:
        return "a"

    letters = []
    while n:
        n, r = divmod(n, 26)
        letters.append(chr(r + 97))

    return "".join(reversed(letters))
