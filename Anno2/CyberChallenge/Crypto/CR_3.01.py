#!/usr/bin/env python3
import socket

def main():
    # Parametri LCG
    m = 1076867677
    c = 1265354953
    n = 2147483647
    
    # Connessione al servizio
    host = "gtn1.challs.cyberchallenge.it"
    port = 9060
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    
    # Leggi l'output iniziale
    initial_data = b""
    while True:
        data = sock.recv(1024)
        initial_data += data
        if b"v[0] =" in data:
            break
    
    print(initial_data.decode())
    
    # Estrai il valore del seme (s) dall'output
    lines = initial_data.decode().split('\n')
    s = None
    for line in lines:
        if line.startswith("s = "):
            s = int(line.split("=")[1].strip())
    
    if s is None:
        print("Non riesco a trovare il valore del seme.")
        return
    
    # Calcola i prossimi 50 valori
    next_value = s
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