A= [1,2,3,4,6]
x=7  
def sommaUgualex(A,x):
    C=[]
    inizio=0
    fine= len(A)-1
    while(inizio<fine):
        if A[inizio]+A[fine] == x:
            s = A[inizio],A[fine]
            C.append(s)
        if A[inizio]+A[fine]>x:
            fine-=1              
        else:
            inizio+=1
                
        
    return C
c=sommaUgualex(A,x)
if(len(c)<1):
        print("non ci sono elementi che danno come somma ", x)
else:
     print(c)

