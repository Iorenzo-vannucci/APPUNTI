from Cryptodome.Cipher import DES
from Cryptodome.Util.Padding import pad

# Use the CORRECT KEY from the problem
key = bytes.fromhex('46819bc367ad76c4')  # Fix: Updated key
iv = bytes.fromhex('0123456789abcdef')   # IV you provided

plaintext = 'La lunghezza di questa frase non è divisibile per 8'.encode()

# Apply X923 padding correctly
padded_plaintext = pad(plaintext, 8, style='x923')  # Adds 4 bytes (e.g., 00 00 00 04)

# Encrypt with DES-CBC
cipher = DES.new(key, DES.MODE_CBC, iv)
ciphertext = cipher.encrypt(padded_plaintext)

print("Ciphertext (hex):", ciphertext.hex())
print("IV (hex):", iv.hex())