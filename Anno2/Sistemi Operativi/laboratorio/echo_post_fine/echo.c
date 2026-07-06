#include <unistd.h>
#include <stdio.h>
#include <sys/wait.h>

int main() {
    pid_t pid = fork(); // Crea processo figlio
    
    if (pid < 0) { 
        fprintf(stderr, "Fork fallito");
        return 1;
    } else if (pid == 0) { // Codice figlio
        execlp("echo", "echo", "Ciao", NULL); // Sostituisce il codice con echo
    } else { // Codice genitore
        wait(NULL); // Attende la terminazione del figlio
        printf("Figlio completato.\n");
    }
    return 0;
}