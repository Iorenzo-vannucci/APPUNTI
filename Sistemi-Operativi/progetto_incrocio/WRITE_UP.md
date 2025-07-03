# Simulatore di Incrocio Stradale - Write-Up Completo

## 📋 Panoramica del Progetto

Questo progetto implementa un simulatore di incrocio stradale che gestisce il traffico di automobili seguendo le regole di precedenza del codice della strada italiano. Il sistema utilizza **memoria condivisa** e **semafori POSIX** per sincronizzare i processi che rappresentano garage, incrocio e automobili.

### Architettura del Sistema
- **Garage**: processo principale che genera continuamente gruppi di 4 automobili
- **Incrocio**: processo che gestisce l'attraversamento secondo le regole di precedenza  
- **Automobili**: processi figli che rappresentano le singole auto in transito
- **Memoria Condivisa**: per scambiare informazioni tra processi
- **Semafori**: per sincronizzazione e mutua esclusione

---

## 🗂️ Analisi File per File

### 1. `condiviso.h` - Definizioni e Strutture Dati

Questo header contiene tutte le definizioni condivise tra i processi:

#### Costanti e Nomi dei Semafori
```c
#define SHM_NAME       "/incrocio_shm"     // Memoria condivisa
#define SEM_GARAGE     "/sem_garage"       // garage → incrocio
#define SEM_DONE       "/sem_done"         // auto → incrocio  
#define SEM_AUTO_FMT   "/sem_auto_%d"      // incrocio → auto i
#define SEM_FILE_WRITE "/sem_file_write"   // mutex per scrittura file
#define MAX_AUTO       4                   // Numero fisso di auto per gruppo
```

#### Strutture Dati
- **`car_t`**: rappresenta una singola automobile con PID, strada di provenienza e destinazione
- **`shared_data_t`**: array di 4 automobili condiviso in memoria

#### Funzioni per la Logica di Precedenza
- `GetDistanceFromStreet()`: calcola distanza tra strada origine e destinazione
- `StreetOnTheLeft()`: determina la strada a sinistra di una data posizione
- `EstraiDirezione()`: estrae casualmente una destinazione diversa dall'origine
- `GetNextCar()`: **funzione chiave** che determina quale auto ha precedenza

### 2. `src/garage.c` - Generatore di Automobili

Il garage è il **processo principale** che coordina l'intera simulazione:

#### Inizializzazione del Sistema
1. **Pulizia Risorse Precedenti**: rimuove memoria condivisa residua
2. **Creazione Memoria Condivisa**: crea e mappa `shared_data_t`
3. **Creazione Semafori**:
   - `sem_garage`: comunicazione garage→incrocio (valore iniziale: 0)
   - `sem_done`: notifica completamento auto→incrocio (valore iniziale: 0)
   - `sem_file_write`: mutex per scrittura file (valore iniziale: 1)
   - `sem_auto[0-3]`: uno per ogni automobile (valori iniziali: 0)

#### Loop Principale - Generazione Continua di Auto
```c
while (1) {
    // Per ogni strada (0-3), crea un'automobile
    for (int i = 0; i < MAX_AUTO; ++i) {
        int dest = EstraiDirezione(i);  // Destinazione casuale
        pid_t pid = fork();
        
        if (pid == 0) {
            // FIGLIO: diventa processo automobile
            execl("./build/automobile", "automobile", arg_from, arg_to, NULL);
        } else {
            // PADRE: registra auto in memoria condivisa
            shm->cars[i] = {pid, i, dest};
        }
    }
    
    // Notifica all'incrocio che le 4 auto sono pronte
    sem_post(sem_garage);
    
    // Attende che tutte le auto terminino
    for (int i = 0; i < MAX_AUTO; ++i) {
        waitpid(-1, &status, 0);
    }
    
    sleep(1);  // Pausa prima del prossimo gruppo
}
```

### 3. `src/incrocio.c` - Controllore del Traffico

L'incrocio gestisce l'attraversamento seguendo le **regole di precedenza**:

#### Gestione dei Segnali
```c
volatile sig_atomic_t keep_running = 1;

void signal_handler(int sig) {
    switch (sig) {
        case SIGINT:   // CTRL+C ignorato
            printf("SIGINT ignorato\n");
            break;
        case SIGTERM:  // Terminazione pulita
            keep_running = 0;
            break;
    }
}
```

#### Loop Principale di Gestione Traffico
```c
while (keep_running) {
    // 1. Attende notifica dal garage
    sem_wait(sem_garage);
    
    // 2. Copia destinazioni delle auto
    int direzioni[MAX_AUTO];
    for (int i = 0; i < MAX_AUTO; ++i) {
        direzioni[i] = shm->cars[i].to;
    }
    
    // 3. Gestisce attraversamento delle 4 auto
    for (int pass = 0; pass < MAX_AUTO && keep_running; ++pass) {
        // Determina quale auto ha precedenza
        int k = GetNextCar(direzioni);
        
        // Marca auto come già attraversata
        direzioni[k] = -1;
        
        // Autorizza l'auto k ad attraversare
        sem_post(sem_auto[k]);
        
        // Attende conferma attraversamento
        sem_wait(sem_done);
    }
}
```

#### Cleanup delle Risorse
La funzione `cleanup_resources()` si occupa di chiudere ordinatamente memoria condivisa e semafori.

### 4. `src/automobile.c` - Processo Automobile

Ogni automobile è un **processo figlio** che rappresenta un'auto in transito:

#### Parsing Argomenti e Inizializzazione
```c
int main(int argc, char *argv[]) {
    int from = atoi(argv[1]);  // Strada di provenienza
    int to = atoi(argv[2]);    // Strada di destinazione (non usata direttamente)
    
    // Apertura semafori necessari
    sem_t *sem_auto = sem_open(SEM_AUTO_FMT, from);  // Per ricevere autorizzazione
    sem_t *sem_done = sem_open(SEM_DONE);            // Per notificare completamento
    sem_t *sem_file_write = sem_open(SEM_FILE_WRITE); // Mutex per log
}
```

#### Attraversamento e Logging
```c
// Attende autorizzazione dall'incrocio
sem_wait(sem_auto);

// Simula attraversamento
sleep(1);

// Scrittura ATOMICA nei file di log
sem_wait(sem_file_write);
// Scrive in log/auto.txt
// Scrive in log/incrocio.txt (per mantenere sincronizzazione)
sem_post(sem_file_write);

// Notifica completamento all'incrocio
sem_post(sem_done);

_exit(EXIT_SUCCESS);
```

### 5. `src/direzioni.c` - Logica di Precedenza

Questo file implementa la **logica del codice della strada** per determinare le precedenze:

#### Funzioni di Calcolo Geometrico
- **`GetDistanceFromStreet()`**: calcola la "distanza angolare" tra strade
- **`StreetOnTheLeft()`**: determina la strada a sinistra con rotazione modulo 4

#### Generazione Casuale Destinazioni
```c
int EstraiDirezione(int iMyStreet) {
    int iDirezione = iMyStreet;
    struct timeval tv;
    
    // Estrae destinazione diversa dalla strada di origine
    while(iDirezione == iMyStreet) {
        gettimeofday(&tv, NULL);
        iDirezione = (tv.tv_usec) % NUM_STRADE;
    }
    return iDirezione;
}
```

#### Algoritmo di Precedenza - `GetNextCar()`
Questa è la **funzione chiave** che implementa le regole del codice della strada:

1. **Prima priorità**: auto che svoltano a destra (distanza = 1)
2. **Controllo destra libera**: verifica che non ci siano auto dalla destra
3. **Gestione incroci complessi**: valuta conflitti con auto di fronte
4. **Fallback**: se nessuna regola si applica, sceglie la prima auto disponibile

```c
// Pseudo-codice semplificato
for (ogni strada i) {
    if (auto i svolta a destra) {
        return i;  // Precedenza immediata
    }
    if (destra libera && gestione_conflitti_ok) {
        return i;
    }
}
```

### 6. `build.sh` - Script di Compilazione

Lo script automatizza la compilazione gestendo le differenze tra macOS e Linux:

```bash
# Gestione librerie platform-specific
if [[ "$(uname)" == "Darwin" ]]; then
  EXTRA_LIBS=""        # macOS non richiede -lrt
else
  EXTRA_LIBS="-lrt"    # Linux richiede real-time library
fi

# Compilazione dei tre eseguibili
gcc -o build/garage     src/garage.c     src/direzioni.c $EXTRA_LIBS
gcc -o build/incrocio   src/incrocio.c   src/direzioni.c $EXTRA_LIBS  
gcc -o build/automobile src/automobile.c                   $EXTRA_LIBS
```

### 7. `run.sh` - Script di Esecuzione

Gestisce l'avvio e la terminazione pulita del sistema:

```bash
# 1. Avvia garage in background
./build/garage &

# 2. Attesa per inizializzazione risorse
sleep 1

# 3. Avvia incrocio (processo principale)
./build/incrocio

# 4. Cleanup automatico alla terminazione
cleanup() {
    pkill -f "./build/garage"
    pkill -f "./build/incrocio" 
    pkill -f "./build/automobile"
}
```

---

## 🔄 Flusso di Esecuzione Completo

### 1. **Fase di Inizializzazione**
1. `garage` crea memoria condivisa e tutti i semafori
2. `incrocio` si connette alle risorse condivise
3. Sistema pronto per simulazione

### 2. **Ciclo di Simulazione** (ripetuto infinitamente)
1. **Garage genera 4 auto**: una per ogni strada (0-3)
2. **Fork + Exec**: ogni auto diventa processo `automobile`
3. **Notifica incrocio**: `sem_post(sem_garage)`
4. **Incrocio gestisce attraversamenti**:
   - Applica regole di precedenza con `GetNextCar()`
   - Autorizza auto una alla volta: `sem_post(sem_auto[k])`
   - Attende conferma: `sem_wait(sem_done)`
5. **Auto attraversano**: simulazione + logging
6. **Sincronizzazione**: garage attende terminazione di tutte le auto
7. **Pausa e ricomincia**

### 3. **Gestione della Terminazione**
- **SIGINT (Ctrl+C)**: ignorato dall'incrocio per evitare terminazioni accidentali
- **SIGTERM**: terminazione pulita con cleanup delle risorse
- **Script cleanup**: garantisce terminazione di tutti i processi

---

## 🔧 Dettagli Tecnici

### Sincronizzazione Inter-Processo
- **Memoria condivisa**: scambio dati tra garage e incrocio
- **Semafori named**: comunicazione asincrona tra processi
- **Mutex per file I/O**: scrittura atomica nei log

### Algoritmo di Precedenza
Il sistema implementa una **versione semplificata** del codice della strada:
1. **Destra sempre**: priorità alle auto che svoltano a destra
2. **Destra libera**: controllo che non arrivino auto dalla destra
3. **Valutazione conflitti**: gestione incroci con auto di fronte
4. **Risoluzione deadlock**: fallback per situazioni ambigue

### Logging e Debugging
- **File `log/auto.txt`**: traccia delle auto che attraversano
- **File `log/incrocio.txt`**: mirror sincronizzato per verifica
- **Output console**: messaggi di debug e stato del sistema

---

## ⚡ Caratteristiche Avanzate

### Robustezza
- **Gestione segnali**: terminazione pulita e controllo errori
- **Cleanup automatico**: rimozione risorse in caso di errori
- **Gestione interruzioni**: system call interrompibili gestite correttamente

### Portabilità
- **Cross-platform**: supporto macOS e Linux
- **Gestione librerie**: adattamento automatico delle dipendenze

### Scalabilità
- **Configurabile**: `MAX_AUTO` modificabile per gruppi di dimensioni diverse
- **Modulare**: logica di precedenza separata e sostituibile

---

## 🎯 Conclusioni

Questo simulatore rappresenta un **ottimo esempio** di programmazione di sistema che combina:

- **Concorrenza**: gestione di processi multipli sincronizzati
- **IPC avanzato**: memoria condivisa e semafori POSIX
- **Algoritmi complessi**: implementazione regole di precedenza
- **Robustezza**: gestione errori e terminazione pulita
- **Best practices**: codice modulare e ben documentato

Il sistema dimostra come implementare **comunicazione inter-processo efficiente** per simulare scenari del mondo reale con vincoli di sincronizzazione complessi. 