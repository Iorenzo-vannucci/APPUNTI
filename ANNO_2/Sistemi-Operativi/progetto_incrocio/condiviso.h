#include <semaphore.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>

#define SHM_NAME       "/incrocio_shm"
#define SEM_GARAGE     "/sem_garage"      // garage → incrocio
#define SEM_DONE       "/sem_done"        // auto → incrocio
#define SEM_AUTO_FMT   "/sem_auto_%d"     // incrocio → auto i
#define SEM_FILE_WRITE "/sem_file_write"  // mutex per scrittura file
#define MAX_AUTO       4

typedef struct {
    pid_t  pid;   // PID del processo automobile
    int    from;  // strada di provenienza (0–3)
    int    to;    // strada di destinazione (0–3)
} car_t;

typedef struct {
    car_t cars[MAX_AUTO];
    volatile int terminate_flag;  // Flag per terminazione coordinata dei processi
} shared_data_t;

/*
    GetDistanceFromStreet
    ---------------------
    Calcola la distanza tra una strada di origine e una direzione di destinazione.
    Funzione helper per calcoli di precedenza.
 
    iStreet: strada di origine (0-3)
    iDirezione: direzione di destinazione (0-3)
    Ritorna: distanza calcolata
 */
int GetDistanceFromStreet(int iStreet, int iDirezione);

/*
    StreetOnTheLeft
    ---------------
    Calcola la strada che si trova a sinistra di una data strada a una certa distanza.
    Funzione helper per logica delle precedenze.
   
    iMyStrada: strada di riferimento (0-3)
    iDistance: distanza (1-3: 1=destra, 2=fronte, 3=sinistra)
     Ritorna: indice della strada risultante (0-3)
 */
int StreetOnTheLeft(int iMyStrada, int iDistance);

/*
    EstraiDirezione
    ---------------
    Estrae "a sorte" (pseudo-casualmente) una strada di destinazione
    diversa da quella di provenienza.
  
    iMyStreet: indice (0–3) della strada di provenienza
    Ritorna: indice (0–3) della strada di destinazione, garantito diverso da iMyStreet
 */
int EstraiDirezione(int iMyStreet);

/*
    GetNextCar
    ----------
    Determina quale automobile può attraversare l'incrocio, 
    secondo le regole di precedenza del codice della strada.
  
    piDirezioni: array di 4 interi, ciascuno è la direzione (0–3) che ogni 
            automobile intende prendere, o -1 se nessuna auto da quella strada
    Ritorna: indice (0–3) dell'automobile avente priorità, o -1 se nessuna auto può passare
 */
int GetNextCar(int *piDirezioni);

