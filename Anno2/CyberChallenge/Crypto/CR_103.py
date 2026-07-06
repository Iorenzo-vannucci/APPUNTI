from pwn import * #type: ignore
from binascii import unhexlify
import string

def send_and_get_ciphertext(password):
    p.sendlineafter("Give me the password to encrypt:", password)
    p.recvline()  # Salta la riga vuota
    enc_line = p.recvline().strip().decode()
    return enc_line.split(": ")[1]  # Estrae solo il testo cifrato

def brute_force_flag():
    known_flag = ""
    block_size = 16  # AES usa blocchi da 16 byte
    
    for i in range(1, block_size + 1):
        padding = "A" * (block_size - i)
        reference_cipher = send_and_get_ciphertext(padding)[:block_size * 2]
        
        for c in string.printable:
            test_input = padding + known_flag + c
            test_cipher = send_and_get_ciphertext(test_input)[:block_size * 2]
            
            if test_cipher == reference_cipher:
                known_flag += c
                print(f"Flag trovata finora: {known_flag}")
                break
    
    return known_flag

if __name__ == "__main__":
    p = process(["python3", "server.py"])  # Sostituisci con il comando corretto se remoto
    flag = brute_force_flag()
    print(f"FLAG: {flag}")
    p.close()
