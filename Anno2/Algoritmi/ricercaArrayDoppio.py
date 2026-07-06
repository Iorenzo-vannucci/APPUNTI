def ricerca(A, i, f):
    #print(i, f)
    if i>f:
        return -1
    else:
        mid= (i+f)//2
        #print("1:   "+str(A[mid+1]),"-1:   "+str(A[mid-1]))
        if A[mid] == A[mid+1] or A[mid]==A[mid-1]:
            
            return mid

        else:
            if mid == A[mid]:
                return ricerca(A, i, mid-1)
            else:
                return ricerca (A, mid+1, f)
            

array = [1,2,3,4,5,6,7,8,8,9]
a = ricerca(array, 0, len(array))
print(a)
