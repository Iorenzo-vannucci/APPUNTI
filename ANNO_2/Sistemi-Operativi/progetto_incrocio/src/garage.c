#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <string.h>
#include <semaphore.h>
#include <signal.h>
#include "../incrocio.h"

// Variabili globali per la gestione della terminazione
volatile int keep_running = 1;
shared_data_t *global_shm = NULL;

void signal_handler(int sig) {
    switch (sig) {
        case SIGINT:
            printf("\n\x1b[35;1mGarage:\x1b[37;1m \x1b[33;1mricevuto SIGINT (CTRL+C) - ignorato.\n");
            fflush(stdout);
            break;
        case SIGTERM:
            printf("\n\x1b[35;1mGarage:\x1b[37;1m \x1b[33;1mricevuto SIGTERM - ignorato.\n" );
            fflush(stdout);
            break;
        case SIGQUIT:
            printf("\n\x1b[35;1mGarage:\x1b[37;1m \x1b[33;1mricevuto SIGQUIT (CTRL+\\) - ignorato.\n");
            fflush(stdout);
            break;
        default:
            break;
    }
}

void setup_signal_handling() {
    struct sigaction sa;
    
    sa.sa_handler = signal_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    
    if (sigaction(SIGINT, &sa, NULL) == -1) {
        perror("sigaction SIGINT");
        exit(EXIT_FAILURE);
    }
    
    if (sigaction(SIGTERM, &sa, NULL) == -1) {
        perror("sigaction SIGTERM");
        exit(EXIT_FAILURE);
    }
    
    if (sigaction(SIGQUIT, &sa, NULL) == -1) {
        perror("sigaction SIGQUIT");
        exit(EXIT_FAILURE);
    }
    
    printf("Garage: configurazione segnali completata (PID: %d)\n", getpid());
    printf("-\x1b[34;1m SIGINT (CTRL+C) verrà ignorato\x1b[37m\n");
    printf("-\x1b[34;1m SIGQUIT (CTRL+\\) verrà ignorato\x1b[37m\n");
    printf("-\x1b[34;1m SIGTERM terminerà il programma\x1b[37m \x1b[37m \n");
    fflush(stdout);
}

void cleanup_resources(shared_data_t *shm, sem_t *sem_garage, sem_t *sem_done, sem_t *sem_file_write, sem_t **sem_auto_arr) {
    printf("\x1b[33;1mGarage: pulizia risorse in corso...\x1b[37m\n");
    fflush(stdout);
    
    // Termina tutti i processi figli rimanenti
    printf("\x1b[33;1mGarage: terminazione processi auto rimanenti...\x1b[37m\n");
    int status;
    pid_t child_pid;
    while ((child_pid = waitpid(-1, &status, WNOHANG)) > 0) {
        printf("\x1b[32;1mGarage: processo figlio %d terminato\x1b[0m\n", child_pid);
    }
    
    // Chiudi e rimuovi semafori
    if (sem_garage != SEM_FAILED) {
        sem_close(sem_garage);
        sem_unlink(SEM_GARAGE);
    }
    if (sem_done != SEM_FAILED) {
        sem_close(sem_done);
        sem_unlink(SEM_DONE);
    }
    if (sem_file_write != SEM_FAILED) {
        sem_close(sem_file_write);
        sem_unlink(SEM_FILE_WRITE);
    }
    
    char sem_name[32];
    for (int i = 0; i < MAX_AUTO; ++i) {
        if (sem_auto_arr[i] != SEM_FAILED) {
            sem_close(sem_auto_arr[i]);
            snprintf(sem_name, sizeof(sem_name), SEM_AUTO_FMT, i);
            sem_unlink(sem_name);
        }
    }
    
    // Unmappa e rimuovi memoria condivisa
    if (shm != MAP_FAILED) {
        munmap(shm, sizeof(shared_data_t));
    }
    shm_unlink(SHM_NAME);
    
    printf("\x1b[32;1mGarage: terminazione completata.\x1b[37;1m\n");
    fflush(stdout);
}

int main() {
    // Setup della gestione dei segnali
    setup_signal_handling();
    
    //Rimuove eventuale shared memory residua da run precedenti 
    shm_unlink(SHM_NAME);

    //Creazione e mappatura della shared memory 
    int shm_fd = shm_open(SHM_NAME, O_CREAT | O_RDWR, 0666);
    if (shm_fd < 0) {
        perror("shm_open");
        exit(EXIT_FAILURE);
    }
    if (ftruncate(shm_fd, sizeof(shared_data_t)) < 0) {
        perror("ftruncate");
        exit(EXIT_FAILURE);
    }
    shared_data_t *shm = mmap(NULL, sizeof(shared_data_t),
                              PROT_READ | PROT_WRITE, MAP_SHARED,
                              shm_fd, 0);
    if (shm == MAP_FAILED) {
        perror("mmap");
        exit(EXIT_FAILURE);
    }
    
    // Inizializza il flag di terminazione
    shm->terminate_flag = 0;
    global_shm = shm;  // Salva riferimento globale per signal handler

    //Creazione / apertura dei semafori principali 
    sem_t *sem_garage = sem_open(SEM_GARAGE, O_CREAT, 0666, 0);
    sem_t *sem_done   = sem_open(SEM_DONE,   O_CREAT, 0666, 0);
    sem_t *sem_file_write = sem_open(SEM_FILE_WRITE, O_CREAT, 0666, 1); // mutex inizializzato a 1
    if (sem_garage == SEM_FAILED || sem_done == SEM_FAILED || sem_file_write == SEM_FAILED) {
        perror("sem_open garage/done/file_write");
        exit(EXIT_FAILURE);
    }

    //Creazione dei semafori per ciascuna automobile 
    sem_t *sem_auto_arr[MAX_AUTO];
    char sem_name[32];
    for (int i = 0; i < MAX_AUTO; ++i) {
        snprintf(sem_name, sizeof(sem_name), SEM_AUTO_FMT, i);
        sem_auto_arr[i] = sem_open(sem_name, O_CREAT, 0666, 0);
        if (sem_auto_arr[i] == SEM_FAILED) {
            perror("sem_open sem_auto");
            exit(EXIT_FAILURE);
        }
    }

    //Loop principale: genera sempre gruppi da 4 auto fino a quando non viene richiesta la terminazione
    while (keep_running && !shm->terminate_flag) {
        for (int i = 0; i < MAX_AUTO && keep_running && !shm->terminate_flag; ++i) {
            int dest = EstraiDirezione(i);      //destino scelto UNA volta 
            pid_t pid = fork();
            if (pid < 0) {
                perror("fork");
                exit(EXIT_FAILURE);
            }

            if (pid == 0) {
                //=== FIGLIO: diventa processo automobile === 
                char arg_from[4], arg_to[4];
                snprintf(arg_from, sizeof(arg_from), "%d", i);
                snprintf(arg_to,   sizeof(arg_to),   "%d", dest);
                execl("./build/automobile", "automobile", arg_from, arg_to, NULL);
                //Se execl fallisce: 
                perror("execl");
                _exit(EXIT_FAILURE);
            } else {
                //=== PADRE (garage): registra l'auto in shared memory === 
                shm->cars[i].pid  = pid;
                shm->cars[i].from = i;
                shm->cars[i].to   = dest;
                printf("\x1b[35mGarage:\x1b[39m creata auto %d (PID %d) da %d verso %d\n",
                       i, pid, i, dest);
                fflush(stdout);
            }
        }

        // Se dobbiamo terminare, non segnalare all'incrocio
        if (!keep_running || shm->terminate_flag) {
            break;
        }

        //Segnala a incrocio che le 4 auto sono pronte
        sem_post(sem_garage);

        //Attende che tutte le auto terminate (sincronizzazione grossolana) 
        for (int i = 0; i < MAX_AUTO; ++i) {
            int status;
            if (waitpid(-1, &status, 0) < 0) {
                perror("waitpid");
            }
        }

        // Attesa prima di generare il prossimo gruppo di auto
        sleep(1);
    }

    // Cleanup delle risorse prima della terminazione
    cleanup_resources(shm, sem_garage, sem_done, sem_file_write, sem_auto_arr);

    return 0;  
}