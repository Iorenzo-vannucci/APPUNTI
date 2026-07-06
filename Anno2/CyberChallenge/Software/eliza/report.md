# Analisi del Crackme "Eliza"

## Panoramica della Challenge

La challenge "Eliza" presenta un chatbot che interagisce con l'utente. Il server è accessibile tramite netcat all'indirizzo `eliza.challs.cyberchallenge.it` sulla porta `9131`. Secondo la descrizione, Eliza può discutere liberamente di qualsiasi argomento, con l'unica limitazione che le frasi non possono superare i 16 caratteri.

L'obiettivo della challenge è convincere il chatbot a rivelare la flag.

## Analisi della Vulnerabilità

### Struttura del Programma

Dall'analisi del codice in Ghidra, abbiamo identificato tre funzioni principali:
- `main`: Inizializza il programma e chiama la funzione `eliza`
- `eliza`: Gestisce l'interazione con l'utente, riceve input e fornisce risposte
- `spawn_shell`: Una funzione nascosta che esegue `/bin/bash` quando chiamata

### Buffer Overflow nella funzione `eliza`

Una vulnerabilità critica è stata identificata nella funzione `eliza`. Il codice alloca un buffer di 72 byte (`input_buffer`) ma tenta di leggere fino a 256 byte (0x100) dall'input dell'utente:

```c
memset(input_buffer, 0, 0x40);
local_60 = read(0, input_buffer, 0x100);  // Legge fino a 256 byte in un buffer di 72 byte
```

Questa discrepanza crea una vulnerabilità di buffer overflow. Inserendo più di 72 caratteri, è teoricamente possibile sovrascrivere variabili nello stack, incluso il canary di protezione (`local_10`) e l'indirizzo di ritorno.

### Controlli di Sicurezza e Limitazioni

Il programma implementa diverse protezioni:
1. **Stack Canary**: Un valore di controllo che verifica se lo stack è stato corrotto
2. **Controllo della lunghezza**: Verifica se l'input dell'utente supera i 16 caratteri

```c
sVar2 = strlen(input_buffer);
if (sVar2 < 0x11) {  // Se l'input è minore di 17 caratteri
  // Risposta normale
} else {
  // Messaggio di errore
}
```

## Tentativi di Exploit

### Approccio 1: Buffer Overflow

Il nostro primo approccio è stato tentare un buffer overflow per sovrascrivere l'indirizzo di ritorno con la funzione `spawn_shell`. La strategia era:

1. Creare un input di 72 bytes per riempire `input_buffer`
2. Aggiungere 8 bytes per sovrascrivere `local_60`
3. Aggiungere 8 bytes del canary (determinato essere tutti zeri)
4. Aggiungere 8 bytes per sovrascrivere il saved RBP
5. Aggiungere l'indirizzo di `spawn_shell` (0x00400897) come indirizzo di ritorno

Per bypassare il controllo della lunghezza, abbiamo inserito un carattere null dopo i primi 16 caratteri, così strlen() restituisce una lunghezza di 16 caratteri anche se il payload è più lungo.

Questo approccio non ha avuto successo sul server remoto. Nonostante il canary fosse stato determinato correttamente (tutti zeri), il server ha continuato a rispondere come il chatbot Eliza senza attivare la shell.

### Approccio 2: Interazione Diretta con il Chatbot

Considerando il testo della challenge, che richiede di "convincere il bot a rivelare la flag", abbiamo cambiato strategia. Abbiamo provato diverse categorie di input:

1. **Parole chiave relative alla flag**: "flag", "show flag", "give me flag", "password", "secret", ecc.
2. **Input di lunghezze variabili**: Test con input di diverse lunghezze vicine al limite di 16 caratteri
3. **Payload speciali**: Format string, command injection, nomi di file comuni per flag
4. **Parole chiave contestuali**: Parole legate a ELIZA, al suo creatore, e al contesto della challenge

## Osservazioni Chiave

1. Il chatbot risponde con una serie di frasi predefinite selezionate casualmente
2. Due risposte fanno riferimento a "cookie" e "canary", suggerendo una possibile connessione con la vulnerabilità
3. Il controllo della lunghezza è applicato dopo che i dati sono stati scritti nel buffer, ma prima che venga data una risposta

## Conclusione

La challenge "Eliza" combina elementi di ingegneria sociale (convincere il chatbot) con potenziali vulnerabilità tecniche (buffer overflow). La soluzione potrebbe richiedere:

1. Trovare la parola chiave o frase esatta che attiva la risposta con la flag
2. Sfruttare la vulnerabilità di buffer overflow in un modo specifico che non siamo ancora riusciti a identificare
3. Una combinazione di entrambi gli approcci

I tentativi finora non hanno portato alla flag, ma l'analisi ha rivelato aspetti interessanti della challenge che potrebbero essere utili per ulteriori tentativi.
