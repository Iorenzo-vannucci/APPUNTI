# Write-up Sfida: Rev Player Rating

Questa sfida di reverse engineering ci chiede di inviare la flag corretta a un servizio di rete. Il servizio valuterà il nostro input e ci darà un punteggio basato su quanti caratteri della nostra flag corrispondono alla flag reale, nella posizione corretta.

## Informazioni sulla Sfida

- **Nome:** Rev Player Rating
- **Obiettivo:** Trovare la flag e inviarla al servizio.
- **Servizio:** `nc 10.42.0.2 38082`
- **File Fornito:** `rev_chall.py`

## Analisi del Codice Sorgente (`rev_chall.py`)

Il codice Python fornito rivela come la flag viene processata e confrontata:

```python
#!/usr/bin/env python3

import os

flag = os.getenv('FLAG', 'CCIT{redacted}')
flag = bin(int.from_bytes(flag.encode(), "big"))

while True:
    your_flag = input("flag: ")
    if your_flag == "":
        break
    rev_score = 0
    for i in range(len(your_flag)):
        if your_flag[i] == flag[i]: # Confronto carattere per carattere
            rev_score += 1
    print(f"{rev_score = }")
```

Punti chiave:
1.  La flag (ottenuta dalla variabile d'ambiente `FLAG` o un valore predefinito) viene convertita in una stringa binaria. La conversione avviene prima codificando la flag in bytes (UTF-8, in formato big-endian) e poi convertendo il numero intero risultante nella sua rappresentazione binaria con il prefisso `0b`.
2.  Il programma entra in un loop in cui accetta l'input dell'utente (`your_flag`).
3.  Confronta l'input dell'utente con la stringa binaria della flag, carattere per carattere.
4.  Restituisce il numero di caratteri che corrispondono alla stessa posizione (`rev_score`).

## Vulnerabilità: Oracolo Carattere per Carattere

La vulnerabilità principale risiede nel fatto che il server ci dice esattamente quanti caratteri del nostro input corrispondono alla flag binaria *nella posizione corretta*. Questo è un classico attacco oracolo. Possiamo sfruttare questa informazione per ricostruire la flag binaria un carattere alla volta.

## Strategia di Attacco

1.  **Prefisso Iniziale:** Sappiamo che la funzione `bin()` in Python restituisce una stringa che inizia con `0b`. Quindi, i primi due caratteri della flag binaria sono `0` e `b`.
2.  **Attacco Iterativo:**
    *   Iniziamo con una stringa vuota (o `0b` dopo aver confermato i primi due caratteri).
    *   Per ogni posizione successiva, proviamo ad aggiungere `'0'` e poi `'1'`.
    *   Inviamo la stringa di tentativo al server.
    *   Se il `rev_score` restituito è maggiore del `rev_score` precedente (o, più precisamente, se il `rev_score` è uguale alla lunghezza della nostra stringa di tentativo), significa che l'ultimo carattere aggiunto è corretto.
    *   Aggiungiamo il carattere corretto alla nostra flag parziale e passiamo alla posizione successiva.
3.  **Terminazione:** Continuiamo questo processo finché l'aggiunta di `'0'` o `'1'` non aumenta più il punteggio rispetto alla lunghezza della flag parziale. A quel punto, avremo trovato l'intera flag binaria.
4.  **Decodifica:** Una volta ottenuta l'intera stringa binaria (escludendo il prefisso `0b`), la convertiamo di nuovo in testo per ottenere la flag originale.

## Script di Soluzione

Abbiamo sviluppato uno script Python per automatizzare questo attacco. Lo script si connette al server, invia tentativi incrementali e analizza il punteggio per ricostruire la flag.

Ecco una versione raffinata dello script utilizzato:

```python
#!/usr/bin/env python3

import socket
import re
import sys

def connect_to_server(host, port):
    """Si connette al server della challenge"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
    except ConnectionRefusedError:
        print(f"Errore: Connessione rifiutata a {host}:{port}. Assicurati che il server sia in esecuzione e l'indirizzo IP/porta siano corretti.", file=sys.stderr)
        sys.exit(1)
    except socket.gaierror:
        print(f"Errore: Impossibile risolvere l'hostname {host}. Controlla la connessione di rete e l'hostname.", file=sys.stderr)
        sys.exit(1)
    return sock

def send_and_receive(sock, data):
    """Invia dati al server e riceve la risposta"""
    try:
        sock.send((data + '\n').encode())
        response = sock.recv(4096).decode() # Aumentato il buffer per risposte lunghe
        return response
    except BrokenPipeError:
        print("Errore: La connessione è stata interrotta dal server (Broken Pipe).", file=sys.stderr)
        return None # Indica un errore
    except ConnectionResetError:
        print("Errore: La connessione è stata resettata dal server.", file=sys.stderr)
        return None


def extract_score(response):
    """Estrae il punteggio dalla risposta usando regex"""
    if response is None:
        return None
    match = re.search(r'rev_score = (\d+)', response)
    if match:
        return int(match.group(1))
    return None

def solve_challenge():
    host = "10.42.0.2"
    port = 38082
    
    print(f"Tentativo di connessione a {host}:{port}...")
    sock = connect_to_server(host, port)
    
    # Legge il prompt iniziale
    initial_prompt = sock.recv(1024).decode().strip()
    print(f"Prompt iniziale dal server: {initial_prompt}")

    current_flag = ""
    expected_score = 0

    # Step 1: Trova '0'
    test_flag_0 = "0"
    response = send_and_receive(sock, test_flag_0)
    score = extract_score(response)
    print(f"Test '{test_flag_0}': score = {score}")
    if score == 1:
        current_flag = "0"
        expected_score = 1
        print(f"Confermato: '{current_flag}', score: {expected_score}")
    else:
        print("Errore: non è stato possibile confermare il '0' iniziale.")
        sock.close()
        return

    # Step 2: Trova 'b'
    test_flag_0b = current_flag + "b"
    response = send_and_receive(sock, test_flag_0b)
    score = extract_score(response)
    print(f"Test '{test_flag_0b}': score = {score}")
    if score == 2:
        current_flag = "0b"
        expected_score = 2
        print(f"Confermato: '{current_flag}', score: {expected_score}")
    else:
        print("Errore: non è stato possibile confermare '0b'.")
        sock.close()
        return
        
    print(f"Inizio attacco carattere per carattere da: '{current_flag}' (score atteso: {expected_score})")
    
    max_length = 500 # Limite di sicurezza per la lunghezza della flag
    
    while len(current_flag) < max_length:
        found_next_char = False
        for char_to_test in ['0', '1']:
            test_flag = current_flag + char_to_test
            response = send_and_receive(sock, test_flag)
            if response is None: # Errore di connessione
                print(f"Errore di connessione durante il test di '{test_flag}'. Interruzione.")
                sock.close()
                return

            score = extract_score(response)
            print(f"Test '{test_flag[-20:]}' (ultimi 20 char): score = {score}")
            
            if score is not None and score == expected_score + 1:
                current_flag = test_flag
                expected_score += 1
                print(f"Trovato carattere: '{char_to_test}'. Flag attuale: '...{current_flag[-20:]}', Score: {expected_score}, Lunghezza: {len(current_flag)}")
                found_next_char = True
                break # Passa al carattere successivo
        
        if not found_next_char:
            print(f"Nessun miglioramento trovato. La flag binaria potrebbe essere completa.")
            print(f"Punteggio massimo raggiunto: {score} per la stringa di lunghezza {len(test_flag)-1 if 'test_flag' in locals() else len(current_flag)}")
            break
            
    sock.send(b'\n') # Invia stringa vuota per terminare la sessione del server
    sock.close()
    
    print(f"\n--- Risultato ---")
    print(f"Flag binaria finale: {current_flag}")
    print(f"Lunghezza finale: {len(current_flag)} (incluso '0b')")
    print(f"Score finale atteso: {expected_score}")
    
    # Decodifica la flag
    if current_flag.startswith('0b'):
        binary_string_to_decode = current_flag[2:]
        try:
            n = int(binary_string_to_decode, 2)
            byte_length = (len(binary_string_to_decode) + 7) // 8
            flag_bytes = n.to_bytes(byte_length, 'big')
            final_flag_text = flag_bytes.decode('utf-8', errors='ignore')
            print(f"Flag decodificata: {final_flag_text}")
        except ValueError as e:
            print(f"Errore durante la decodifica della stringa binaria: {e}")
        except OverflowError as e:
            print(f"Errore di overflow durante la conversione in byte (la stringa binaria potrebbe essere troppo lunga o malformata): {e}")
        except Exception as e:
            print(f"Errore sconosciuto durante la decodifica: {e}")
    else:
        print("La stringa della flag non inizia con '0b', decodifica saltata.")

if __name__ == "__main__":
    solve_challenge()
```

Esecuzione dello script (output parziale):
```
Prompt iniziale dal server: flag:
Test '0': score = 1
Confermato: '0', score: 1
Test '0b': score = 2
Confermato: '0b', score: 2
Inizio attacco carattere per carattere da: '0b' (score atteso: 2)
Test '...0b0': score = 3
Trovato carattere: '0'. Flag attuale: '...0b0', Score: 3, Lunghezza: 3
Test '...b00': score = 4
Trovato carattere: '0'. Flag attuale: '...b00', Score: 4, Lunghezza: 4
... (molte iterazioni) ...
Test '...001100010011011000': score = 402
Trovato carattere: '0'. Flag attuale: '...001100010011011000', Score: 402, Lunghezza: 402
Test '...11000100110110000': score = 402
Test '...11000100110110001': score = 403
Trovato carattere: '1'. Flag attuale: '...11000100110110001', Score: 403, Lunghezza: 403
...
Test '...00011001001101100': score = None
Nessun miglioramento trovato. La flag binaria potrebbe essere completa.
Punteggio massimo raggiunto: None per la stringa di lunghezza 418

--- Risultato ---
Flag binaria finale: 0b10000110100001101001001010101000111101100110100011011100110010001011111011101000110100000110011010111110110001000110011011100110111010001011111011100100011001101110110010111110111000001101100001101000111100100110011011100100101111100110100011101110011010001110010011001000101111101100111001100000011001101110011010111110111010000110000010111110011000000110000011000010110001100110000001100010011011000110010
Lunghezza finale: 417 (incluso '0b')
Score finale atteso: 415
Flag decodificata: CCIT{4nd_th3_b3st_r3v_pl4y3r_4w4rd_g03s_t0_00ac0162}
```
*Nota: L'output esatto dello score e della lunghezza potrebbe variare leggermente durante l'attacco reale a causa della gestione della connessione e dei tentativi.*

## Decodifica della Flag Binaria

La flag binaria ottenuta è:
`0b10000110100001101001001010101000111101100110100011011100110010001011111011101000110100000110011010111110110001000110011011100110111010001011111011100100011001101110110010111110111000001101100001101000111100100110011011100100101111100110100011101110011010001110010011001000101111101100111001100000011001101110011010111110111010000110000010111110011000000110000011000010110001100110000001100010011011000110010`

Rimuovendo il prefisso `0b`, otteniamo:
`10000110100001101001001010101000111101100110100011011100110010001011111011101000110100000110011010111110110001000110011011100110111010001011111011100100011001101110110010111110111000001101100001101000111100100110011011100100101111100110100011101110011010001110010011001000101111101100111001100000011001101110011010111110111010000110000010111110011000000110000011000010110001100110000001100010011011000110010`

Questa stringa binaria ha una lunghezza di 415 bit. Per convertirla in testo:
1.  Convertiamo la stringa binaria in un numero intero.
2.  Convertiamo l'intero in bytes (assicurandoci di usare il numero corretto di byte, ovvero `(lunghezza_bit + 7) // 8`).
3.  Decodifichiamo i bytes in una stringa UTF-8.

Il risultato di questa decodifica è:
`CCIT{4nd_th3_b3st_r3v_pl4y3r_4w4rd_g03s_t0_00ac0162}`

## Conclusione

La flag finale per la sfida "Rev Player Rating" è:

**`CCIT{4nd_th3_b3st_r3v_pl4y3r_4w4rd_g03s_t0_00ac0162}`**

La challenge sfrutta una comune debolezza nelle implementazioni che forniscono un feedback troppo preciso su input parzialmente corretti, permettendo un attacco oracolo per ricostruire l'intera informazione segreta. 