

def mcd(a, b):
    while b:
        a, b = b, a % b
        print(a,b)
    return a


print(mcd( 66528,52920))  # Output: 6
        


        


    
