#!/usr/bin/env python3

from Crypto.Cipher import AES
import binascii
import string

# Informazioni dal challenge
msg = "AES with CBC is very unbreakable"
plaintext = msg.encode()

# Secondo blocco noto
second_block_p = "very unbreakable".encode()
second_block_cipher = bytes.fromhex("78c670cb67a9e5773d696dc96b78c4e0")

key = ""
missing = ""

# Brute-force per trovare i 2 caratteri mancanti della chiave
for i in string.ascii_letters + string.digits:
    for j in string.ascii_letters + string.digits:
        key_try = f"yn9RB3Lr43xJK2{i}{j}"
        cipher = AES.new(key_try.encode(), AES.MODE_ECB)
        decrypted = cipher.decrypt(second_block_cipher)
        # Ricostruzione del primo blocco ciphertext
        first_cipher_block = bytes(a ^ b for a, b in zip(second_block_p, decrypted))
        hex_block = binascii.hexlify(first_cipher_block).decode()
        if hex_block.startswith("c5") and hex_block.endswith("d49e"):
            key = key_try
            missing = hex_block
            print(f"[+] Chiave trovata: {key}")
            break
    if key:
        break

if not key:
    print("[-] Nessuna chiave trovata.")
    exit(1)

# Ricostruiamo il ciphertext completo
full_ciphertext = bytes.fromhex(missing + "78c670cb67a9e5773d696dc96b78c4e0")

# Calcoliamo il IV tramite decrittazione del primo blocco
cipher = AES.new(key.encode(), AES.MODE_ECB)
decrypted_first_block = cipher.decrypt(full_ciphertext[:16])

iv = bytes(a ^ b for a, b in zip(decrypted_first_block, plaintext[:16]))

# Stampa dei risultati
print(f"[+] IV (hex): {binascii.hexlify(iv).decode()}")

try:
    iv_ascii = iv.decode()
    print(f"[+] IV (ASCII): {iv_ascii}")
    print(f"[+] Flag (ASCII IV): CCIT{{{iv_ascii}}}")
except UnicodeDecodeError:
    print("[!] IV non decodificabile in ASCII.")

# Flag finale in formato hex
print(f"[+] Flag (hex IV): CCIT{{{binascii.hexlify(iv).decode()}}}")