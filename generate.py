result = [[None for i in range(64)] for j in range(64)]
for x1 in range(8):
    for y1 in range(8):
        for x2 in range(x1, 8):
            for y2 in range(y1, 8):
                current = [["0", "0", "0", "0", "0", "0", "0", "0"] for _ in range(8)]
                
                if abs(y2 - y1) == 0 and abs(x2 - x1) >= 0:
                    current[y1][x1] = "1"
                    for i in range(x2 - x1):
                        current[y1][x1 + i + 1] = "1"
                elif abs(y2 - y1) >= 1 and abs(x2 - x1) == 0:
                    current[y1][x1] = "1"
                    for i in range(y2 - y1):
                        current[y1 + i + 1][x1] = "1"
                elif abs(y2 - y1) >= 1 and abs(x2 - x1) >= 1 and abs(x2 - x1) == abs(y2 - y1):
                    current[y1][x1] = "1"
                    if y2 - y1 > 0:
                        for i in range(y2 - y1):
                            current[y1 + i + 1][x1 + i + 1] = "1"
                    else:
                        for i in range(abs(y2 - y1)):
                            current[y1 - i - 1][x1 - i - 1] = "1"
                current1 = []
                for i in current:
                    current1 += i
                current1 = "".join(current1)
                current1 = hex(int(current1, 2))
                if current1 != hex(0) and not (x2 == x1 and y2 == y1):
                    result[x1 + y1 * 8][x2 + y2 * 8] = current1
                else:
                    result[x1 + y1 * 8][x2 + y2 * 8] = None
                    
                    
print ("[", end="")
for list in result:
    print ("[", end="")
    final = ""
    for element in list:
        final += str(element) + "," + " "
    final = final[:-2]
    print(final, end="")
    print ("],", end="")
    print()
    
print ("]", end="")