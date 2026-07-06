#!/usr/bin/env python3
import socket

def main():
    # Parametri LCG noti
    m = 2115495185
    n = 2147483647
    v0 = 1680462708
    v1 = 77243019
    
    # Calcolo il parametro c
    c = (v1 - (m * v0) % n) % n
    print(f"Parametro c calcolato: {c}")
    
    # Connessione al servizio
    host = "gtn2.challs.cyberchallenge.it"
    port = 9061
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    
    # Leggi l'output iniziale
    initial_data = b""
    while True:
        data = sock.recv(1024)
        initial_data += data
        if b"v[2] =" in data:
            break
    
    print(initial_data.decode())
    
    # Calcola i prossimi 50 valori partendo da v[1]
    next_value = v1
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