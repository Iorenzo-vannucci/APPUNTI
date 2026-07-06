#RICERCA BINARIA PER BUONANOTTE
def cerca(A, i, f):
    if i > f:
        return -1  # Caso base: non trovato
    
    mid = (i + f) // 2  # Divisione intera per ottenere un indice valido
    
    # Controllo se `mid+1` è valido prima di accedere
    if mid + 1 < len(A) and isinstance(A[mid], str) and isinstance(A[mid + 1], int): #CONTROLLO CARATTERE
        return mid
    else:
        if isinstance(A[mid], str):
            return cerca(A, mid + 1, f)  # Cerca nella parte destra
        else:
            return cerca(A, i, mid - 1)  # Cerca nella parte sinistra

array = ["b", "u", "o", "n", "a", "n", "o", "t", "t", 7, 2, 0, 2, 3]

# Chiamata alla funzione
indice = cerca(array, 0, len(array) - 1)
print(array[9])
print(f"Indice trovato: {indice}" if indice != -1 else "Nessuna transizione trovata")