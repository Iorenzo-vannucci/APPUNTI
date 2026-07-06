#!/usr/bin/env python3
import base64
import sys
from Crypto.Util.number import *
import binascii
import pwn
'''

# import this

if sys.version_info.major == 2:
    print("You are running Python 2, which is no longer supported. Please update to Python 3.")

ords = [81, 64, 75, 66, 70, 93, 73, 72, 1, 92, 109, 2, 84, 109, 66, 75, 70, 90, 2, 92, 79]

print("Here is your flag:")
print("".join(chr(o ^ 0x32) for o in ords))
'''

'print(chr([99, 114, 121, 112, 116, 111, 123, 65, 83, 67, 73, 73, 95, 112, 114, 49, 110, 116, 52, 98, 108, 51, 125]))'
'testo = [99, 114, 121, 112, 116, 111, 123, 65, 83, 67, 73, 73, 95, 112, 114, 49, 110, 116, 52, 98, 108, 51, 125]'
'for c in testo:'
'print(chr(c), end="")'

#print(bytes.fromhex('63727970746f7b596f755f77696c6c5f62655f776f726b696e675f776974685f6865785f737472696e67735f615f6c6f747d'))

#print(base64.b64encode(bytes.fromhex('72bca9b68fc16ac7beeb8f849dca1d8a783e8acf9679bf9269f7bf')))

#num=11515195063862318899931685488813747395775516287289682636499965282714637259206269

#bytes = long_to_bytes(num)

#print("bytes:" + str(bytes))

#stringa = "label"
#num = 13

#xor = ("".join(chr(ord(c) ^ num) for c in stringa))

#print(f"crypto{xor}")
#print(f"crypto{{{xor}}}")

####################################
#             esercizio            #
####################################
'''
KEY1 = bytes.fromhex('a6c8b6733c9b22de7bc0253266a3867df55acde8635e19c73313')
risultato1= bytes.fromhex('37dcb292030faa90d07eec17e3b1c6d8daf94c35d4c9191a5e1e')
print(risultato1)
print(f'KEY1= {KEY1}')

xor1 = bytes(a^b for a,b in zip(KEY1,risultato1))
KEY2 = ((xor1))
print('KEY2 ='+str(KEY2))


risultato2 = bytes.fromhex('c1545756687e7573db23aa1c3452a098b71a7fbf0fddddde5fc1')
xor2 = bytes(a^b for a,b in zip(KEY2, risultato2))


KEY3 = xor2
print(f'KEY3= {KEY3}')

risultato3 = bytes.fromhex('04ee9855208a2cd59091d04767ae47963170d1660df7f56f5faf')
xor3 = bytes(a^b^c^d for a,b,c,d in zip(KEY1,KEY2,KEY3, risultato3))

flag= xor3
print(f'flag{{{flag}}}')'

'''

####################################
#             esercizio            #
####################################
'''
numeroHEX = '73626960647f6b206821204f21254f7d694f7624662065622127234f726927756d'
cifrato = bytes.fromhex(numeroHEX)
print(cifrato)


for key in range(256):
    testo = bytes(c^key for c in cifrato)
    try:
        decoded= testo.decode()
        if 'crypto' in decoded:
            print(f'Chiave: {key}: {decoded}')

    except:
        continue

'''


####################################
#             esercizio            #
####################################
import binascii

from pwn import xor

# Given ciphertext in hex
ciphertext_hex = "0e0b213f26041e480b26217f27342e175d0e070a3c5b103e2526217f27342e175d0e077e263451150104"
ciphertext = bytes.fromhex(ciphertext_hex)

print('provaChiave:',xor(ciphertext, 'crypto{'.encode()))
print('stringa finale:', xor(ciphertext, 'myXORkey'.encode()))


a = mcd(1,2)
print(f'a={a}')
