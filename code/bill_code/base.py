text = "=VLOOKUP(A4918,'[income_0601-1002.xlsx]Order details'!$A:$AX,{},FALSE)"
for i in range(4,30):
    print(text.format(i))