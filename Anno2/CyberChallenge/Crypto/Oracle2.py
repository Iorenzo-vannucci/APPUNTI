from pwn import *
from Crypto.Util.number import inverse, long_to_bytes, GCD

def get_encryption(r, m):
    """
    Invia il comando per cifrare il valore m e restituisce il ciphertext.
    """
    r.sendline(b"1")
    r.recvuntil(b"Plaintext > ")
    r.sendline(str(m).encode())
    r.recvuntil(b"Encrypted: ")
    return int(r.recvline().strip())

def main():
    r = remote("oracle.challs.cyberchallenge.it", 9042)
    
    r.recvuntil(b"Encrypted flag: ")
    encrypted_flag = int(r.recvline().decode().strip())
    log.info(f"Encrypted flag (C) = {encrypted_flag}")
    
    # =========================
    # Recupero del modulo n
    # =========================
    # Dato che:
    # x mod n = x - k • n for some integer value of k >= 0 (proprietà del modulo)
    # Quindi --> encrypt(x)^2 - encrypt(x^2) is equal to (x^e mod n)^2 - (x^2e mod n)
    # Senza modulo i valori sono uguali, ma passati all'oracolo la loro differenza è multiplo di n
    # Quindi possiamo calcolare n come gcd(encrypt(a)^2 - encrypt(a^2), encrypt(b)^2 - encrypt(b^2))
    # =========================
    # Presi quindi due valori a e b, calcoliamo:
    # encrypt(a)^2 - encrypt(a^2) = k1 * n
    # encrypt(b)^2 - encrypt(b^2) = k2 * n
    # Per a = 2:
    c2 = get_encryption(r, 2)
    c4 = get_encryption(r, 4)
    d1 = c2**2 - c4
    log.info(f"d1 (da a=2) = {d1}")
    
    # Per b = 3:
    c3 = get_encryption(r, 3)
    c9 = get_encryption(r, 9)
    d2 = c3**2 - c9
    log.info(f"d2 (da b=3) = {d2}")
    
    # Calcoliamo n = gcd(d1, d2), eseguire lo script diverse volte 
    # affinché gcd(k1,k2) = 1, altrimenti non worka
    n = GCD(d1, d2)
    log.info(f"Modulo n recuperato = {n}")
    
    # ============================================
    # Attacco: recuperiamo la flag sfruttando l'omomorfismo
    # ============================================
    # Per aggirare il controllo (che blocca se il messaggio decriptato è multiplo di un valore in used)
    # scegliamo r = 2^-1 mod n, in modo tale che:
    # decrypt(encrypted_flag * encrypt(2^{-1})) = flag * 2^{-1} mod n
    # e poi flag = (flag * 2^{-1}) * 2 mod n.
    
    # Calcoliamo l'inverso modulare di 2 modulo n
    inv2 = inverse(2, n)
    log.info(f"inv2 (mod n) = {inv2}")
    
    # Chiediamo l'encryption di inv2
    c_inv2 = get_encryption(r, inv2)
    log.info(f"Ciphertext di inv2 = {c_inv2}")
    
    # Costruiamo il "falso ciphertext":
    # C' = encrypted_flag * c_inv2
    manipulated_ciphertext = encrypted_flag * c_inv2
    log.info(f"Manipulated ciphertext = {manipulated_ciphertext}")
    
    # Richiediamo la decryption del ciphertext manipolato
    r.sendline(b"2")
    r.recvuntil(b"Ciphertext > ")
    r.sendline(str(manipulated_ciphertext).encode())
    r.recvuntil(b"Decrypted: ")
    decrypted_value = int(r.recvline().decode().strip())
    log.info(f"Decrypted value (flag * inv2 mod n) = {decrypted_value}")
    
    # Recuperiamo la flag: flag = (decrypted_value * 2) mod n
    flag_num = (decrypted_value * 2) % n
    flag = long_to_bytes(flag_num)
    log.success(f"FLAG recuperata = {flag}")
    
    r.close()

if __name__ == "__main__":
    main()