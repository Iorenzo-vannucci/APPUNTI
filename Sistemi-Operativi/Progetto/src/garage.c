#include "../include/incrocio.h"

// Variabili globali
int shm_id = -1;
int sem_id = -1;
stato_incrocio_t *stato_condiviso = NULL;

int main(int argc, char *argv[]) {
    // Elimina warning per parametri non utilizzati
    (void)argc;
    (void)argv;
    
    printf("=== PROCESSO GARAGE ===\n");
    printf("Avvio del processo generatore di automobili\n");
    
    // Il garage NON gestisce segnali direttamente
    // Solo l'incrocio gestisce SIGTERM secondo le specifiche
    
    // Connetti alla memoria condivisa esistente (creata dall'incrocio)
    shm_id = shmget(SHM_KEY, sizeof(stato_incrocio_t), 0666);
    if (shm_id == -1) {
        printf(" Errore: impossibile connettersi alla memoria condivisa\n");
        printf("   Assicurati che il processo 'incrocio' sia già avviato\n");
        exit(EXIT_FAILURE);
    }
    
    stato_condiviso = (stato_incrocio_t*)shmat(shm_id, NULL, 0);
    if (stato_condiviso == (stato_incrocio_t*)-1) {
        perror("Errore nel collegamento alla memoria condivisa");
        exit(EXIT_FAILURE);
    }
    
    // Connetti ai semafori esistenti
    sem_id = semget(SEM_KEY, NUM_SEMAFORI, 0666);
    if (sem_id == -1) {
        perror("Errore nella connessione ai semafori");
        exit(EXIT_FAILURE);
    }
    
    printf(" Connesso alla memoria condivisa e ai semafori\n");
    printf(" Garage operativo. Inizio generazione automobili...\n\n");
    
    // ========================================================================
    // LOOP PRINCIPALE DEL PROCESSO GARAGE
    // ========================================================================
    
    int ciclo = 1;
    
    while (1) {
        // Controlla se è stata richiesta la terminazione
        P(sem_id, SEM_MUTEX);
        int termine = stato_condiviso->termine_richiesto;
        V(sem_id, SEM_MUTEX);
        
        if (termine) {
            printf(" Terminazione richiesta. Uscita dal garage.\n");
            break;
        }
        
        printf(" Ciclo %d: Creazione di 4 automobili\n", ciclo);
        
        // 1. Crea 4 processi automobile, uno per ogni strada
        pid_t pids[NUM_AUTO];
        
        for (int i = 0; i < NUM_AUTO; i++) {
            // Estrae direzione casuale diversa dalla strada di origine
            int destinazione = EstraiDirezione(i);
            
            // 2. Emette messaggio a video
            printf(" Creata automobile %d: strada %d → strada %d\n", 
                   i, i, destinazione);
            
            // Registra l'automobile nella memoria condivisa
            P(sem_id, SEM_MUTEX);
            stato_condiviso->automobili[i].strada_origine = i;
            stato_condiviso->automobili[i].strada_destinazione = destinazione;
            stato_condiviso->automobili[i].attiva = 1;
            stato_condiviso->num_auto_attive++;
            V(sem_id, SEM_MUTEX);
            
            // Crea processo automobile con fork()
            pids[i] = fork();
            
            if (pids[i] == -1) {
                perror("Errore nella creazione del processo automobile");
                exit(EXIT_FAILURE);
            }
            
            if (pids[i] == 0) {
                // *** PROCESSO FIGLIO (AUTOMOBILE) ***
                
                // Converte parametri in stringhe per execl
                char strada_str[10];
                char destinazione_str[10];
                
                snprintf(strada_str, sizeof(strada_str), "%d", i);
                snprintf(destinazione_str, sizeof(destinazione_str), "%d", destinazione);
                
                // Esegue il programma automobile
                execl("./build/bin/automobile", "automobile", 
                      strada_str, destinazione_str, NULL);
                
                // Se execl fallisce
                perror("Errore nell'esecuzione del processo automobile");
                exit(EXIT_FAILURE);
            }
            
            // *** PROCESSO PADRE (GARAGE) ***
            // Registra il PID dell'automobile
            P(sem_id, SEM_MUTEX);
            stato_condiviso->automobili[i].pid = pids[i];
            V(sem_id, SEM_MUTEX);
        }
        
        // 3. Notifica all'incrocio che ci sono 4 auto da far passare
        P(sem_id, SEM_MUTEX);
        stato_condiviso->auto_pronte = 1;
        V(sem_id, SEM_MUTEX);
        
        printf(" Notifica inviata all'incrocio: 4 auto pronte!\n");
        V(sem_id, SEM_AUTO_PRONTE);  // Sblocca l'incrocio
        
        // 4. Rimane in attesa che tutte le automobili abbiano attraversato
        printf(" Attendo che tutte le automobili attraversino...\n");
        
        for (int i = 0; i < NUM_AUTO; i++) {
            int status;
            waitpid(pids[i], &status, 0);  // Attesa bloccante
            
            printf(" Processo automobile %d terminato\n", i);
            
            // Aggiorna il contatore
            P(sem_id, SEM_MUTEX);
            stato_condiviso->num_auto_attive--;
            V(sem_id, SEM_MUTEX);
        }
        
        printf(" Tutte le automobili del ciclo %d hanno terminato!\n", ciclo);
        
        // 5. Attende 1 secondo
        printf("Pausa di 1 secondo...\n\n");
        sleep(1);
        
        ciclo++;
        
        // 6. Riprende dal punto 1
    }
    
    // ========================================================================
    // TERMINAZIONE
    // ========================================================================
    
    printf(" Processo garage terminato\n");
    
    // Scollega dalla memoria condivisa
    if (shmdt(stato_condiviso) == -1) {
        perror("Errore nello scollegamento dalla memoria condivisa");
    }
    
    return EXIT_SUCCESS;
} 
