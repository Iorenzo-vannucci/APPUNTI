#ifndef INCROCIO_H
#define INCROCIO_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/sem.h>
#include <time.h>
#include <errno.h>

// Costanti del progetto
#define NUM_AUTO 4
#define NUM_STRADE 4

// Chiavi IPC System V
#define SHM_KEY 0x1234
#define SEM_KEY 0x5678

// Semafori utilizzati
#define SEM_MUTEX 0           // Mutex per accesso alla memoria condivisa
#define SEM_AUTO_PRONTE 1     // Segnala che ci sono 4 auto pronte
#define SEM_AUTO_PASSAGGIO 2  // Semaforo per ogni auto che può passare
#define SEM_AUTO_FINITA 3     // Segnala che un'auto ha finito
#define NUM_SEMAFORI 4

// Struttura automobile
typedef struct {
    int strada_origine;      // 0, 1, 2, 3
    int strada_destinazione; // diversa da origine
    pid_t pid;              // PID del processo automobile
    int attiva;             // 1 se l'auto è attiva, 0 se terminata
} automobile_t;

// Struttura condivisa tra processi
typedef struct {
    automobile_t automobili[NUM_AUTO];  // Array delle 4 automobili
    int num_auto_attive;               // Numero di auto ancora attive
    int auto_pronte;                   // Flag: 4 auto sono state create
    int termine_richiesto;             // Flag: terminazione richiesta
    int prossima_auto;                 // Indice della prossima auto che può passare
} stato_incrocio_t;

// Funzioni di utilità
void inizializza_memoria_condivisa(void);
void connetti_memoria_condivisa(void);
void cleanup_risorse(void);
void gestore_sigterm(int sig);

// Funzioni per gestione IPC
void P(int sem_id, int sem_num);  // Wait
void V(int sem_id, int sem_num);  // Signal

// Funzioni per determinare precedenze
int EstraiDirezione(int iAutomobile);
int GetNextCar(int *Direzioni);

// Variabili globali (definite in ogni modulo)
extern int shm_id;
extern int sem_id;
extern stato_incrocio_t *stato_condiviso;

#endif // INCROCIO_H
