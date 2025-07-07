# Progetto Incrocio - Simulatore di Traffico

## Panoramica del Progetto

Il **Progetto Incrocio** è un simulatore di traffico che implementa la gestione di un incrocio stradale a 4 strade utilizzando i concetti fondamentali dei sistemi operativi. Il sistema simula automobili che attraversano un incrocio seguendo le regole del codice della strada italiano, utilizzando processi multipli, memoria condivisa e semafori per la sincronizzazione.

## Architettura del Sistema

Il sistema è composto da tre processi principali:

1. **Garage** (`garage.c`) - Processo generatore di automobili
2. **Incrocio** (`incrocio.c`) - Processo gestore del traffico 
3. **Automobile** (`automobile.c`) - Processo rappresentante ogni singola auto

### Schema di Funzionamento

```
   Strada 0
      |
      ↓
Strada 3 ← [INCROCIO] → Strada 1  
      ↑
      |
   Strada 2
```

## File di Configurazione e Header

### `incrocio.h` - Logiche di Precedenza - Strutture Dati Condivise

Questo file contiene tutte le definizioni condivise tra i processi:

**Costanti principali:**
- `SHM_NAME "/incrocio_shm"` - Nome della memoria condivisa
- `SEM_GARAGE "/sem_garage"` - Semaforo garage → incrocio  
- `SEM_DONE "/sem_done"` - Semaforo auto → incrocio
- `SEM_AUTO_FMT "/sem_auto_%d"` - Template per semafori incrocio → auto
- `SEM_FILE_WRITE "/sem_file_write"` - Mutex per scrittura file di log
- `MAX_AUTO 4` - Numero massimo di auto per gruppo

**Struttura `car_t`:**
```c
typedef struct {
    pid_t  pid;   // PID del processo automobile
    int    from;  // strada di provenienza (0–3)
    int    to;    // strada di destinazione (0–3)
} car_t;
```

**Struttura `shared_data_t`:**
```c
typedef struct {
    car_t cars[MAX_AUTO];
    volatile int terminate_flag;  // Flag per terminazione coordinata
} shared_data_t;
```

**Funzioni helper:**
- `GetDistanceFromStreet()` - Calcola distanza tra strade per precedenze
- `StreetOnTheLeft()` - Identifica strada a sinistra a una certa distanza
- `EstraiDirezione()` - Genera casualmente destinazione diversa da origine
- `GetNextCar()` - Determina quale auto ha precedenza secondo codice stradale



Contiene l'implementazione completa delle regole del codice della strada:

**Algoritmo di precedenza (`GetNextCar`):**
1. **Controllo svolta a destra**: Auto che svolta immediatamente a destra ha sempre precedenza
2. **Controllo destra libera**: Verifica se c'è traffico dalla destra
3. **Controllo auto di fronte**: Gestisce precedenze con auto che arriva di fronte
4. **Fallback**: Se nessuna regola si applica, passa la prima auto disponibile

Il sistema implementa correttamente le precedenze:
- Chi svolta a destra passa sempre per primo
- Chi ha la destra libera ha precedenza  
- In caso di conflitto, precedenza a chi fa manovra meno impegnativa

## Script di Build e Esecuzione

### `build.sh` - Script di Compilazione

```bash
#!/usr/bin/env bash
set -e

# Gestione multipiattaforma (macOS/Linux)
if [[ "$(uname)" == "Darwin" ]]; then
  EXTRA_LIBS=""        # macOS non richiede -lrt
else
  EXTRA_LIBS="-lrt"    # Linux richiede real-time library
fi

# Compilazione dei tre eseguibili
gcc -o build/garage     src/garage.c      $EXTRA_LIBS
gcc -o build/incrocio   src/incrocio.c    $EXTRA_LIBS  
gcc -o build/automobile src/automobile.c  $EXTRA_LIBS
```

**Funzionalità:**
- Crea directory `build/` per eseguibili
- Gestione automatica dipendenze sistema operativo
- Compilazione con error handling (`set -e`)
- Output colorato per feedback utente

### `run.sh` - Script di Avvio Sistema

```bash
#!/usr/bin/env bash
set -e

# Preparazione ambiente
mkdir -p log                          # Crea directory log
rm -f log/incrocio.txt log/auto.txt  # Pulisce log precedenti

# Avvio coordinato processi
./build/garage &    # Garage in background (crea risorse)
sleep 1             # Attesa creazione risorse
./build/incrocio    # Incrocio in foreground (processo principale)
```

**Sequenza di avvio:**
1. **Preparazione**: Crea directory e pulisce log
2. **Garage**: Avviato in background, crea shared memory e semafori
3. **Attesa**: Pausa per garantire inizializzazione risorse
4. **Incrocio**: Avviato in foreground come processo principale

## Processi Principali

### `garage.c` - Generatore di Automobili

Il garage è il **processo coordinatore** che gestisce l'intero ciclo di vita del sistema.

**Responsabilità principali:**

1. **Inizializzazione Sistema:**
   ```c
   // Pulizia risorse precedenti
   shm_unlink(SHM_NAME);
   
   // Creazione shared memory
   int shm_fd = shm_open(SHM_NAME, O_CREAT | O_RDWR, 0666);
   ftruncate(shm_fd, sizeof(shared_data_t));
   shared_data_t *shm = mmap(NULL, sizeof(shared_data_t), ...);
   ```

2. **Creazione Semafori:**
   ```c
   sem_t *sem_garage = sem_open(SEM_GARAGE, O_CREAT, 0666, 0);
   sem_t *sem_done = sem_open(SEM_DONE, O_CREAT, 0666, 0);
   sem_t *sem_file_write = sem_open(SEM_FILE_WRITE, O_CREAT, 0666, 1);
   
   // Semafori per ogni automobile (4 totali)
   for (int i = 0; i < MAX_AUTO; ++i) {
       snprintf(sem_name, sizeof(sem_name), SEM_AUTO_FMT, i);
       sem_auto_arr[i] = sem_open(sem_name, O_CREAT, 0666, 0);
   }
   ```

3. **Generazione Automobili:**
   ```c
   while (keep_running && !shm->terminate_flag) {
       for (int i = 0; i < MAX_AUTO; ++i) {
           int dest = EstraiDirezione(i);  // Destinazione casuale
           pid_t pid = fork();
           
           if (pid == 0) {
               // FIGLIO: diventa processo automobile
               execl("./build/automobile", "automobile", from_str, to_str, NULL);
           } else {
               // PADRE: registra auto in shared memory
               shm->cars[i].pid = pid;
               shm->cars[i].from = i;
               shm->cars[i].to = dest;
           }
       }
       
       sem_post(sem_garage);  // Segnala gruppo pronto all'incrocio
       
       // Attende terminazione di tutte le auto del gruppo
       for (int i = 0; i < MAX_AUTO; ++i) {
           waitpid(-1, &status, 0);
       }
   }
   ```

**Gestione Segnali:**
- `SIGINT/SIGQUIT`: Ignorati (solo per debug)
- `SIGTERM`: Terminazione pulita con cleanup risorse

**Cleanup Finale:**
- Chiusura e rimozione di tutti i semafori (`sem_close`, `sem_unlink`)
- Terminazione processi figlio rimanenti (`waitpid`)
- Rimozione shared memory (`munmap`, `shm_unlink`)

### `incrocio.c` - Gestore del Traffico

L'incrocio è il **processo arbitro** che decide quale automobile può attraversare.

**Responsabilità principali:**

1. **Connessione alle Risorse:**
   ```c
   // Apertura shared memory (creata dal garage)
   int shm_fd = shm_open(SHM_NAME, O_RDWR, 0666);
   shared_data_t *shm = mmap(NULL, sizeof(shared_data_t), ...);
   
   // Apertura semafori (creati dal garage)
   sem_t *sem_garage = sem_open(SEM_GARAGE, 0);
   sem_t *sem_done = sem_open(SEM_DONE, 0);
   for (int i = 0; i < MAX_AUTO; ++i) {
       sem_auto[i] = sem_open(sem_auto_name, 0);
   }
   ```

2. **Loop Principale di Gestione:**
   ```c
   while (keep_running && !shm->terminate_flag) {
       // Attesa segnale dal garage (nuovo gruppo auto)
       sem_wait(sem_garage);
       
       // Costruzione array direzioni per algoritmo precedenze
       int direzioni[MAX_AUTO];
       for (int i = 0; i < MAX_AUTO; ++i) {
           direzioni[i] = shm->cars[i].to;
       }
       
       // Gestione attraversamento di tutte e 4 le auto
       for (int pass = 0; pass < MAX_AUTO; ++pass) {
           int k = GetNextCar(direzioni);  // Calcolo precedenze
           direzioni[k] = -1;              // Marca auto come processata
           
           printf("auto %d da %d verso %d può attraversare\n", 
                  k, shm->cars[k].from, shm->cars[k].to);
           
           sem_post(sem_auto[k]);          // Autorizza attraversamento
           sem_wait(sem_done);             // Attende conferma completamento
       }
   }
   ```

**Algoritmo di Precedenza:**
- Utilizza `GetNextCar()` per determinare quale auto ha diritto di passaggio
- Rispetta rigorosamente le regole del codice stradale italiano
- Garantisce che tutte le auto attraversino in ordine corretto

**Gestione Segnali:**
- `SIGINT/SIGQUIT`: Ignorati (solo incrocio può decidere terminazione)
- `SIGTERM`: Terminazione coordinata con impostazione flag

### `automobile.c` - Processo Automobile

Ogni automobile è un **processo indipendente** che simula l'attraversamento.

**Parametri di Input:**
- `argv[1]`: strada di provenienza (0-3)
- `argv[2]`: strada di destinazione (0-3)

**Ciclo di Vita:**

1. **Apertura Semafori:**
   ```c
   // Semaforo specifico per questa auto
   char sem_name[32];
   snprintf(sem_name, sizeof(sem_name), SEM_AUTO_FMT, from);
   sem_t *sem_auto = sem_open(sem_name, 0);
   
   // Semafori comuni
   sem_t *sem_done = sem_open(SEM_DONE, 0);
   sem_t *sem_file_write = sem_open(SEM_FILE_WRITE, 0);
   ```

2. **Attesa Autorizzazione:**
   ```c
   sem_wait(sem_auto);  // Blocca fino a autorizzazione incrocio
   ```

3. **Attraversamento e Logging:**
   ```c
   // Acquisizione mutex per scrittura atomica
   sem_wait(sem_file_write);
   
   // Apertura simultanea di entrambi i file di log
   int fd1 = open("log/auto.txt", O_CREAT | O_APPEND | O_WRONLY, 0666);
   int fd2 = open("log/incrocio.txt", O_CREAT | O_APPEND | O_WRONLY, 0666);
   
   // Scrittura atomica su entrambi i file
   char buf[16];
   int len = snprintf(buf, sizeof(buf), "%d\n", from);
   write(fd1, buf, len);
   write(fd2, buf, len);
   
   close(fd1);
   close(fd2);
   sem_post(sem_file_write);
   ```

4. **Notifica Completamento:**
   ```c
   sem_post(sem_done);  // Segnala all'incrocio il completamento
   _exit(EXIT_SUCCESS); // Terminazione pulita
   ```

**Caratteristiche Importanti:**
- **Logging Atomico**: Usa mutex per garantire scrittura consistente
- **Doppio Log**: Scrive simultaneamente su `auto.txt` e `incrocio.txt`
- **Terminazione Pulita**: Usa `_exit()` per evitare cleanup del parent

## Meccanismi di Sincronizzazione

### Schema dei Semafori

```
garage ──[sem_garage]──> incrocio
                            │
                            ├─[sem_auto_0]─> automobile_0
                            ├─[sem_auto_1]─> automobile_1  
                            ├─[sem_auto_2]─> automobile_2
                            └─[sem_auto_3]─> automobile_3
                                │
automobile_* ──[sem_done]──────┘

[sem_file_write] ← mutex per logging atomico
```

### Protocollo di Comunicazione

1. **Inizializzazione** (garage):
   - Crea shared memory e tutti i semafori
   - Genera gruppo di 4 automobili
   - Registra dati auto in shared memory

2. **Segnalazione Gruppo Pronto** (garage → incrocio):
   ```c
   sem_post(sem_garage);  // "Gruppo di 4 auto pronto"
   ```

3. **Gestione Attraversamenti** (incrocio):
   ```c
   for (ogni auto nel gruppo) {
       k = GetNextCar(direzioni);      // Calcola precedenza
       sem_post(sem_auto[k]);          // "Auto k può attraversare"
       sem_wait(sem_done);             // Attende "attraversamento completato"
   }
   ```

4. **Attraversamento** (automobile):
   ```c
   sem_wait(sem_auto[from]);  // Attende autorizzazione
   // ... attraversamento e logging ...
   sem_post(sem_done);        // "Attraversamento completato"
   ```

### Gestione della Memoria Condivisa

**Struttura condivisa:**
```c
shared_data_t {
    car_t cars[4];              // Dati delle 4 auto correnti
    volatile int terminate_flag; // Flag di terminazione globale
}
```

**Accesso ai dati:**
- **Garage**: Scrive dati delle auto (`cars[i].pid`, `from`, `to`)
- **Incrocio**: Legge dati per algoritmo precedenze (`cars[i].from`, `cars[i].to`)
- **Automobili**: Non accedono direttamente alla shared memory

## File di Log

Il sistema genera due file di log identici:

### `log/auto.txt` e `log/incrocio.txt`

**Formato**: Un numero per riga rappresentante la strada di provenienza dell'auto che ha attraversato

**Esempio:**
```
0
2  
1
3
0
1
3
2
```

**Significato**: Le auto sono attraversate in quest'ordine:
- Auto dalla strada 0
- Auto dalla strada 2  
- Auto dalla strada 1
- Auto dalla strada 3
- (nuovo gruppo) Auto dalla strada 0
- etc.

**Garanzie di Consistenza:**
- **Logging atomico**: Mutex `sem_file_write` garantisce scrittura atomica
- **Doppia scrittura**: Ogni auto scrive simultaneamente su entrambi i file
- **Sincronizzazione**: Ordine riflette esattamente l'ordine di attraversamento

## Gestione degli Errori e Terminazione

### Gestione Segnali

**Processo Garage:**
- Ignora `SIGINT` e `SIGQUIT` per evitare terminazioni accidentali
- Risponde a `SIGTERM` con cleanup completo delle risorse

**Processo Incrocio:**  
- Ignora `SIGINT` e `SIGQUIT` (solo l'incrocio decide quando fermarsi)
- Risponde a `SIGTERM` impostando flag di terminazione

**Processi Automobile:**
- Gestione standard dei segnali (terminazione immediata se necessario)

### Cleanup delle Risorse

**Ordine di cleanup (garage):**
1. Terminazione processi figlio rimanenti (`waitpid`)
2. Chiusura semafori (`sem_close`)  
3. Rimozione semafori dal sistema (`sem_unlink`)
4. Rimozione shared memory (`munmap`, `shm_unlink`)

**Robustezza:**
- Ogni processo verifica sempre il valore di ritorno delle system call
- Gestione graceful degli errori con `perror()` e exit codes appropriati
- Cleanup automatico delle risorse in caso di terminazione imprevista

## Caratteristiche Avanzate

### Portabilità Multi-Piattaforma

Il sistema funziona sia su **Linux** che su **macOS**:

```bash
# Gestione automatica delle dipendenze
if [[ "$(uname)" == "Darwin" ]]; then
  EXTRA_LIBS=""        # macOS include POSIX di default
else  
  EXTRA_LIBS="-lrt"    # Linux richiede real-time library
fi
```

### Generazione Pseudocasuale Deterministica

```c
int EstraiDirezione(int iMyStreet) {
    int iDirezione = iMyStreet;
    struct timeval tv;
    
    while(iDirezione == iMyStreet) {
        gettimeofday(&tv, NULL);           // Timestamp microsecondi
        long l = tv.tv_usec % NUM_STRADE;  // Modulo per 0-3
        iDirezione = (int)l;
    }
    return iDirezione;
}
```

**Caratteristiche:**
- Usa timestamp per garantire casualità
- Garantisce destinazione diversa da origine
- Deterministica ma imprevedibile

### Algoritmo Ottimizzato per Precedenze

L'implementazione di `GetNextCar()` è ottimizzata per gestire tutti i casi del codice stradale:

1. **Prima passata**: Cerca auto con precedenza assoluta (svolta a destra o situazioni semplici)
2. **Seconda passata**: Se nessuna precedenza assoluta, applica regole complesse
3. **Fallback**: Se nessuna regola si applica, passa la prima auto disponibile

Questo garantisce **deadlock-free operation** e rispetto delle regole stradali.

