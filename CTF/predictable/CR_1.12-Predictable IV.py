import binascii

iv = bytes.fromhex(input('Insert the IV generated: '))
old = b'login_token:0000'
new = b'login_token:admi'

difference = bytearray([a^b for a,b in zip(old, new)])

new_iv = bytearray([a^b for a,b in zip(iv, difference)])
print(binascii.hexlify(new_iv))