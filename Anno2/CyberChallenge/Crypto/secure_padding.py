'''
#!/usr/bin/env python3
from pwn import *
from binascii import hexlify, unhexlify
import time
import random
import string

# Configurazione
HOST = 'padding.challs.cyberchallenge.it'
PORT = 9030
BLOCK_SIZE = 16
MAX_LENGTH = 64
SAVE_FILE = 'flag_progress.txt'

def load_progress():
    try:
        with open(SAVE_FILE, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        return b""

def save_progress(flag):
    with open(SAVE_FILE, 'wb') as f:
        f.write(flag)

def connect_server():
    context.log_level = 'error'  # Riduce il rumore di output
    context.timeout = 30
    return remote(HOST, PORT)

def main():
    known_flag = load_progress()
    print(f"Riprendendo da: {known_flag.decode(errors='replace')}")

    try:
        conn = connect_server()
        
        # Funzione per inviare/ricevere con robustezza
        def query(payload):
            nonlocal conn
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    conn.sendlineafter(b"Give me the password to encrypt:", payload)
                    conn.recvuntil(b"Here is you secure encrypted password: ")
                    encrypted = conn.recvline().strip()
                    return unhexlify(encrypted)
                except EOFError:
                    print(f"Connessione chiusa, riconnessione (tentativo {attempt+1}/{max_retries})...")
                    try:
                        conn.close()
                    except:
                        pass
                    time.sleep(2)  # Attendi un po' prima di riconnettere
                    conn = connect_server()
                except Exception as e:
                    print(f"Errore durante la query: {str(e)} (tentativo {attempt+1}/{max_retries})")
                    try:
                        conn.close()
                    except:
                        pass
                    time.sleep(2)  # Attendi un po' prima di riconnettere
                    conn = connect_server()
            
            # Se arriviamo qui, abbiamo esaurito i tentativi
            print("Impossibile completare la query dopo diversi tentativi. Riprovo...")
            time.sleep(5)  # Attesa più lunga prima di riprovare
            conn = connect_server()
            return query(payload)  # Riprova ancora

        # Determina lunghezza target
        try:
            base_length = len(query(b""))
            print(f"Lunghezza ciphertext base: {base_length} bytes")
        except Exception as e:
            print(f"Errore nel determinare la lunghezza base: {str(e)}")
            base_length = 32  # Valore di fallback basato sul tuo output

        # Attacco ECB byte-per-byte
        for i in range(len(known_flag), MAX_LENGTH):
            print(f"\n=== Tentativo byte {i+1} ===")
            
            # Calcola padding necessario per allineare correttamente i blocchi
            prefix_len = (BLOCK_SIZE - 1 - (i % BLOCK_SIZE))
            prefix = b"A" * prefix_len
            
            # Ottengo il blocco target
            try:
                target = query(prefix)
                target_block_idx = (len(prefix) + i) // BLOCK_SIZE
                target_block = target[target_block_idx * BLOCK_SIZE:(target_block_idx + 1) * BLOCK_SIZE]
                print(f"Target block: {hexlify(target_block).decode()}")
            except Exception as e:
                print(f"Errore nell'ottenere il blocco target: {str(e)}")
                time.sleep(5)
                continue  # Riprova con questo byte
            
            found = False
            # Prova prima caratteri stampabili (più probabili)
            for c in string.printable.encode():
                try:
                    test_payload = prefix
                    test_resp = query(test_payload + known_flag + bytes([c]))
                    test_block = test_resp[target_block_idx * BLOCK_SIZE:(target_block_idx + 1) * BLOCK_SIZE]
                    
                    if test_block == target_block:
                        known_flag += bytes([c])
                        print(f"Trovato: {c:02x} ('{chr(c)}')")
                        print(f"Flag attuale: {known_flag.decode(errors='replace')}")
                        save_progress(known_flag)
                        found = True
                        break
                except Exception as e:
                    print(f"Errore durante il test del carattere {c:02x}: {str(e)}")
                    time.sleep(2)
                    continue
            
            if not found:
                print("Nessun carattere stampabile trovato, proviamo tutti i byte...")
                for c in range(256):
                    if bytes([c]) in string.printable.encode():
                        continue  # Già provato
                    
                    try:
                        test_payload = prefix
                        test_resp = query(test_payload + known_flag + bytes([c]))
                        test_block = test_resp[target_block_idx * BLOCK_SIZE:(target_block_idx + 1) * BLOCK_SIZE]
                        
                        if test_block == target_block:
                            known_flag += bytes([c])
                            print(f"Trovato byte {c:02x}")
                            print(f"Flag attuale: {hexlify(known_flag).decode()}")
                            save_progress(known_flag)
                            found = True
                            break
                    except Exception as e:
                        print(f"Errore durante il test del byte {c:02x}: {str(e)}")
                        time.sleep(2)
                        continue
            
            if not found:
                print(f"Byte {i+1} non trovato. Flag parziale: {known_flag.decode(errors='replace')}")
                # Proviamo ancora con questo byte
                i -= 1
                time.sleep(5)
                continue
                
            # Controllo se la flag termina con "}"
            if known_flag.endswith(b"}"):
                print(f"\nFlag completa trovata: {known_flag.decode(errors='replace')}")
                break

        print(f"\nFlag recuperata: {known_flag.decode(errors='replace')}")

    except KeyboardInterrupt:
        print("\nInterrotto manualmente. Salvo lo stato...")
    except Exception as e:
        print(f"Errore grave: {str(e)}")
    finally:
        try:
            conn.close()
        except:
            pass
        save_progress(known_flag)

if __name__ == "__main__":
    main()

    '''

from string import printable as pippo
from pwn import *

FLAG_LENGHT = 31
flag = ''

connection = remote('padding.challs.cyberchallenge.it', 9030)

def split_blocks(msg, BLOCK = 32):
    return [msg[i:i+BLOCK] for i in range(0, len(msg), BLOCK)]

def send_and_recive(data):
    connection.recvuntil(":")
    connection.sendline(data)
    print(connection.recvuntil(":"))
    return split_blocks(connection.recvline().strip().decode())

while '}' not in flag:
    for carattere in pippo:
        injection = 'C' * (FLAG_LENGHT - len(flag)) + flag + carattere + 'C' * (FLAG_LENGHT - len(flag))
        response = send_and_recive(injection)
        test_block, brute_block = response[1], response[3]
        if test_block == brute_block:
            flag += carattere
            print (f'Flag: {flag}')
            print(f'Carattere trovato: {carattere}')
            break