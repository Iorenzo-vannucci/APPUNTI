from Cryptodome.Cipher import ChaCha20
from Cryptodome.Util import Padding

# Chiave di 32 byte (256 bit) in formato esadecimale
key = bytes.fromhex('f4043af01b201a49d5d88f7ac96a09e022239a534614124e44a631b1fc2318ad')

# Nonce di 8 byte in formato esadecimale
nonce = bytes.fromhex('9c68bca1167160ad')

# Testo cifrato in formato esadecimale
ciphertext = bytes.fromhex('720517fe40a5af5bc0222d954a8b33b36d088ac13fbd2c2bc963ae12')

# Inizializzare il cifrario ChaCha20 con la chiave e il nonce
cipher = ChaCha20.new(key=key, nonce=nonce)

# Decifrare il testo cifrato
plaintext = cipher.decrypt(ciphertext)

# Stampare il testo decifrato
print("Plaintext:", plaintext.decode())