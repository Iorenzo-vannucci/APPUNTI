from pwn import *
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.number import long_to_bytes

def main():
    # Connect to the service
    conn = remote('carol.challs.cyberchallenge.it', 9045)

    # Parse initial parameters
    conn.recvuntil(b"p: ")
    p = int(conn.recvline().strip())
    conn.recvuntil(b"pubA: ")
    pubA = int(conn.recvline().strip())
    conn.recvuntil(b"pubB: ")
    pubB = int(conn.recvline().strip())
    conn.recvuntil(b"Encrypted flag: ")
    encrypted_flag = bytes.fromhex(conn.recvline().strip().decode())

    # Proceed to interaction phase
    conn.recvuntil(b"Enter your prime: ")
    conn.sendline(str(p).encode())
    conn.recvuntil(b"Enter the generator: ")
    conn.sendline(str(pubA).encode())
    conn.recvuntil(b"Enter your public value: ")
    conn.sendline(b"1")
    conn.recvuntil(b"Enter your message: ")
    conn.sendline(b"a")  # Any message works

    # Get Bob's pubB from the interaction
    conn.recvuntil(b"pubB: ")
    shared_secret = int(conn.recvline().strip())

    # Derive the AES key
    key = hashlib.sha256(long_to_bytes(shared_secret)).digest()[:16]
    cipher = AES.new(key, AES.MODE_ECB)
    # Decrypt the flag (assuming PKCS#7 padding)
    flag = cipher.decrypt(encrypted_flag)
    print("Decrypted Flag:", flag)

if __name__ == "__main__":
    main()