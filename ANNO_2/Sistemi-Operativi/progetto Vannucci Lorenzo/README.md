# Progetto: Simulazione di Incrocio Stradale con Garage e Automobili

## 📌 Obiettivo
Il progetto simula la gestione di un **incrocio stradale** connesso a un **garage** da cui escono automobili.  
L’obiettivo è modellare la sincronizzazione e la comunicazione tra processi indipendenti (garage, incrocio e automobili) tramite:
- **Memoria condivisa (POSIX shared memory)**
- **Semafori POSIX (unnamed/named)**
- **Gestione dei segnali (SIGINT, SIGTERM, ecc.)**

---

## 🏗️ Architettura del sistema
Il sistema è composto da tre programmi principali:

1. **`garage.c`**  
   - Rappresenta il garage che genera i processi *automobili*.  
   - Si occupa di inizializzare memoria condivisa e semafori.  
   - Coordina la creazione delle automobili e segnala la loro partenza.  
   - Intercetta i segnali di sistema (SIGINT, SIGTERM) e gestisce correttamente la terminazione.

2. **`automobile.c`**  
   - Ogni automobile è un processo separato.  
   - Accetta due parametri:  
     ```
     automobile <from> <to>
     ```
     - `from`: punto di ingresso (da dove parte l’auto).  
     - `to`: punto di uscita (dove deve andare).  
   - L’automobile utilizza un semaforo dedicato (`SEM_AUTO_FMT`) per coordinarsi con l’incrocio.  
   - Una volta attraversato l’incrocio, segnala il completamento al garage/incrocio e termina.

3. **`incrocio.c`**  
   - Rappresenta il gestore dell’incrocio.  
   - Coordina le automobili in arrivo da più direzioni evitando conflitti.  
   - Usa i semafori per concedere il via libera alle auto e per garantire che non ci siano collisioni logiche.  
   - Gestisce i segnali di sistema e rilascia correttamente le risorse (shm, semafori).

---

## 🔑 Meccanismi di Sincronizzazione
- **Memoria condivisa (`shared_data_t`)**  
  Usata per scambiare informazioni tra garage, incrocio e automobili.  
  Ad esempio: lo stato dell’incrocio, quante auto devono ancora passare, ecc.  
  (La struttura è definita in `incrocio.h`, non incluso qui).

- **Semafori**  
  - `SEM_GARAGE_DONE`: segnala che il garage ha terminato l’inizializzazione.  
  - `SEM_AUTO_FMT`: semafori nominati dinamicamente per ogni automobile (es. `/sem_auto_0`, `/sem_auto_1`, …).  
  - Semafori aggiuntivi per sincronizzare scrittura su file e aggiornamento memoria condivisa.

- **Segnali**  
  - `SIGINT`: ignorato per evitare chiusura accidentale con CTRL+C.  
  - `SIGTERM`: usato per terminazione controllata.  
  - Alla ricezione di un segnale, il programma stampa messaggi colorati per chiarezza.

---

## ⚙️ Flusso di Esecuzione
1. **Avvio del Garage (`garage.c`)**
   - Crea la memoria condivisa.  
   - Inizializza i semafori.  
   - Lancia processi `automobile`.

2. **Creazione Automobili (`automobile.c`)**
   - Ogni automobile attende il permesso dal semaforo.  
   - Una volta ottenuto, attraversa l’incrocio.  
   - Segnala il completamento al garage/incrocio e termina.

3. **Gestione Incrocio (`incrocio.c`)**
   - Coordina le automobili in arrivo.  
   - Rilascia il permesso ad attraversare in base alle regole dell’incrocio.  
   - Aggiorna lo stato della memoria condivisa.

---

