from Crypto.Util.number import *
n1 = 66528
n2 = 52920
print(f'il MCD tra {n1} e {n2} è: {mcd(n1,n2)}')



def extended_euclidean(a, b):
    if b == 0:
        return a, 1, 0  # Caso base: gcd(a, 0) = a, con coefficienti (1, 0)
    
    gcd, x1, y1 = extended_euclidean(b, a % b)  # Chiamata ricorsiva
    
    x = y1
    y = x1 - (a // b) * y1
    
    return gcd, x, y

# Valori dati
p = 56
q = 141

gcd, u, v = extended_euclidean(p, q)
print(f"gcd({p}, {q}) = {gcd}")
print(f"u = {u}, v = {v}")

x = 8146798528947
reminder = x%17
print(reminder)