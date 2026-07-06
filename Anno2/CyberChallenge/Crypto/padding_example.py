from Cryptodome.Util.Padding import pad
from Cryptodome.Cipher import AES
import binascii
'''
key = b'Chiave segreta!'
msg = (b'(ciao BOB!)')
block_size= 16

padded_plaintext= pad(msg, block_size, style = 'pkcs7')
cipher1 = AES.new(key, AES.MODE_CBC)
cipher2 = AES.new(key, AES.MODE_CBC)

msg_en1 = cipher1.encrypt(padded_plaintext)
msg_en2 = cipher2.encrypt(padded_plaintext)
#print(len(padded_plaintext))
print(msg_en1)
print(msg_en2)


ec2d332ce82e51ba
344dffacb8e772eb
2b19c2a7650475ca
9ab12131e07724d2
020c376aa2b98978
026ae8e0cf453356
'''

stringa = b'Ciao!'
block_size = 16

padded_data = pad(stringa, block_size, style='pkcs7')
print(padded_data)