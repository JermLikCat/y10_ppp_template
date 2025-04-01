# testing
def is_odd(num):
    counter = 0
    even = True
    while counter < num:
        counter += 1
        if even:
            even = False
        else:
            even = True
    return not even

