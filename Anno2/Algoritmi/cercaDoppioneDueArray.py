def ricercaBin(A,i,f,key):
    if i>f :
        return -1
    else:
        mid =(i+f)//2
        if(A[mid]==key):
            return A[mid]
        else:
            if A[mid]>key:
                return ricercaBin(A,i,mid-1,key)
            else:
                return ricercaBin(A,mid+1,f,key)

a = [1,33,44,56,78,99]
b = [20,33,45,56,80]
C=[]

for elemento in range (0,len(a)-1):
    trovato=ricercaBin(b,0,len(b)-1, a[elemento] )
    if(trovato!=-1):
        C.append(trovato)

print(C.reverse)