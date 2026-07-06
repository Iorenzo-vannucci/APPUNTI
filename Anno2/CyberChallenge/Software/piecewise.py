from pwn import *
import struct
import re

# Connect to the server
host = "piecewise.challs.cyberchallenge.it"
port = 9110
conn = remote(host, port)

def handle_empty_line():
    print("Sending empty line")
    conn.sendline(b'')  # Send just a newline (0x0a)

while True:
    try:
        line = conn.recvline().decode().strip()
    except EOFError:
        break
    print(f"Received: {line}")

    if "Please send me an empty line" in line:
        handle_empty_line()
        continue

    # Handle number conversion requests
    match = re.match(r'Please send me the number (\d+) as a (\d+)-bit (big|little)-endian integer', line)
    if match:
        num = int(match.group(1))
        bits = int(match.group(2))
        endian = match.group(3)

        fmt = '>' if endian == 'big' else '<'
        fmt += 'I' if bits == 32 else 'Q'

        try:
            converted = struct.pack(fmt, num)
            conn.send(converted)
            print(f"Sent: {converted.hex()}")
        except struct.error as e:
            print(f"Error packing number: {e}")
            break
        continue

    # Handle actual empty line request (no text)
    if not line:
        handle_empty_line()
        continue

conn.close()