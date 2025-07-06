#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <semaphore.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <string.h>
#include <signal.h>
#include "../condiviso.h"
#include "../incrocio.h"


// Variabile globale per controllare la terminazione del programma
volatile int keep_running = 1;
shared_data_t *global_shm = NULL;

void signal_handler(int sig) {
    switch (sig) {
        case SIGINT:
            // Ignora SIGINT (CTRL+C)
            printf("\n\x1b[36mIncrocio:\x1b[37;1m \x1b[33;1mricevuto SIGINT (CTRL+C) - ignorato. Usa 'kill -SIGTERM %d' per terminare.\x1b[37;1m\n", getpid());
            fflush(stdout);
            break;
        case SIGTERM:
            // Termina il programma pulitamente
            printf("\n\x1b[36mIncrocio:\x1b[37;1m \x1b[32;1mricevuto SIGTERM - impostando flag di terminazione...\x1b[37;1m\n");
            fflush(stdout);
            keep_running = 0;
            // Imposta il flag di terminazione nella memoria condivisa
            if (global_shm != NULL) {
                global_shm->terminate_flag = 1;
            }
            break;
        case SIGQUIT:
            // Ignora SIGQUIT (CTRL+\\)
            printf("\n\x1b[36mIncrocio:\x1b[37;1m \x1b[33;1mricevuto SIGQUIT (CTRL+\\) - ignorato. Usa 'kill -SIGTERM %d' per terminare.\x1b[37;1m\n", getpid());
            fflush(stdout);
            break;
        default:
            // Altri segnali: continua l'esecuzione
            break;
    }
}

//Configura la gestione dei segnali per il processo incrocio.
void setup_signal_handling() {
    struct sigaction sa;
    
    // Configura il gestore per SIGINT e SIGTERM
    sa.sa_handler = signal_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    
    // Installa il gestore per SIGINT (CTRL+C)
    if (sigaction(SIGINT, &sa, NULL) == -1) {
        perror("sigaction SIGINT");
        exit(EXIT_FAILURE);
    }
    
    // Installa il gestore per SIGTERM
    if (sigaction(SIGTERM, &sa, NULL) == -1) {
        perror("sigaction SIGTERM");
        exit(EXIT_FAILURE);
    }
    // Installa il gestore per SIGQUIT (CTRL+\\)
    if (sigaction(SIGQUIT, &sa, NULL) == -1) {
        perror("sigaction SIGQUIT");
        exit(EXIT_FAILURE);
    }
    
    printf("Incrocio: configurazione segnali completata (PID: %d)\n", getpid());
    printf("-\x1b[34;1m SIGINT (CTRL+C) verrà ignorato\x1b[37m\n");
    printf("-\x1b[34;1m SIGQUIT (CTRL+\\) verrà ignorato\x1b[37m\n");
    printf("-\x1b[34;1m SIGTERM terminerà il programma\x1b[37m \x1b[37m \n");
    fflush(stdout);
}

//Pulisce le risorse prima della terminazione del programma.
void cleanup_resources(shared_data_t *shm, sem_t *sem_garage, sem_t *sem_done, sem_t **sem_auto) {
    printf("\x1b[33;1mIncrocio: pulizia risorse in corso...\x1b[37m\n");
    fflush(stdout);
    
    // Unmappa la memoria condivisa
    if (shm != MAP_FAILED) {
        munmap(shm, sizeof(shared_data_t));
    }
    
    // Chiudi i semafori (senza rimuoverli - sarà compito del garage)
    if (sem_garage != SEM_FAILED) sem_close(sem_garage);
    if (sem_done != SEM_FAILED) sem_close(sem_done);
    
    for (int i = 0; i < MAX_AUTO; ++i) {
        if (sem_auto[i] != SEM_FAILED) {
            sem_close(sem_auto[i]);
        }
    }
    
    printf("\x1b[32;1mIncrocio: terminazione completata.\x1b[37m\n");
    fflush(stdout);
}

int main() {
    // Setup della gestione dei segnali
    setup_signal_handling();
    
    /* 1. Apertura e mappatura shared memory */
    int shm_fd = shm_open(SHM_NAME, O_RDWR, 0666);
    if (shm_fd < 0) {
        perror("shm_open"); 
        exit(EXIT_FAILURE);
    }
    shared_data_t *shm = mmap(
        NULL, sizeof(shared_data_t),
        PROT_READ | PROT_WRITE,    // permessi di lettura e scrittura  
        MAP_SHARED,                // mapping condiviso
        shm_fd, 0
    );
    if (shm == MAP_FAILED) {
        perror("mmap");
        exit(EXIT_FAILURE);
    }
    
    global_shm = shm;  // Salva riferimento globale per signal handler

    /* 2. Apertura semafori named */
    sem_t *sem_garage = sem_open(SEM_GARAGE, 0);    // aperto da garage con valore iniziale 0  
    sem_t *sem_done   = sem_open(SEM_DONE,   0);    // idem  

    sem_t *sem_auto[MAX_AUTO];
    char namebuf[32];
    for (int i = 0; i < MAX_AUTO; ++i) {
        snprintf(namebuf, sizeof(namebuf), SEM_AUTO_FMT, i);
        sem_auto[i] = sem_open(namebuf, 0);         // creati nel garage  
        if (sem_auto[i] == SEM_FAILED) {
            perror("sem_open auto");
            exit(EXIT_FAILURE);
        }
    }

    //Loop principale di attraversamento
    while (keep_running && !shm->terminate_flag) {
        //3.1 Attesa passiva del garage 
        if (sem_wait(sem_garage) == -1) {
            // Se sem_wait viene interrotta da un segnale, controlla se dobbiamo fermarci
            if (!keep_running || shm->terminate_flag) break;
            continue; // Riprova se è stato un altro segnale
        }

        // Controlla ancora il flag dopo aver ricevuto il segnale dal garage
        if (!keep_running || shm->terminate_flag) break;

        //Scelta e attraversamento di ciascuna delle 4 auto
        //Costruzione array delle destinazioni (DENTRO il loop while) 
        int direzioni[MAX_AUTO];
        for (int i = 0; i < MAX_AUTO; ++i) {
            direzioni[i] = shm->cars[i].to;
        }

        for (int pass = 0; pass < MAX_AUTO && keep_running && !shm->terminate_flag; ++pass) {

            //GetNextCar individua l'indice k in base al codice della strada 
            int k = GetNextCar(direzioni);           // fornita in incrocio.h 
            
            //Verifica di sicurezza: se nessuna auto disponibile, esci 
            if (k == -1) {
                printf("ERRORE: GetNextCar ha restituito -1, nessuna auto disponibile!\n");
                fflush(stdout);
                break;
            }
            
            //Marca questa auto come già attraversata 
            direzioni[k] = -1;
            
            //Log dell'attraversamento 
            printf("\x1b[36mIncrocio:\x1b[39m auto %d da %d verso %d può attraversare\x1b[39m\n",
                   k, shm->cars[k].from, shm->cars[k].to);
            fflush(stdout);

            //Notifica all'automobile k 
            sem_post(sem_auto[k]);                  

            //Attesa che l'auto segnali il passaggio 
            if (sem_wait(sem_done) == -1) {
                // Se sem_wait viene interrotta da un segnale, controlla se dobbiamo fermarci
                if (!keep_running || shm->terminate_flag) break;
                // Altrimenti continua (riprova)
            }              
        }
    }

    // Cleanup delle risorse prima della terminazione
    cleanup_resources(shm, sem_garage, sem_done, sem_auto);
    
    return 0;
}