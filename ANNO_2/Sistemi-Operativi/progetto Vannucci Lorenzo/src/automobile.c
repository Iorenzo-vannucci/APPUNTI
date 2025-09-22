#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <semaphore.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <string.h>
#include <stdio.h>
#include "../incrocio.h"

// Funzione principale del processo automobile
int main(int argc, char *argv[]) {
    // Controlla se il numero di argomenti è corretto
    if (argc != 3) {
        // Messaggio di errore per uso scorretto
        const char *msg = "Usage: automobile <from> <to>\n";
        write(STDERR_FILENO, msg, strlen(msg));
        _exit(EXIT_FAILURE);
    }

    // Parsing degli argomenti
    int from = atoi(argv[1]);
    
    // Apertura semafori
    char sem_name[32];
    snprintf(sem_name, sizeof(sem_name), SEM_AUTO_FMT, from);
    sem_t *sem_auto = sem_open(sem_name, 0);
    if (sem_auto == SEM_FAILED) {
        perror("sem_open sem_auto");
        _exit(EXIT_FAILURE);
    }
    sem_t *sem_done = sem_open(SEM_DONE, 0);
    if (sem_done == SEM_FAILED) {
        perror("sem_open sem_done");
        _exit(EXIT_FAILURE);
    }
    sem_t *sem_file_write = sem_open(SEM_FILE_WRITE, 0);
    if (sem_file_write == SEM_FAILED) {
        perror("sem_open sem_file_write");
        _exit(EXIT_FAILURE);
    }

    // Attesa via semaforo del via libera dall'incrocio
    sem_wait(sem_auto);

        // Attesa per accesso esclusivo ai file di log
    sem_wait(sem_file_write);
    
    // Buffer per scrittura nei file di log
    char buf1[16];
    int len1 = snprintf(buf1, sizeof(buf1), "%d\n", from);
    
    // Apre il file per il log dell'automobile
    int fd1 = open("log/auto.txt", O_CREAT | O_APPEND | O_WRONLY, 0666);
    
    // Controlla se l'apertura del file è fallita
    if (fd1 == -1) {
        perror("open log/auto.txt");
        sem_post(sem_file_write);
        exit(EXIT_FAILURE);
    }
    
    // Scrive nel file prima di chiuderlo
    if (write(fd1, buf1, len1) == -1) {
        perror("write log/auto.txt");
        close(fd1);
        sem_post(sem_file_write);
        exit(EXIT_FAILURE);
    }
    
    close(fd1);
    
    // Rilascia il semaforo per l'accesso ai file
    sem_post(sem_file_write);

    // Notifica all'incrocio del completamento
    sem_post(sem_done);
    
    // Termina processo
    _exit(EXIT_SUCCESS);
}