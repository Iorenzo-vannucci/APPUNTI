#!/bin/env python3

# Ciphertext C (dall'output fornito)
C_str = ["lc3b", "?4Cd", "I}rC", "STm{"]
C = [list(row) for row in C_str]

# --- Funzioni ausiliarie (originali e inverse) ---

def transpose(v):
    # Assicura che v non sia vuota e le righe abbiano la stessa lunghezza
    if not v or not v[0]:
        return []
    rows = len(v)
    cols = len(v[0])
    # Crea la matrice trasposta
    transposed_v = [['' for _ in range(rows)] for _ in range(cols)]
    for i in range(rows):
        for j in range(cols):
            transposed_v[j][i] = v[i][j]
    return transposed_v

def rotate(v, k):
    """Shift circolare a SINISTRA di k posizioni (come nell'originale)"""
    n = len(v)
    if n == 0:
        return []
    k = k % n # Normalizza k
    return v[k:] + v[:k]

def unrotate(v, k):
    """Shift circolare a DESTRA di k posizioni (inverso di rotate)"""
    n = len(v)
    if n == 0:
        return []
    k = k % n # Normalizza k
    # Shift a destra di k è come shift a sinistra di n-k
    # return rotate(v, n - k)
    # Oppure implementazione diretta: sposta gli ultimi k elementi all'inizio
    return v[-k:] + v[:-k]

# --- Funzione di Decifratura ---
def decipher(C_in, K_guess):
    # Crea una copia per non modificare l'originale
    M_prime = [row[:] for row in C_in]

    # Inverti il secondo round (prima transpose, poi unrotate)
    M_prime = transpose(M_prime)
    for i in range(len(K_guess)):
        M_prime[i] = unrotate(M_prime[i], K_guess[i])

    # Inverti il primo round (prima transpose, poi unrotate)
    M_prime = transpose(M_prime)
    for i in range(len(K_guess)):
        M_prime[i] = unrotate(M_prime[i], K_guess[i])

    return M_prime

# --- Brute-force della chiave K ---
print("Inizio brute-force della chiave K...")
found = False
for k0 in range(4): # K[0]
    for k1 in range(4): # K[1]
        for k2 in range(4): # K[2]
            for k3 in range(4): # K[3]
                K_guess = [k0, k1, k2, k3]

                # Esegui la decifratura con la chiave K_guess
                M_potential = decipher(C, K_guess)

                # Ricostruisci il potenziale flag dalla matrice M_potential
                potential_flag = "".join(["".join(row) for row in M_potential])

                # Controlla se il flag sembra plausibile (es. contiene '{' e '}')
                # Questo è un controllo euristico, potrebbe dover essere adattato
                if '{' in potential_flag and '}' in potential_flag:
                    print(f"\nPotenziale chiave trovata: K = {K_guess}")
                    print(f"Flag decifrato corrispondente: {potential_flag}")
                    found = True
                    # Se ci aspettiamo una sola soluzione, possiamo fermarci
                    # break # Rompe il ciclo k3
            # if found: break # Rompe il ciclo k2
        # if found: break # Rompe il ciclo k1
    # if found: break # Rompe il ciclo k0

if not found:
    print("\nNessuna chiave trovata che produca un flag contenente '{' e '}'.")

print("Brute-force completato.")