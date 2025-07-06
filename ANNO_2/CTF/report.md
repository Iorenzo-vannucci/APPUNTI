# Cha-Cha Binary Analysis Report

## Program Structure

The program consists of two main functions:

1. `main` (0x00101289)
2. `encrypt_string` (0x00101209)

### Main Function Analysis

The main function:
1. Takes a command line argument as input (the flag)
2. Allocates memory for the output buffer
3. Calls `encrypt_string` to process the input
4. Compares the result with a stored value
5. Prints "You got it!" if the comparison matches, otherwise "Learn to move properly"

### Encryption Function Analysis

The `encrypt_string` function implements a recursive encryption algorithm:

1. Takes three parameters:
   - input: pointer to input string
   - output: pointer to output buffer
   - index: current position in the string

2. For each character:
   - Calculates a rotation value based on the character's position (index)
   - The rotation is limited to values 0-7 using modulo
   - Performs a circular bit rotation on the character
   - Recursively processes the next character

The encryption can be described as:
```c
output[i] = (input[i] >> rot) | (input[i] << (8 - rot))
where rot = index & 7
```

## Encrypted Flag

The encrypted flag was found at address 0x2038:
```
43a1 528a b71b a168 5fb1 1a86 f593 ccc2 6caf dcad 037b d1d0 5fb2 4de6 7399 91c2
```

## Solution

The program uses the length of the input string to determine how many bytes to compare in the `memcmp` function. This means we need to provide the flag without the closing brace, as the stored encrypted bytes don't include it.

Here's the Python script used to decrypt the flag:

```python
def decrypt_char(c, pos):
    # Get rotation value for this position (0-7)
    rot = pos & 7
    # Reverse the rotation by rotating left instead of right
    return ((c << rot) | (c >> (8 - rot))) & 0xFF

def decrypt_flag():
    # Encrypted flag bytes
    enc = bytes.fromhex("43a1528ab71ba1685fb11a86f593ccc26cafdcad037bd1d05fb24de6739991c2")
    
    # Decrypt each byte
    flag = ""
    for i in range(len(enc)):
        dec = decrypt_char(enc[i], i)
        flag += chr(dec)
    
    return flag
```

The decryption works by:
1. Taking each byte of the encrypted flag
2. Calculating the rotation value based on its position (same as encryption)
3. Performing the reverse rotation (left instead of right)
4. Converting the resulting byte to a character

Running this script reveals the flag:
```
CCIT{ch4_ch4_r3al_sm0oth_e5773da
```

Note: While the flag format typically includes a closing brace, in this case we need to provide it without the closing brace to match the binary's comparison. This is because the program uses the length of our input to determine how many bytes to compare, and the stored encrypted bytes don't include an encrypted version of the closing brace.

The challenge name "cha-cha" appears to be a reference to both the ChaCha cipher (though this isn't actually ChaCha) and the fact that the encryption performs a "dance" of bit rotations based on position.

## Next Steps

1. Extract the target encrypted value from the binary
2. Implement a decryption function that reverses the bit rotation
3. Run the decryption on the target value to recover the flag 