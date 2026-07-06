from Crypto.Cipher import DES
from Crypto.Util.Padding import pad
import socket

HOST = "spg.challs.cyberchallenge.it"
PORT = 9600

def try_login(username, password):
    """Prova a loggarsi con il server tramite socket."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    # Legge il messaggio iniziale del server
    data = s.recv(1024).decode()
    print(data)

    # Invia opzione login (2)
    s.sendall(b"2\n")

    # Attende la richiesta di username
    data = s.recv(1024).decode()
    print(data)

    # Invia username
    s.sendall(username.encode() + b"\n")

    # Attende richiesta password
    data = s.recv(1024).decode()
    print(data)

    # Invia password cifrata
    s.sendall(password.encode() + b"\n")

    # Legge risposta del server
    response = s.recv(1024).decode()
    print(response)

    s.close()

    return "wrong" not in response.lower() 


def generate_secure_random_password():
    with open("/Users/lorenzovannucci/Downloads/wordlist.txt", "r") as f:
        passwords = f.readlines()
    for i in range(len(passwords)):
        passwords[i] = passwords[i].strip()
        cipher = DES.new(key = b"\x00"*8, mode = DES.MODE_ECB)
        random_psw = cipher.encrypt(pad(passwords[i].encode(), 8))
        print(random_psw.hex()[:12])
        try_login("admin", random_psw.hex()[:12])


        
generate_secure_random_password()
