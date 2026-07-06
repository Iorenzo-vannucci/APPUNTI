def capovolgi(A):
    i=0
    k=len(A)-1
    while(i<k):
            temp=A[k]
            A[k]=A[i]
            A[i]=temp
            i+=1
            k-=1
    

        
D=[1,2,3,4,5]
f=capovolgi(D)
print(D)

