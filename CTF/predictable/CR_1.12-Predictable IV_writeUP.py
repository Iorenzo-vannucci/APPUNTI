#!/usr/bin/env python3
'''
La logica del codice e' strutturata con queste 4 opzioni:
1. Registrare un nuovo utente con un username, questo ci genera l'IV usato per criptare il nostro login_token:{username}
2. Possiamo usare il nostro login_token per creare un command_token che ci consentira' di eseguire un comando (nel nostro caso sara' get_flag) tramite poi l'opzione 3.
3. Tramite il command_token fornito precedentemente andremo ad eseguire il comando che e' criptato all'interno del token.
4. Possiamo vedere il database contenente tutti gli IV.

Come protezioni, abbiamo il fatto che ovviamente non possiamo usare come username admin poiche' e' gia' stato registrato nel database, inoltre a primo impatto sembra che 
un normale bit flip riservandoci un blocco a parte non sia possibile dato che quando il login_token viene decriptato si prende correttamente values[0] che quindi deve essere
sempre per forza login_token, e poi si divide con separatore : e si prende l'elemento dopo login_token, che quindi verrebbe tradotto in byte spazzatura se si eseguisse un bit flip
tradizionale.
In realta' qui la cosa e' molto piu' semplice.
Noi sappiamo che il nostro login_token e' cosi' costituito: IV + ciphertext('login_token:{username}'), quando poi andiamo ad usare il login_token per generare il command_token
e' qui che avviene l'errore di fondo del codice, per decriptare il codice usa come IV i primi 16 byte del login_token e poi come blocchi da decriptare i successivi byte,
ma noi sappiamo che AES CBC cripta le stringhe cosi, partendo dalla prima: c1 = AES(b1 XOR IV); c2 = AES(c1 XOR b2) ... eccetera. Al contrario per ottenere i blocchi
di  plaintext b1, b2... si procede cosi': b1 = Decrypt(c1) XOR IV, b2 = Decrypt(c2) XOR c1 ..., siccome in questo programma l'IV che usiamo puo' essere cio' che vogliamo
e' facile manipolarlo in modo tale che lo username del login_token diventi admin senza 'corrompere' niente del plaintext.
Basta dunque procedere in questo modo:
1. Sappiamo che login_token: occupa 12 byte del primo blocco e noi possiamo manipolare soltanto il primo blocco cambiando l'IV, abbiamo quindi a disposizione 4 byte, ma
admin ne contiene 5, questo pero' non e' un problema dato che mettendo come input qualsiasi 4 caratteri + n --> xxxxn, soltanto i primi 4 byte verranno cambiati, la n rimarra'
intatta e restera' tale anche dopo la decifratura.
Registriamo quindi un nuovo utente con nome ad esempio 0000n.
2. Dopo aver registrato il nostro utente possiamo prendere l'IV che ci e' stato generato e manipolarlo, sappiamo che IV XOR Dec(c1) = 'login_token:0000', bastera' quindi
fare la differenza di XOR tra 'login_token:0000' e 'login_token:admi', applicarla all'IV, e copiare il login_token che ci e' stato dato prima con l'IV cambiato.
3. Diamo come input all'opzione 2 il nostro nuovo login_token con l'IV cambiato e vedremo che il programma ci dara' il benvenuto come admin, ora non ci resta altro che mettere
come input l'esadecimale di 'get_flag' e ci verra' dato il command_token con l'IV dell'admin e il gioco sara' fatto.
4. Usando il command token andiamo ad eseguire get_flag tramite l'opzione 3 e ci verra' restituita la flag.

PS: nella flag e' scritto il motivo per cui questo modo non va bene: la chiave e' la stessa usata per tutte le operazioni di encrypt/decrypt, inoltre l'IV e' prevedibile
facilmente.
'''


import signal
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os

TIMEOUT = 300

assert("FLAG" in os.environ)
flag = os.environ["FLAG"]
assert(flag.startswith("CCIT{"))
assert(flag.endswith("}"))

key = os.urandom(16)
db = {'admin': os.urandom(16).hex()}


def handle():
    while True:
        print("1. Register")
        print("2. Generate command tokens")
        print("3. Execute commands with token")
        print("4. See database")
        print("0. Exit")
        choice = int(input("> "))
        if choice == 1:
            name = input("Insert your username: ")
            if ":" in name:
                continue
            if name not in db:
                cookie = f"login_token:{name}".encode()
                iv = os.urandom(16)
                db[name] = iv.hex()
                cipher = AES.new(key, AES.MODE_CBC, iv)
                encrypted = cipher.encrypt(pad(cookie, 16))
                print(f"Your login token: {iv.hex()+encrypted.hex()}")
            else:
                print("Username already registered")
        elif choice == 2:
            token = input("Please give me your login token ")
            try:
                cookie = bytes.fromhex(token[32:])
                iv = bytes.fromhex(token[:32])
                cipher = AES.new(key, AES.MODE_CBC, iv)
                pt = unpad(cipher.decrypt(cookie), 16).decode()
                values = pt.split(":")
                if values[0] == "login_token":
                    print("Welcome back {}".format(values[1]))
                    command = bytes.fromhex(input(
                        "What command do you want to execute? "))
                    iv = bytes.fromhex(db[values[1]])
                    cipher = AES.new(key, AES.MODE_CBC, iv)
                    encrypted = cipher.encrypt(pad(command, 16))
                    print(f"Your command token: {iv.hex()+encrypted.hex()}")
                else:
                    print("It seems that this is not a login token.")
            except:
                print("Something went wrong")
        elif choice == 3:
            token = input("What do you want to do? ")
            try:
                cmd = bytes.fromhex(token[32:])
                iv = bytes.fromhex(token[:32])
                cipher = AES.new(key, AES.MODE_CBC, iv)
                pt = unpad(cipher.decrypt(cmd), 16)
                if pt == b"get_flag":
                    if iv == bytes.fromhex(db['admin']):
                        print(f"Here is your flag: {flag}")
                    else:
                        print("Only admin can see the flag.")
                else:
                    print("Nice command! But it seems useless...")
            except:
                print("Something went wrong")
        elif choice == 4:
            print(db)
        else:
            break


if __name__ == "__main__":
    signal.alarm(TIMEOUT)
    handle()
