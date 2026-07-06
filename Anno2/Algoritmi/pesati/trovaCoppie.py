def trova_coppia_con_somma_x(A, inizio, fine, x):
    if inizio >= fine:
        return None  # Nessuna coppia trovata

    somma = A[inizio] + A[fine]

    if somma == x:
        return (A[inizio], A[fine])
    elif somma > x:
        return trova_coppia_con_somma_x(A, inizio, fine - 1, x)
    else:
        return trova_coppia_con_somma_x(A, inizio + 1, fine, x)
    

A = [1, 3, 5, 6, 8, 10]
x = 14
risultato = trova_coppia_con_somma_x(A, 0, len(A) - 1, x)

if risultato:
    print(f"Coppia trovata: {risultato}")
else:
    print("Nessuna coppia trovata")