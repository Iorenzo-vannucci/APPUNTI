#define _GNU_SOURCE
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <pthread.h>

int iCondivisa = 12;

void *thread1(void *arg){
    int iLocale = 100;
    uint64_t tid;
    pthread_threadid_np(NULL, &tid);
    printf("Thread 1. PID = %d, Pthread ID = %p, macOS Thread ID = %llu\n",
           getpid(), (void *)pthread_self(), tid);
    printf("Condivisa = %d, iLocale = %d, arg = %d\n", iCondivisa, iLocale, *(int *)arg);
    //pthread_exit(NULL);
    pthread_exit((void *)2000);
}

void *thread2(void *arg){
    int iLocale = 200;
    uint64_t tid;
    pthread_threadid_np(NULL, &tid);
    printf("Thread 2. PID = %d, Pthread ID = %p, macOS Thread ID = %llu\n",
           getpid(), (void *)pthread_self(), tid);
    printf("Condivisa = %d, iLocale = %d, arg = %s\n", iCondivisa, iLocale, (char *)arg);
    //pthread_exit(NULL);
    pthread_exit((void *)2000);
}

int main(){
    pthread_t tID1, tID2;
    int arg1 = 42;
    char arg2[] = "Ciao";
    long l1, l2;

    pthread_create(&tID1, NULL, thread1, &arg1);
    pthread_create(&tID2, NULL, thread2, arg2);

    //pthread_join(tID1, NULL);
    //pthread_join(tID2, NULL);

    pthread_join(tID1, (void **)&l1);
    pthread_join(tID2, (void **)&l2);

    uint64_t tid;
    pthread_threadid_np(NULL, &tid);
    printf("Main. PID = %d, Pthread ID = %p, macOS Thread ID = %llu\n",
           getpid(), (void *)pthread_self(), tid);
    printf("Ritorno Thread1 = %ld\n, Ritorno Thread2 = %ld\n", l1, l2);

    return 0;
}