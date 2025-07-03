// automobile.c
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <semaphore.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <string.h>
#include <stdio.h>
#include "../condiviso.h"
#include "../incrocio.h"

int main(int argc, char *argv[]) {
    if (argc != 3) {
        const char *msg = "Usage: automobile <from> <to>\n";
        write(STDERR_FILENO, msg, strlen(msg));
        _exit(EXIT_FAILURE);
    }

    //parsing degli argomenti 
    int from = atoi(argv[1]);
    

    //Apertura semafori named
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

    //Attesa via semaforo del via libera dall'incrocio
    sem_wait(sem_auto);

    //Attraversamento (simulato)
    //sleep(1);

    //Log ATOMICO su entrambi i file auto.txt E incrocio.txt */
    sem_wait(sem_file_write);
    
    char buf1[16];
    int len1 = snprintf(buf1, sizeof(buf1), "%d\n", from);
    
    //Apre entrambi i file contemporaneamente
    int fd1 = open("log/auto.txt", O_CREAT | O_APPEND | O_WRONLY, 0666);
    int fd2 = open("log/incrocio.txt", O_CREAT | O_APPEND | O_WRONLY, 0666);
    
    if (fd1 == -1 || fd2 == -1) {
        perror("open log files");
        if (fd1 >= 0) close(fd1);
        if (fd2 >= 0) close(fd2);
        sem_post(sem_file_write);
        exit(EXIT_FAILURE);
    }
    
    //Scrive in entrambi i file prima di chiuderli
    if (write(fd1, buf1, len1) == -1) {
        perror("write log/auto.txt");
        close(fd1);
        close(fd2);
        sem_post(sem_file_write);
        exit(EXIT_FAILURE);
    }
    
    if (write(fd2, buf1, len1) == -1) {
        perror("write log/incrocio.txt");
        close(fd1);
        close(fd2);
        sem_post(sem_file_write);
        exit(EXIT_FAILURE);
    }
    
    //Chiude entrambi i file
    close(fd1);
    close(fd2);
    
    sem_post(sem_file_write);

    // Notifica all'incrocio del completamento
    
    sem_post(sem_done);
    

    //Termina processo
    _exit(EXIT_SUCCESS);
}