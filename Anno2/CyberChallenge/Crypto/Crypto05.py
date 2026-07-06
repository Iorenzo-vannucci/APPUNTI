ciphertext = bytes.fromhex("104e137f425954137f74107f525511457f5468134d7f146c4c")

# Testiamo tutte le possibili chiavi (da 0 a 255)
for key in range(256):
    decrypted = bytes(c ^ key for c in ciphertext)
    
    # Verifichiamo se il risultato è leggibile (solo caratteri ASCII stampabili)
    if all(32 <= c <= 126 or c in (10, 13) for c in decrypted):  
        print(f"Chiave: {key} -> Testo decifrato: {decrypted.decode(errors='ignore')}")


