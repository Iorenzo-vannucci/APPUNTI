array = ['G','G','G','G','G','R','R','R','R','R','R','R','R']

def ric_bin(array, i, f):
    if i > f:
        return -1
    else:
        mid = (i + f) // 2
        if array[mid] == 'G' and (mid + 1 < len(array) and array[mid + 1] == 'R'):
            return mid
        elif array[mid] == 'G':
            return ric_bin(array, mid + 1, f)
        else:
            return ric_bin(array, i, mid - 1)


pos = ric_bin(array, 0, len(array)-1)


print("Numero di palline gialle:", pos + 1 )