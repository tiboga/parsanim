cena = 0
inp = input()
while inp != '':
    cena += float(inp)
    inp = input()
cents = float(str(cena).split('.')[1]) % 5
print(cents)
if cents < 2.5:
    
    print(str(cena).split('.')[0] + str(cena).split('.')[1])