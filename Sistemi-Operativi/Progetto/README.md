# Progetto Incrocio
## Sistemi Operativi con Laboratorio - A.A. 2024-25

Simulazione del passaggio di automobili attraverso un quadrivio (incrocio a 4 strade) utilizzando processi Unix/Linux e comunicazione tramite IPC System V.

## 📋 Specifiche del Progetto

Il progetto simula un incrocio stradale con:
- **3 processi distinti**: `incrocio`, `garage`, e `automobile` (processo separato per ogni auto)
- **4 strade numerate**: 0, 1, 2, 3
- **Comunicazione tramite IPC System V**: memoria condivisa e semafori
- **Regole del codice della strada**: per determinare l'ordine di attraversamento

### Comportamento dei Processi

#### 🚦 Processo Incrocio
1. Attende notifica dal garage che ci sono 4 automobili
2. Determina quale auto può attraversare secondo le regole stradali
3. Scrive nel file `incrocio.txt` la strada di origine dell'auto scelta
4. Emette messaggio a video
5. Comunica all'auto che può attraversare
6. Attende che l'auto termini l'attraversamento
7. Ripete per tutte e 4 le auto
8. **Terminazione**: con SIGTERM, termina per ultimo dopo tutti gli altri processi

#### 🏭 Processo Garage
1. Crea 4 processi automobile (uno per strada) con `fork()`
2. Estrae casualmente la destinazione per ogni auto (diversa dall'origine)
3. Emette messaggio per ogni auto creata
4. Notifica all'incrocio che ci sono 4 auto pronte
5. Attende che tutte le auto terminino
6. Aspetta 1 secondo
7. Riprende dal punto 1

#### 🚗 Processo Automobile
1. Attende autorizzazione dall'incrocio
2. Attraversa l'incrocio
3. Scrive nel file `auto.txt` la propria strada di origine
4. Comunica all'incrocio che ha finito e termina

### ✅ Risultato Atteso
I file `incrocio.txt` e `auto.txt` devono essere **identici** al termine dell'esecuzione.

## 🏗️ Architettura

```
┌──────────────────┐    ┌─────────────────┐    ┌──────────────────┐
│   Processo       │    │   Processo      │    │      Processo    │
│   Incrocio       │◄──►│   Garage        │    │   Automobile     │
│                  │    │                 │    │   (4 istanze)    │
│ • Gestisce       │    │ • Crea auto     │    │ • Attraversa     │
│   attraversamento│    │ • Ciclo infinito│    │ • Termina        │
│ • Scrive log     │    │ • fork() + exec │    │ • Scrive log     │
│ • Termina ultimo │    │ • Attesa sync   │    │                  │
└──────────────────┘    └─────────────────┘    └──────────────────┘
         │                       │                        │
         └───────────────────────┼────────────────────────┘
                                 │
                    ┌─────────────────────────┐
                    │     IPC System V        │
                    │ • Memoria Condivisa     │
                    │ • Semafori per Sync     │
                    │ • Chiavi: 0x1234/0x5678 │
                    └─────────────────────────┘
```

## 📁 Struttura dei File

```
Progetto/
├── include/
│   └── incrocio.h          # Header con strutture e definizioni
├── src/
│   ├── incrocio.c          # Processo principale di gestione incrocio
│   ├── garage.c            # Processo generatore di automobili
│   ├── automobile.c        # Processo automobile
│   └── utils.c             # Funzioni IPC e utilità
├── build.sh                # Script di compilazione
├── run.sh                  # Script di avvio e test
├── README.md               # Questa documentazione
├── incrocio.txt            # File di log creato dall'incrocio
└── auto.txt                # File di log creato dalle automobili
```

## 🚀 Compilazione ed Esecuzione

### Compilazione
```bash
./build.sh
```

### Esecuzione Completa (Raccomandato)
```bash
./run.sh
```
Questo script:
- Compila il progetto
- Pulisce risorse IPC precedenti
- Avvia i processi in ordine corretto
- Monitora l'esecuzione
- Verifica che i file di output siano identici

### Esecuzione Manuale
```bash
# 1. Avvia l'incrocio (per primo)
./build/bin/incrocio &
INCROCIO_PID=$!

# 2. Avvia il garage (per secondo)
./build/bin/garage &

# 3. Per terminare gracefully (IMPORTANTE: solo SIGTERM!)
kill -TERM $INCROCIO_PID

# NOTA: Ctrl+C NON termina gracefully secondo le specifiche
```

## 🔧 Dettagli Tecnici

### IPC System V utilizzato
- **Memoria Condivisa**: chiave `0x1234`
  - Struttura `stato_incrocio_t` con array di automobili
  - Flags di stato e controllo
- **Semafori**: chiave `0x5678`
  - `SEM_MUTEX`: protezione memoria condivisa
  - `SEM_AUTO_PRONTE`: notifica dal garage all'incrocio
  - `SEM_AUTO_PASSAGGIO`: autorizzazione dall'incrocio all'auto
  - `SEM_AUTO_FINITA`: conferma di attraversamento completato

### Funzioni Specificate nel Progetto
- `int EstraiDirezione(int iAutomobile)`: estrae destinazione casuale
- `int GetNextCar(int *Direzioni)`: determina auto con precedenza

### Gestione Segnali
- **SIGTERM**: terminazione controllata (SOLO processo incrocio)
- **SIGINT**: NON gestito secondo le specifiche del progetto
- **Ctrl+C**: NON termina gracefully - usare `kill -TERM <PID_incrocio>`

## 🧪 Test e Verifica

Il progetto include verifiche automatiche:

1. **Compilazione**: controllo errori di build
2. **Sincronizzazione**: verifica ordine di avvio processi
3. **Output**: confronto `incrocio.txt` vs `auto.txt`
4. **Cleanup**: rimozione automatica risorse IPC

### Comandi Utili per Debug
```bash
# Visualizza processi attivi
ps aux | grep -E '(incrocio|garage|automobile)'

# Visualizza risorse IPC
ipcs -m  # memoria condivisa
ipcs -s  # semafori

# Monitora file di log in tempo reale
tail -f incrocio.txt auto.txt

# Pulisci risorse IPC manualmente
ipcrm -M 0x1234  # memoria condivisa
ipcrm -S 0x5678  # semafori
```

## 📝 Requisiti di Sistema

- **Sistema Operativo**: Unix/Linux/macOS
- **Compiler**: GCC o Clang con supporto C99
- **Librerie**: Standard POSIX + System V IPC
- **Permessi**: utente normale (non root)

## ⚠️ Note Importanti

1. **Ordine di avvio**: l'incrocio deve essere avviato PRIMA del garage
2. **Terminazione**: SOLO il processo incrocio gestisce SIGTERM
3. **Ctrl+C**: NON funziona per terminazione graceful - usare `kill -TERM`
4. **File di output**: devono essere identici per il successo del test
5. **Cleanup**: le risorse IPC vengono automaticamente rimosse

## 🎓 Obiettivi Didattici

Questo progetto dimostra:
- ✅ Creazione e gestione di processi con `fork()` e `exec()`
- ✅ Comunicazione tra processi tramite IPC System V
- ✅ Sincronizzazione con semafori
- ✅ Gestione corretta dei segnali Unix
- ✅ Coordinamento di processi multipli
- ✅ Cleanup delle risorse di sistema

---

**Autore**: Progetto per il corso di Sistemi Operativi con Laboratorio  
**Anno Accademico**: 2024-25
