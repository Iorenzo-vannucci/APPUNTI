#include "../include/incrocio.h"

// Variabili globali
int shm_id = -1;
int sem_id = -1;
stato_incrocio_t *stato_condiviso = NULL;

int mia_strada;
int mia_destinazione;

int main(int argc, char *argv[]) {
    // Parsing degli argomenti
    if (argc != 3) {
        printf("Uso: %s <strada_origine> <strada_destinazione>\n", argv[0]);
        exit(EXIT_FAILURE);
    }
    
    mia_strada = atoi(argv[1]); //rappresentazione della strada di origine in int
    mia_destinazione = atoi(argv[2]); //rappresentazione della strada di destinazione in int
    
    printf("MACCHINA[%d] Automobile avviata: strada %d → strada %d\n", 
           mia_strada, mia_strada, mia_destinazione);
    
    
    // Connetti alla memoria condivisa esistente
    shm_id = shmget(SHM_KEY, sizeof(stato_incrocio_t), 0666);
    if (shm_id == -1) {
        perror("Automobile: errore nella connessione alla memoria condivisa");
        exit(EXIT_FAILURE);
    }
    
    stato_condiviso = (stato_incrocio_t*)shmat(shm_id, NULL, 0);
    if (stato_condiviso == (stato_incrocio_t*)-1) {
        perror("Automobile: errore nel collegamento alla memoria condivisa");
        exit(EXIT_FAILURE);
    }
    
    // Connetti ai semafori esistenti
    sem_id = semget(SEM_KEY, NUM_SEMAFORI, 0666);
    if (sem_id == -1) {
        perror("Automobile: errore nella connessione ai semafori");
        exit(EXIT_FAILURE);
    }
    
    // =================================|
    // COMPORTAMENTO DELL'AUTOMOBILE    |
    // =================================|
    
    while (1) {
        // 1. Attende che l'incrocio comunichi che può attraversare
        printf("MACCHINA[%d] In attesa di autorizzazione dall'incrocio...\n", mia_strada);
        P(sem_id, SEM_AUTO_PASSAGGIO);
        
        // Controlla se è stata richiesta la terminazione
        P(sem_id, SEM_MUTEX);
        int termine = stato_condiviso->termine_richiesto;
        int auto_autorizzata = stato_condiviso->prossima_auto;
        V(sem_id, SEM_MUTEX);
        
        if (termine) {
            printf("MACCHINA[%d] Terminazione richiesta. Uscita.\n", mia_strada);
            break;
        }
        
        // Verifica se sono io l'automobile autorizzata
        if (auto_autorizzata == mia_strada) {
            printf("MACCHINA[%d] OK Autorizzazione ricevuta! Attraverso l'incrocio\n", mia_strada);
            
            // 2. Attraversa l'incrocio
            printf("MACCHINA[%d]  Attraversando l'incrocio...\n", mia_strada);
            sleep(1);  // Simula il tempo di attraversamento
            
            // 3. Aggiunge al file auto.txt
            FILE *file_auto = fopen("auto.txt", "a");
            if (file_auto) {
                fprintf(file_auto, "%d\n", mia_strada);
                fclose(file_auto);
            }
            
            printf("MACCHINA[%d] OK Incrocio attraversato con successo!\n", mia_strada);
            
            // 4. Comunica all'incrocio che ha attraversato e termina
            V(sem_id, SEM_AUTO_FINITA);
            break;
        } else {
            // Non sono io, rimetto il semaforo a posto per l'auto giusta
            V(sem_id, SEM_AUTO_PASSAGGIO);
            usleep(10000);  // Piccola pausa per evitare busy waiting
        }
    }
    
    // ========================================================================
    // TERMINAZIONE
    // ========================================================================
    
    printf("MACCHINA[%d]  Automobile terminata\n", mia_strada);
    
    // Scollega dalla memoria condivisa
    if (shmdt(stato_condiviso) == -1) {
        perror("Automobile: errore nello scollegamento dalla memoria condivisa");
    }
    
    return EXIT_SUCCESS;
} 
