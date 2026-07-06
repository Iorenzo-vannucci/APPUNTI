from pwn import *
from Crypto.Util.number import long_to_bytes

def main():
    # Connettiamo al server (modifica l'host/porta se necessario)
    r = remote("oracle.challs.cyberchallenge.it", 9044)
    
    # Leggiamo la linea con "Encrypted flag: " e ne estraiamo il valore
    r.recvuntil(b"Encrypted flag: ")
    encrypted_flag = int(r.recvline().decode().strip())
    log.info(f"Encrypted flag (C) = {encrypted_flag}")
    
    # -------------------------------------------------------------------
    # Recupero del modulo n usando la proprietà con -1:
    #
    # Siccome (-1)^e mod n = -1 mod n, allora:
    #   decrypt(-1) = (-1)^d mod n = -1 mod n = n - 1.
    # Quindi: n = decrypt(-1) + 1.
    # -------------------------------------------------------------------
    r.sendline(b"2")  # Scegliamo l'opzione "Decrypt"
    r.recvuntil(b"Ciphertext > ")
    r.sendline(b"-1")
    r.recvuntil(b"Decrypted: ")
    dec_minus1 = int(r.recvline().strip())   # n - 1
    log.info(f"decrypt(-1) = {dec_minus1}")
    
    n = dec_minus1 + 1
    log.info(f"Recovered modulus n = {n}")
    
    # -------------------------------------------------------------------
    # Recupero della flag usando la proprietà con -flag:
    #
    # Poiché:
    #   (-flag)^e mod n = -flag^e mod n = -encrypt(flag) mod n,
    # allora:
    #   decrypt(-encrypt(flag)) = (-flag)^(e*d) mod n = -flag mod n = n - flag. # n - 1 se avessi mandato -1
    # Quindi: flag = n - decrypt(-encrypt(flag)).
    # -------------------------------------------------------------------
    # Prepariamo il valore da decriptare: -encrypt(flag)
    neg_enc_flag = -encrypted_flag  # in Python, -encrypted_flag è un intero negativo
    r.sendline(b"2")
    r.recvuntil(b"Ciphertext > ")
    r.sendline(str(neg_enc_flag).encode())
    r.recvuntil(b"Decrypted: ")
    dec_neg_enc_flag = int(r.recvline().strip())
    log.info(f"decrypt(-encrypt(flag)) = {dec_neg_enc_flag}")
    
    flag_num = n - dec_neg_enc_flag
    flag = long_to_bytes(flag_num)
    log.success(f"Recovered flag: {flag}")
    
    r.close()

if __name__ == "__main__":
    main()