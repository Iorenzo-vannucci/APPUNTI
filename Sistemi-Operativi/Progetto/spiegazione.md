# Spiegazione Dettagliata - Progetto Incrocio

## Indice
1. [Panoramica Generale](#panoramica-generale)
2. [File Header: incrocio.h](#file-header-incrocio-h)
3. [Processo Incrocio: incrocio.c](#processo-incrocio-incrocio-c)
4. [Processo Garage: garage.c](#processo-garage-garage-c)
5. [Processo Automobile: automobile.c](#processo-automobile-automobile-c)
6. [Funzioni Utilities: utils.c](#funzioni-utilities-utils-c)
7. [Script di Compilazione: build.sh](#script-di-compilazione-build-sh)
8. [Script di Esecuzione: run.sh](#script-di-esecuzione-run-sh)
9. [Flusso di Esecuzione Completo](#flusso-di-esecuzione-completo)
10. [Comunicazione tra Processi](#comunicazione-tra-processi)

---

## Panoramica Generale

Il progetto simula un incrocio stradale con **3 tipi di processi**:
- **1 processo INCROCIO**: coordina il traffico
- **1 processo GARAGE**: genera automobili
- **4 processi AUTOMOBILE**: attraversano l'incrocio

**Comunicazione**: IPC System V (memoria condivisa + semafori)
**File Output**: `incrocio.txt` e `auto.txt` (devono essere identici)

---

## File Header: incrocio.h

### Scopo
Definisce tutte le strutture dati, costanti e dichiarazioni condivise tra i processi.

### Elementi Chiave

#### Costanti IPC System V
```c
#define SHM_KEY 0x1234    // Chiave memoria condivisa
#define SEM_KEY 0x5678    // Chiave semafori
#define NUM_AUTO 4        // Sempre 4 automobili per ciclo
#define NUM_STRADE 4      // Incrocio a 4 strade (0,1,2,3)
```

#### I 4 Semafori del Sistema
```c
#define SEM_MUTEX 0           // Mutua esclusione memoria condivisa
#define SEM_AUTO_PRONTE 1     // Garage → Incrocio: "4 auto pronte"
#define SEM_AUTO_PASSAGGIO 2  // Incrocio → Auto: "puoi passare"
#define SEM_AUTO_FINITA 3     // Auto → Incrocio: "ho finito"
```

#### Struttura Memoria Condivisa
```c
typedef struct {
    automobile_t automobili[NUM_AUTO];  // Array delle 4 auto
    int num_auto_attive;               // Contatore processi vivi
    int auto_pronte;                   // Flag: garage ha creato 4 auto
    int termine_richiesto;             // Flag: SIGTERM ricevuto
    int prossima_auto;                 // Quale auto può attraversare
} stato_incrocio_t;
```

---

## Processo Incrocio: incrocio.c

### Ruolo
**COORDINATORE MASTER** - gestisce tutto il traffico e la terminazione.

### Flusso Principale

#### FASE 1: Inizializzazione
```c
signal(SIGTERM, gestore_sigterm);     // Solo l'incrocio gestisce SIGTERM
atexit(cleanup_risorse);              // Pulizia automatica
inizializza_memoria_condivisa();      // Crea risorse IPC
```

#### FASE 2: Loop Coordinamento Traffico
```c
while (1) {
    // 1. Aspetta notifica garage
    P(sem_id, SEM_AUTO_PRONTE);  // Blocca finché garage crea 4 auto
    
    // 2. Controlla terminazione
    if (stato_condiviso->termine_richiesto) break;
    
    // 3. Fa attraversare tutte e 4 le auto
    for (int auto_attraversate = 0; auto_attraversate < 4; auto_attraversate++) {
        int auto_scelta = GetNextCar(direzioni);          // Sceglie auto
        
        // Scrive in incrocio.txt
        fprintf(file_incrocio, "%d\n", strada_origine);
        
        // Autorizza l'auto
        stato_condiviso->prossima_auto = auto_scelta;
        V(sem_id, SEM_AUTO_PASSAGGIO);                    // Sblocca auto
        
        // Aspetta che finisca
        P(sem_id, SEM_AUTO_FINITA);                       // Blocca fino a fine
    }
}
```

#### FASE 3: Terminazione Coordinata
```c
// Informa tutti di terminare
stato_condiviso->termine_richiesto = 1;

// Sblocca processi in attesa
V(sem_id, SEM_AUTO_PRONTE);
V(sem_id, SEM_AUTO_PASSAGGIO);
V(sem_id, SEM_AUTO_FINITA);

// Aspetta che tutti terminino (incrocio termina PER ULTIMO)
do {
    sleep(1);
    processi_attivi = stato_condiviso->num_auto_attive;
} while (processi_attivi > 0);
```

### Perché l'incrocio è il master?
- **Crea le risorse IPC** (memoria + semafori)
- **Coordina la terminazione** di tutti gli altri processi
- **Termina per ultimo** per garantire cleanup completo

---

## Processo Garage: garage.c

### Ruolo
**GENERATORE DI AUTOMOBILI** - crea 4 processi automobile ogni ciclo.

### Flusso Principale

#### FASE 1: Connessione IPC
```c
// Connetti alle risorse create dall'incrocio
shm_id = shmget(SHM_KEY, sizeof(stato_incrocio_t), 0666);     // Solo lettura
stato_condiviso = (stato_incrocio_t*)shmat(shm_id, NULL, 0);
sem_id = semget(SEM_KEY, NUM_SEMAFORI, 0666);                // Solo lettura
```

#### FASE 2: Loop Generazione Auto
```c
while (1) {
    // 1. Controlla se deve terminare
    if (stato_condiviso->termine_richiesto) break;
    
    // 2. Crea 4 processi automobile
    for (int i = 0; i < NUM_AUTO; i++) {
        int destinazione = EstraiDirezione(i);    // Direzione casuale
        
        // Registra auto in memoria condivisa
        P(sem_id, SEM_MUTEX);
        stato_condiviso->automobili[i].strada_origine = i;
        stato_condiviso->automobili[i].strada_destinazione = destinazione;
        stato_condiviso->num_auto_attive++;
        V(sem_id, SEM_MUTEX);
        
        // Fork + Exec = processo indipendente
        pids[i] = fork();
        if (pids[i] == 0) {
            char strada_str[10], dest_str[10];
            snprintf(strada_str, sizeof(strada_str), "%d", i);
            snprintf(dest_str, sizeof(dest_str), "%d", destinazione);
            
            execl("./build/bin/automobile", "automobile", strada_str, dest_str, NULL);
        }
    }
    
    // 3. Notifica incrocio: "4 auto pronte!"
    V(sem_id, SEM_AUTO_PRONTE);
    
    // 4. Aspetta che tutte terminino
    for (int i = 0; i < NUM_AUTO; i++) {
        waitpid(pids[i], NULL, 0);  // Attesa bloccante
        stato_condiviso->num_auto_attive--;
    }
    
    // 5. Pausa 1 secondo (come da specifiche)
    sleep(1);
}
```

### Perché fork() + execl()?
- **fork()**: crea copia del processo garage
- **execl()**: sostituisce con programma automobile
- **Risultato**: processo automobile **completamente indipendente**

---

## Processo Automobile: automobile.c

### Ruolo
**SINGOLA AUTOMOBILE** che attraversa l'incrocio.

### Flusso Principale

#### FASE 1: Parsing Argomenti
```c
// Il garage passa strada e destinazione come stringhe
mia_strada = atoi(argv[1]);          // "2" → 2
mia_destinazione = atoi(argv[2]);    // "0" → 0
```

#### FASE 2: Loop Attesa Autorizzazione
```c
while (1) {
    printf("MACCHINA[%d] In attesa di autorizzazione...\n", mia_strada);
    P(sem_id, SEM_AUTO_PASSAGGIO);    // Blocca finché incrocio autorizza
    
    // Controlla terminazione
    if (stato_condiviso->termine_richiesto) break;
    
    // Verifica se è autorizzata QUESTA auto
    if (stato_condiviso->prossima_auto == mia_strada) {
        // È il mio turno!
        printf("MACCHINA[%d] Attraversando l'incrocio...\n", mia_strada);
        sleep(1);  // Simula attraversamento
        
        // Scrive in auto.txt
        FILE *file = fopen("auto.txt", "a");
        fprintf(file, "%d\n", mia_strada);
        fclose(file);
        
        // Notifica completamento
        V(sem_id, SEM_AUTO_FINITA);
        break;  // Termina
    } else {
        // Non è il mio turno, rilascio per l'auto giusta
        V(sem_id, SEM_AUTO_PASSAGGIO);
        usleep(10000);  // Piccola pausa
    }
}
```

### Perché questo meccanismo complesso?
**Problema**: 4 auto aspettano sullo stesso semaforo, ma solo 1 può passare.
**Soluzione**: 
1. Incrocio imposta `prossima_auto = X`
2. Sblocca `SEM_AUTO_PASSAGGIO`  
3. Auto controlla se `prossima_auto == mia_strada`
4. Se sì → attraversa, se no → rilascia semaforo

---

## Funzioni Utilities: utils.c

### Operazioni sui Semafori
```c
void P(int sem_id, int sem_num) {  // WAIT - acquisisce risorsa
    struct sembuf sb = {sem_num, -1, 0};  // Decrementa semaforo
    semop(sem_id, &sb, 1);
}

void V(int sem_id, int sem_num) {  // SIGNAL - rilascia risorsa  
    struct sembuf sb = {sem_num, +1, 0};  // Incrementa semaforo
    semop(sem_id, &sb, 1);
}
```

### Funzioni del Progetto
```c
int EstraiDirezione(int iAutomobile) {
    srand(time(NULL) + iAutomobile);  // Seed diverso per ogni auto
    do {
        destinazione = rand() % NUM_STRADE;
    } while (destinazione == iAutomobile);  // Diversa da origine
    return destinazione;
}

int GetNextCar(int *Direzioni) {
    static int ultima_auto = -1;  // Round-robin
    for (int i = 0; i < NUM_AUTO; i++) {
        int auto_test = (ultima_auto + 1 + i) % NUM_AUTO;
        if (Direzioni[auto_test] != -1) {  // -1 = già passata
            ultima_auto = auto_test;
            return auto_test;
        }
    }
    return -1;
}
```

### Gestione Risorse IPC
```c
void inizializza_memoria_condivisa(void) {
    // Crea memoria condivisa
    shm_id = shmget(SHM_KEY, sizeof(stato_incrocio_t), IPC_CREAT | 0666);
    stato_condiviso = (stato_incrocio_t*)shmat(shm_id, NULL, 0);
    
    // Crea e inizializza semafori
    sem_id = semget(SEM_KEY, NUM_SEMAFORI, IPC_CREAT | 0666);
    semctl(sem_id, SEM_MUTEX, SETVAL, 1);        // Mutex libero
    semctl(sem_id, SEM_AUTO_PRONTE, SETVAL, 0);  // Auto non pronte
    // ...
}

void cleanup_risorse(void) {
    shmdt(stato_condiviso);              // Scollega memoria
    shmctl(shm_id, IPC_RMID, NULL);      // Rimuove memoria
    semctl(sem_id, 0, IPC_RMID);         // Rimuove semafori
}
```

---

## Script di Compilazione: build.sh

### Struttura
```bash
CFLAGS="-std=c11 -Wall -Wextra -pedantic"
LIBS="-pthread"  # Necessario per semafori System V

build() {
    # Compila utils.c come oggetto condiviso
    gcc ${CFLAGS} -c "${SRC_DIR}/utils.c" -o "${BUILD_DIR}/utils.o"
    
    # Linka ogni eseguibile con utils.o
    gcc ${CFLAGS} "${SRC_DIR}/incrocio.c" "${BUILD_DIR}/utils.o" -o "${BIN_DIR}/incrocio" ${LIBS}
    gcc ${CFLAGS} "${SRC_DIR}/garage.c" "${BUILD_DIR}/utils.o" -o "${BIN_DIR}/garage" ${LIBS}
    gcc ${CFLAGS} "${SRC_DIR}/automobile.c" "${BUILD_DIR}/utils.o" -o "${BIN_DIR}/automobile" ${LIBS}
}
```

### Opzioni di Uso
- `./build.sh` → solo compilazione
- `./build.sh run` → compila e avvia applicazione
- `./build.sh clean` → pulisce tutto + risorse IPC

---

## Script di Esecuzione: run.sh

### Fasi del Test
```bash
# 1. Compilazione
./build.sh

# 2. Pulizia risorse precedenti
ipcrm -M 0x1234 2>/dev/null || true
ipcrm -S 0x5678 2>/dev/null || true

# 3. Avvio processi
./build/bin/incrocio &
INCROCIO_PID=$!
sleep 2  # Aspetta inizializzazione IPC

./build/bin/garage &
GARAGE_PID=$!

# 4. Gestione terminazione
trap "kill -TERM $INCROCIO_PID; sleep 2; kill -9 $GARAGE_PID $INCROCIO_PID" INT
wait $INCROCIO_PID $GARAGE_PID

# 5. Verifica risultati
if diff incrocio.txt auto.txt >/dev/null; then
    echo "SUCCESS: File identici!"
else
    echo "ERROR: File diversi!"
fi
```

---

## **FLUSSO DI ESECUZIONE COMPLETO**

### 1. Avvio Sistema
```
run.sh → build.sh → compila tutto
run.sh → ./incrocio & → crea IPC, aspetta garage
run.sh → ./garage & → si connette IPC, inizia cicli
```

### 2. Ciclo Normale
```
GARAGE:   Crea 4 auto → V(SEM_AUTO_PRONTE) → aspetta figli
INCROCIO: P(SEM_AUTO_PRONTE) → si sblocca → gestisce traffico
AUTO_i:   P(SEM_AUTO_PASSAGGIO) → attraversa → V(SEM_AUTO_FINITA)
INCROCIO: P(SEM_AUTO_FINITA) → riceve conferma → prossima auto
GARAGE:   waitpid() tutti → sleep(1) → nuovo ciclo
```

### 3. Terminazione
```
USER:     kill -TERM <pid_incrocio>
INCROCIO: gestore_sigterm → termine_richiesto=1 → sblocca tutti
GARAGE:   controlla termine_richiesto → break → exit
AUTO_i:   controlla termine_richiesto → break → exit  
INCROCIO: aspetta num_auto_attive=0 → cleanup IPC → exit
```

---

## **PUNTI CHIAVE PER LA SPIEGAZIONE**

### 1. **Architettura Master-Worker**
- **Incrocio**: Master coordinator
- **Garage**: Job generator  
- **Automobili**: Workers indipendenti

### 2. **Sincronizzazione a 4 Livelli**
- **SEM_AUTO_PRONTE**: Garage notifica Incrocio
- **SEM_AUTO_PASSAGGIO**: Incrocio autorizza Auto
- **SEM_AUTO_FINITA**: Auto conferma a Incrocio
- **SEM_MUTEX**: Protezione memoria condivisa

### 3. **Comunicazione Bidirezionale**
- **Garage → Incrocio**: Tramite SEM_AUTO_PRONTE
- **Incrocio → Auto**: Tramite prossima_auto + SEM_AUTO_PASSAGGIO
- **Auto → Incrocio**: Tramite SEM_AUTO_FINITA
- **Stato globale**: Tramite memoria condivisa protetta

### 4. **Terminazione Graceful**
- **Un solo segnale**: SIGTERM solo a incrocio
- **Coordinamento**: termine_richiesto in memoria condivisa
- **Ordine**: tutti terminano, incrocio per ultimo
- **Cleanup**: automatico con atexit()

### 5. **Correttezza Verificabile**
- **File identici**: incrocio.txt = auto.txt
- **Determinismo**: ordine attraversamento prevedibile
- **Atomicità**: ogni operazione è transazione completa

---

## Flusso di Esecuzione Completo

### 1. Avvio Sistema
```
run.sh → build.sh → compila tutto
run.sh → ./incrocio & → crea IPC, aspetta garage
run.sh → ./garage & → si connette IPC, inizia cicli
```

### 2. Ciclo Normale
```
GARAGE:   Crea 4 auto → V(SEM_AUTO_PRONTE) → aspetta figli
INCROCIO: P(SEM_AUTO_PRONTE) → si sblocca → gestisce traffico
AUTO_i:   P(SEM_AUTO_PASSAGGIO) → attraversa → V(SEM_AUTO_FINITA)
INCROCIO: P(SEM_AUTO_FINITA) → riceve conferma → prossima auto
GARAGE:   waitpid() tutti → sleep(1) → nuovo ciclo
```

### 3. Terminazione
```
USER:     kill -TERM <pid_incrocio>
INCROCIO: gestore_sigterm → termine_richiesto=1 → sblocca tutti
GARAGE:   controlla termine_richiesto → break → exit
AUTO_i:   controlla termine_richiesto → break → exit  
INCROCIO: aspetta num_auto_attive=0 → cleanup IPC → exit
```

---

## Comunicazione tra Processi

### Schema delle Comunicazioni

```
GARAGE ──────V(SEM_AUTO_PRONTE)──────> INCROCIO
              │                           │
              │                           │
              └─── MEMORIA CONDIVISA ─────┘
                     │                    │
           ┌─────────┴────────┐           │
           │                  │           │
           v                  v           v
    AUTOMOBILE_0        AUTOMOBILE_1     ...
           │                  │           │
           └──V(SEM_AUTO_FINITA)──> INCROCIO
```

### Dettaglio Sincronizzazione

#### Semaforo SEM_AUTO_PRONTE
- **Producer**: Garage (V quando crea 4 auto)
- **Consumer**: Incrocio (P per aspettare notifica)
- **Valore**: 0→1→0 ciclicamente

#### Semaforo SEM_AUTO_PASSAGGIO  
- **Producer**: Incrocio (V quando autorizza un'auto)
- **Consumer**: Automobili (P per aspettare autorizzazione)
- **Valore**: 0→1→0 per ogni auto

#### Semaforo SEM_AUTO_FINITA
- **Producer**: Automobili (V quando finiscono attraversamento)
- **Consumer**: Incrocio (P per aspettare completamento)  
- **Valore**: 0→1→0 per ogni auto

#### Semaforo SEM_MUTEX
- **Uso**: Protezione memoria condivisa
- **Tutti i processi**: P prima di leggere/scrivere, V dopo
- **Valore**: 1 (libero) ↔ 0 (occupato)

### Variabili di Coordinamento

#### stato_condiviso->prossima_auto
- **Scrittore**: Incrocio
- **Lettori**: Automobili  
- **Uso**: Comunica quale auto può attraversare

#### stato_condiviso->termine_richiesto
- **Scrittore**: Incrocio (in gestore_sigterm)
- **Lettori**: Garage, Automobili
- **Uso**: Segnale di terminazione coordinata

#### stato_condiviso->num_auto_attive
- **Scrittori**: Garage (+), Automobili (-)
- **Lettore**: Incrocio
- **Uso**: Contatore per terminazione ordinata

---
