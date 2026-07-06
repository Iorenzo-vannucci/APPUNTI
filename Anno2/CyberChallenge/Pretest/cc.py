def f(n):
    res = 0
    for i in range(n + 1):  # Loop from 0 to n (inclusive)
        t = n
        while t > 0:
            if i == t:
                res = res << 1  # Left shift res by 1
                res = res + ((i >> 1) & 1)  # Add the least significant bit of i shifted right by 1
            t = t >> 1  # Right shift t by 1
    return res

a = f(202520252025)
print(a)