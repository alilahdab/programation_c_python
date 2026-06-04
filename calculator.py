def add(a,b):
    return a+b
def sub(a,b):
    return a-b
def mul(a,b):
    return a*b
def div(a,b):
    if b!=0:
        return a/b
    return "erreure"
while True:
    print("--- Nouvelle Operation ---")
    a = float(input("Enter a number: "))
    op = input("enter an operator(+,-,*,/):")
    b = float(input("Enter another number: "))
    if op=="+":
     print(add(a,b))
    elif op=="-":
     print(sub(a,b))
    elif op=="*":
        print(mul(a,b))
    elif op=="/":
        print(div(a,b))
    else:
        print("l'opperateure n'existe pas!")

