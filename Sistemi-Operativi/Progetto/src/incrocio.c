#include "../include/incrocio.h"

// Variabili globali
int shm_id = -1;
int sem_id = -1;
stato_incrocio_t *stato_condiviso = NULL;

int main(int argc, char *argv[]) {
    // Elimina warning per parametri non utilizzati
    (void)argc;
    (void)argv;
    
    printf("=== PROCESSO INCROCIO ===\n");
    printf("Avvio del processo di gestione incrocio\n");
    
    // Registra gestore per SIGTERM (come da specifiche)
    signal(SIGTERM, gestore_sigterm);
    
    // NOTA: Ctrl+C (SIGINT) non viene gestito secondo le specifiche.
    // Per test, inviare: kill -TERM <PID_incrocio>
    
    // Registra funzione di pulizia all'uscita
    atexit(cleanup_risorse);
    
    // Inizializza memoria condivisa e semafori
    inizializza_memoria_condivisa();
    
    printf("Incrocio pronto. In attesa di automobili...\n\n");
    
    // ========================================================================
    // LOOP PRINCIPALE DEL PROCESSO INCROCIO
    // ========================================================================
    
    while (1) {
        // 1. Attende che il garage gli comunichi che ci sono 4 auto
        printf("Attendo notifica dal garage...\n");
        P(sem_id, SEM_AUTO_PRONTE);
        
        // Controlla se è stata richiesta la terminazione
        P(sem_id, SEM_MUTEX);
        if (stato_condiviso->termine_richiesto) {
            V(sem_id, SEM_MUTEX);
            printf("Terminazione richiesta. Uscita dal loop principale.\n");
            break;
        }
        V(sem_id, SEM_MUTEX);
        
        printf(" Ricevuta notifica: 4 automobili da far passare!\n");
        
        // 2-7. Determina quale auto può attraversare e la fa passare (4 volte)
        int direzioni[NUM_AUTO];
        int auto_attraversate = 0;
        
        // Leggi le direzioni delle automobili
        P(sem_id, SEM_MUTEX);
        for (int i = 0; i < NUM_AUTO; i++) {
            direzioni[i] = stato_condiviso->automobili[i].strada_destinazione;
        }
        V(sem_id, SEM_MUTEX);
        
        // Fai attraversare tutte e 4 le auto
        while (auto_attraversate < NUM_AUTO) {
            // 2. Determina quale auto può attraversare
            int auto_scelta = GetNextCar(direzioni);
            
            if (auto_scelta == -1) {
                printf("Errore: nessuna auto da far passare!\n");
                break;
            }
            
            P(sem_id, SEM_MUTEX);
            int strada_origine = stato_condiviso->automobili[auto_scelta].strada_origine;
            int strada_destinazione = stato_condiviso->automobili[auto_scelta].strada_destinazione;
            V(sem_id, SEM_MUTEX);
            
            // 3. Aggiunge al file incrocio.txt
            FILE *file_incrocio = fopen("incrocio.txt", "a");
            if (file_incrocio) {
                fprintf(file_incrocio, "%d\n", strada_origine);
                fclose(file_incrocio);
            }
            
            // 4. Emette messaggio a video
            printf(" Auto scelta: strada %d → strada %d\n", 
                   strada_origine, strada_destinazione);
            
            // 5. Comunica all'auto che può attraversare
            P(sem_id, SEM_MUTEX);
            stato_condiviso->prossima_auto = auto_scelta;
            V(sem_id, SEM_MUTEX);
            
            V(sem_id, SEM_AUTO_PASSAGGIO);  // Sblocca l'auto scelta
            
            // 6. Attende che l'auto attraversi
            P(sem_id, SEM_AUTO_FINITA);
            
            // Marca l'auto come già passata
            direzioni[auto_scelta] = -1;
            auto_attraversate++;
            
            printf("Auto %d ha attraversato l'incrocio (%d/4)\n", 
                   auto_scelta, auto_attraversate);
        }
        
        printf("Tutte e 4 le automobili hanno attraversato!\n\n");
        
        // Reset per il prossimo gruppo di auto
        P(sem_id, SEM_MUTEX);
        stato_condiviso->auto_pronte = 0;
        stato_condiviso->prossima_auto = -1;
        V(sem_id, SEM_MUTEX);
    }
    
    // ========================================================================
    // TERMINAZIONE CONTROLLATA
    // ========================================================================
    
    printf("\n Inizio procedura di terminazione...\n");
    
    // Informa tutti gli altri processi che devono terminare
    P(sem_id, SEM_MUTEX);
    stato_condiviso->termine_richiesto = 1;
    V(sem_id, SEM_MUTEX);
    
    // Sblocca eventuali processi in attesa
    V(sem_id, SEM_AUTO_PRONTE);
    V(sem_id, SEM_AUTO_PASSAGGIO);
    V(sem_id, SEM_AUTO_FINITA);
    
    // Attende la terminazione di tutti gli altri processi
    printf("Attendo terminazione di tutti gli altri processi...\n");
    
    int processi_attivi;
    do {
        sleep(1);
        P(sem_id, SEM_MUTEX);
        processi_attivi = stato_condiviso->num_auto_attive;
        V(sem_id, SEM_MUTEX);
        
        if (processi_attivi > 0) {
            printf("   Processi ancora attivi: %d\n", processi_attivi);
        }
    } while (processi_attivi > 0);
    
    printf("Tutti i processi sono terminati\n");
    printf("Processo incrocio termina per ultimo\n");
    
    return EXIT_SUCCESS;
} 
