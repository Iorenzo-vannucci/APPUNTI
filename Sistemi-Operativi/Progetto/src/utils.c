#include "../include/incrocio.h"

// ============================================================================
// VARIABILI GLOBALI (condivise con tutti i file)
// ============================================================================

extern int shm_id;
extern int sem_id;
extern stato_incrocio_t *stato_condiviso;

// ============================================================================
// FUNZIONI IPC SYSTEM V - SEMAFORI
// ============================================================================

// Operazione P (Wait) sul semaforo
void P(int sem_id, int sem_num) {
    struct sembuf sb;
    sb.sem_num = sem_num;
    sb.sem_op = -1;  // Decrementa
    sb.sem_flg = 0;
    
    if (semop(sem_id, &sb, 1) == -1) {
        perror("Errore nella P (wait)");
        exit(EXIT_FAILURE);
    }
}

// Operazione V (Signal) sul semaforo
void V(int sem_id, int sem_num) {
    struct sembuf sb;
    sb.sem_num = sem_num;
    sb.sem_op = 1;   // Incrementa
    sb.sem_flg = 0;
    
    if (semop(sem_id, &sb, 1) == -1) {
        perror("Errore nella V (signal)");
        exit(EXIT_FAILURE);
    }
}

// ============================================================================
// FUNZIONI SPECIFICATE NEL PROGETTO
// ============================================================================

// Estrae a sorte una direzione diversa da quella di origine
int EstraiDirezione(int iAutomobile) {
    int destinazione;
    
    srand(time(NULL) + iAutomobile);
    
    do {
        destinazione = rand() % NUM_STRADE;
    } while (destinazione == iAutomobile);
    
    return destinazione;
}

// Determina quale auto può attraversare secondo le regole del codice stradale
// Implementazione semplificata: priorità alle auto con indice minore
int GetNextCar(int *Direzioni) {
    // Implementazione semplice: le auto attraversano in ordine 0, 1, 2, 3
    // In un'implementazione più realistica si dovrebbero considerare:
    // - Precedenza a destra
    // - Diritto di precedenza nelle svolte
    // - etc.
    
    static int ultima_auto = -1;
    
    for (int i = 0; i < NUM_AUTO; i++) {
        int auto_da_testare = (ultima_auto + 1 + i) % NUM_AUTO;
        if (Direzioni[auto_da_testare] != -1) {  // -1 indica auto già passata
            ultima_auto = auto_da_testare;
            return auto_da_testare;
        }
    }
    
    return -1;  // Nessuna auto da far passare
}

// ============================================================================
// FUNZIONI DI UTILITÀ
// ============================================================================

void inizializza_memoria_condivisa(void) {
    printf("Inizializzazione memoria condivisa e semafori...\n");
    
    // Crea memoria condivisa
    shm_id = shmget(SHM_KEY, sizeof(stato_incrocio_t), IPC_CREAT | 0666);
    if (shm_id == -1) {
        perror("Errore nella creazione della memoria condivisa");
        exit(EXIT_FAILURE);
    }
    
    // Collega memoria condivisa
    stato_condiviso = (stato_incrocio_t*)shmat(shm_id, NULL, 0);
    if (stato_condiviso == (stato_incrocio_t*)-1) {
        perror("Errore nel collegamento alla memoria condivisa");
        exit(EXIT_FAILURE);
    }
    
    // Crea semafori
    sem_id = semget(SEM_KEY, NUM_SEMAFORI, IPC_CREAT | 0666);
    if (sem_id == -1) {
        perror("Errore nella creazione dei semafori");
        exit(EXIT_FAILURE);
    }
    
    // Inizializza semafori
    semctl(sem_id, SEM_MUTEX, SETVAL, 1);        // Mutex inizializzato a 1
    semctl(sem_id, SEM_AUTO_PRONTE, SETVAL, 0);  // Auto pronte inizializzato a 0
    semctl(sem_id, SEM_AUTO_PASSAGGIO, SETVAL, 0); // Passaggio inizializzato a 0
    semctl(sem_id, SEM_AUTO_FINITA, SETVAL, 0);  // Auto finita inizializzato a 0
    
    // Inizializza struttura condivisa
    memset(stato_condiviso, 0, sizeof(stato_incrocio_t));
    stato_condiviso->num_auto_attive = 0;
    stato_condiviso->auto_pronte = 0;
    stato_condiviso->termine_richiesto = 0;
    stato_condiviso->prossima_auto = -1;
    
    printf("✓ Memoria condivisa e semafori inizializzati\n");
}

void cleanup_risorse(void) {
    printf("\nPulizia risorse IPC...\n");
    
    if (stato_condiviso) {
        // Scollega memoria condivisa
        if (shmdt(stato_condiviso) == -1) {
            perror("Errore nello scollegamento dalla memoria condivisa");
        }
        
        // Rimuovi memoria condivisa
        if (shmctl(shm_id, IPC_RMID, NULL) == -1) {
            perror("Errore nella rimozione della memoria condivisa");
        } else {
            printf("✓ Memoria condivisa rimossa\n");
        }
    }
    
    // Rimuovi semafori
    if (semctl(sem_id, 0, IPC_RMID) == -1) {
        perror("Errore nella rimozione dei semafori");
    } else {
        printf("✓ Semafori rimossi\n");
    }
    
    printf("✓ Pulizia completata\n");
}

void gestore_sigterm(int sig) {
    (void)sig;  // Elimina warning per parametro non usato
    printf("\nRicevuto SIGTERM. Inizio terminazione...\n");
    
    if (stato_condiviso) {
        P(sem_id, SEM_MUTEX);
        stato_condiviso->termine_richiesto = 1;
        V(sem_id, SEM_MUTEX);
        
        // Sveglia eventuali processi in attesa
        V(sem_id, SEM_AUTO_PRONTE);
        V(sem_id, SEM_AUTO_PASSAGGIO);
        V(sem_id, SEM_AUTO_FINITA);
    }
} 
