import requests
import binascii

BASE_URL = "https://aes.cryptohack.org/flipping_cookie/"

# 1. Get the encrypted cookie
response = requests.get(f"{BASE_URL}/get_cookie/")
data = response.json()

# 2. Extract IV and ciphertext
original_iv = bytearray.fromhex(data["cookie"][:32])
ciphertext = data["cookie"][32:]

print(f"Original IV: {binascii.hexlify(original_iv).decode()}")
print(f"Ciphertext: {ciphertext}")

# 3. Create a modified IV to flip 'False' to 'True'
# The string "admin=False;" starts at position 0 in the plaintext
# We need to flip bits in the IV at positions where 'F' (0x46) becomes 'T' (0x54)
# and 'a' (0x61) becomes 'r' (0x72), etc.

# Original: 'a' 'd' 'm' 'i' 'n' '=' 'F' 'a' 'l' 's' 'e' ';' ...
# Target:   'a' 'd' 'm' 'i' 'n' '=' 'T' 'r' 'u' 'e' ';' ...

# Calculate XOR between original and target bytes at positions 6-10
modified_iv = bytearray(original_iv)

# Position 6: 'F' (0x46) -> 'T' (0x54)
modified_iv[6] ^= 0x46 ^ 0x54

# Position 7: 'a' (0x61) -> 'r' (0x72)
modified_iv[7] ^= 0x61 ^ 0x72

# Position 8: 'l' (0x6C) -> 'u' (0x75)
modified_iv[8] ^= 0x6C ^ 0x75

# Position 9: 's' (0x73) -> 'e' (0x65)
modified_iv[9] ^= 0x73 ^ 0x65

# Position 10: 'e' (0x65) -> ';' (0x3B)
modified_iv[10] ^= 0x65 ^ 0x3B

# 4. Send the modified IV with the original ciphertext
modified_iv_hex = binascii.hexlify(modified_iv).decode()
response = requests.get(f"{BASE_URL}/check_admin/{ciphertext}/{modified_iv_hex}/")
result = response.json()

print("🚩 Result with modified IV:", result)
