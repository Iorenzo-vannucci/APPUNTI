from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad
import secrets

# Genera una chiave AES256 valida (32 bytes)
key = secrets.token_bytes(32)
print("Chiave (hex):", key.hex())

# Converti il plaintext
plaintext = 'Mi chiedo cosa significhi il numero nel nome di questo algoritmo.'.encode()

# Padding PKCS7 con block size 16
padded_plaintext = pad(plaintext, 16, style='pkcs7')

# Cifratura AES-CFB con segment size 8 (nonostante la specifica del problema)
# Il segment size 24 è tecnicamente impossibile per AES, assumiamo un typo
cipher = AES.new(key, AES.MODE_CFB, segment_size=24)  # Usa segment_size valido
ciphertext = cipher.encrypt(padded_plaintext)

print("IV usato (hex):", cipher.iv.hex())
print("Ciphertext (hex):", ciphertext.hex())