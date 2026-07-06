#!/usr/bin/env python3
import socket

def main():
    # Parametri dati
    n = 2147483647
    v0 = 125778740
    v1 = 513146825
    v2 = 1999511474
    
    # Calcola i parametri m e c del generatore LCG
    # Risolvere il sistema:
    # v1 = (m * v0 + c) % n
    # v2 = (m * v1 + c) % n
    
    # Da cui si ricava:
    # (v1 - v2) = m * (v0 - v1) % n
    
    # Calcolare l'inverso modulare di (v0 - v1) % n
    def mod_inverse(a, m):
        g, x, y = extended_gcd(a % m, m)
        if g != 1:
            raise Exception('Modular inverse does not exist')
        else:
            return x % m
    
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        else:
            gcd, x, y = extended_gcd(b % a, a)
            return gcd, y - (b // a) * x, x
    
    # Calcolo di m
    diff = (v0 - v1) % n
    inv = mod_inverse(diff, n)
    m = ((v1 - v2) % n * inv) % n
    
    # Calcolo di c
    c = (v1 - (m * v0) % n) % n
    
    print(f"Parametri calcolati: m = {m}, c = {c}")
    
    # Verifica che i parametri siano corretti
    test_v2 = (m * v1 + c) % n
    print(f"Verifica v2: calcolato = {test_v2}, atteso = {v2}")
    
    # Connessione al servizio
    host = "gtn3.challs.cyberchallenge.it"
    port = 9062
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    
    # Leggi l'output iniziale
    initial_data = b""
    while True:
        data = sock.recv(1024)
        initial_data += data
        if b"v[3] =" in data:
            break
    
    print(initial_data.decode())
    
    # Calcola i prossimi 50 valori partendo da v[2]
    next_value = v2
    values = []
    
    for i in range(50):
        next_value = (m * next_value + c) % n
        values.append(str(next_value))
    
    # Invia i valori al servizio
    for val in values:
        sock.send((val + "\n").encode())
        response = sock.recv(1024)
        print(response.decode())
    
    sock.close()

if __name__ == "__main__":
    main() 