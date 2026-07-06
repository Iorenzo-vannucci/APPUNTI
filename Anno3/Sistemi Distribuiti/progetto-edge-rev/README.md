# Sistemi Paralleli e Distribuiti  
## Titolo del Progetto

> Corso di Sistemi Paralleli e Distribuiti  
> Anno Accademico: 2025/2026  
> Docente: Francesco Sportolari  
> Studente/i: Vannucci Lorenzo: 370003; Lauria Tommaso: 366560; Ragnacci Giordano: 367442

---

## 📌 Descrizione dell'attività

Questo progetto implementa un'infrastruttura di calcolo distribuito per l'esecuzione di codice Python in sandbox isolate (Docker). Include la gestione della replicazione dei task e del routing su un anello logico decentralizzato basato sull'algoritmo **Chord DHT (Distributed Hash Table)**.

---

## 📦 Modalità di consegna

La consegna avviene **esclusivamente tramite GitHub Classroom**.

Lo studente deve:

1. Sviluppare il progetto all'interno di questo repository.
2. Effettuare il commit delle modifiche in modo regolare e coerente.
3. Effettuare il **push finale su GitHub entro la scadenza indicata**.

⚠️ **Farà fede l’ultimo commit presente sul repository remoto alla scadenza.**  
Non sono ammesse consegne tramite email o altri canali.

---

## 🛠 Requisiti tecnici


## Schema dell'Architettura del Progetto

Ecco come funziona il giro di un task nel sistema, dall'invio fino al completamento dentro la sandbox:

```text
               +----------------------------------------+
               |               CLIENT                   |
               +----------------------------------------+
                                   |
                [1] Qual è il nodo responsabile?
                Key = hash("TASK-123") % 32 = 14
                                   v
               +----------------------------------------+
               |         Tabella di Routing Chord       |
               | (Trova nodo responsabile per la Chiave)|
               +----------------------------------------+
                                   |
                                   |  Inoltra Task a
                                   v  Dispatcher 5006
  +-----------------------------------------------------------------------+
  |                                                                       |
  |   ANELLO LOGICO CHORD (DHT)                                           |
  |                                                                       |
  |       [Nodo ID: 3] -------> [Nodo ID: 15] -------> [Nodo ID: 28]      |
  |       Porta 5005            Porta 5006             Porta 5007         |
  |                                 |                                     |
  +-----------------------------------|-------------------------------------+
                                    |
                                    v [2] Riceve connessione
                      +---------------------------+
                      |      DISPATCHER 5006      |
                      +---------------------------+
                                    |
                                    v [3] Avvia Worker Thread
                      +---------------------------+
                      |    worker_thread_logic    |
                      +---------------------------+
                                    |
               +--------------------+--------------------+
               | Scrive script su file temporaneo        |
               | task_<thread_id>.py                     |
               +--------------------+--------------------+
                                    |
                                    v [4] Esegue Sandbox Docker
               +-----------------------------------------+
               |  CONTAINER DOCKER (python:3.10-slim)    |
               |                                         |
               |  $ python task_<thread_id>.py           |
               |  (CPU/Memoria limitati in isolamento)   |
               +-----------------------------------------+
                                    |
                                    | [5] Ritorna Output Script
                                    v
                                (Stdout)
                                    |
                                    v [6] Invia Risposta
               +-----------------------------------------+
               | Client riceve: {"status": "SETTLED"}     |
               +-----------------------------------------+
```

---

## Analisi dei File di Sistema

### 1. [client.py](client.py)
Il client invia task computazionali (codice Python) al cluster di dispatcher.
*   **Routing:** Contatta un nodo bootstrap per scoprire l'anello, poi invia il task a min(3, N) entry-point diversi. Ogni entry-point instrada il task via Chord al nodo responsabile.
*   **Consenso:** Raccoglie le risposte e applica una logica di maggioranza (quorum) per convalidare il risultato, tollerando il crash parziale dei nodi.

### 2. [dispatcher.py](dispatcher.py)
Il dispatcher funge da nodo Chord e worker di computazione.
*   **Routing Chord hop-by-hop:** Riceve un task, calcola l'hash, e se non è il nodo responsabile lo inoltra al prossimo hop secondo la finger table. Se è responsabile, lo esegue in sandbox.
*   **Sandbox:** Avvia un container Docker isolato (`edgerev-sandbox`) con risorse limitate. Il codice viene inviato via stdin (no file temporanei).
*   **Protocolli:** Gestisce JOIN, LEAVE, GET_RING, BEAT, ROUTE e TASK.

### 3. [chord.py](chord.py)
Implementa la logica di anello logico distribuito del protocollo Chord DHT.
*   Ogni nodo possiede un `id` calcolato come `hash(IP:porta) % 2^m` (m=8, spazio 0-255).
*   La `costruisci_finger_table` calcola i collegamenti rapidi per salti di $2^{i-1}$ posizioni sull'anello.
*   `trova_successore_chiave` implementa il lookup O(log N) con gestione wrap-around.

---

## Guida per far partire il progetto

### Metodo 1: Docker Compose (consigliato)

Un solo comando per avviare l'intero cluster:

```bash
# 1. Build delle immagini (da fare una sola volta)
docker build -t edgerev-sandbox .
docker compose build

# 2. Avvia il cluster (3 dispatcher)
docker compose up

# 3. In un altro terminale, invia un task
python3 client.py localhost:5005
```

Per simulare un crash:
```bash
docker compose stop dispatcher-2    # Uccide un nodo
python3 client.py localhost:5005     # Il task viene comunque eseguito
```

Per spegnere tutto:
```bash
docker compose down
```

### Metodo 2: Avvio manuale (senza Docker Compose)

```bash
# 1. Build della sandbox
docker build -t edgerev-sandbox .

# 2. Avvia i dispatcher (in terminali separati)
python3 dispatcher.py 5005                          # Seed
python3 dispatcher.py 5006 127.0.0.1:5005           # Si connette al seed
python3 dispatcher.py 5007 127.0.0.1:5005           # Si connette al seed

# 3. Invia un task
python3 client.py 127.0.0.1:5005
```

### Test Fault Tolerance
Spegnendo uno dei dispatcher (Ctrl+C o `docker compose stop`), il sistema rileva il crash tramite heartbeat o graceful leave, ricostruisce le finger table, e i task successivi vengono instradati correttamente ai nodi rimanenti.

