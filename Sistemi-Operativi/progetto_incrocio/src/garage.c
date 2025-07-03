#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <string.h>
#include <semaphore.h>
#include "../condiviso.h"


int main() {
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

    //Loop infinito: genera sempre gruppi da 4 auto 
    while (1) {
        for (int i = 0; i < MAX_AUTO; ++i) {
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
                printf("Garage: creata auto %d (PID %d) da %d verso %d\n",
                       i, pid, i, dest);
                fflush(stdout);
            }
        }

        //Segnala a incrocio che le 4 auto sono pronte
        sem_post(sem_garage);

        //Attende che tutte le auto terminated (sincronizzazione grossolana) 
        for (int i = 0; i < MAX_AUTO; ++i) {
            int status;
            if (waitpid(-1, &status, 0) < 0) {
                perror("waitpid");
            }
        }

        //Pausa di respiro prima di ricominciare 
        sleep(1);
    }

    return 0;  
}