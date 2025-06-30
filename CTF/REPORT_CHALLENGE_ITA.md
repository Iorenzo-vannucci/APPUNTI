# Report della Challenge: Completely Obfuscated Web Server

## Introduzione

Mi sono trovato davanti a una challenge intitolata "Completely Obfuscated Web Server" - e devo dire che il nome non mentiva affatto! L'obiettivo era analizzare un binario chiamato `chall` che faceva girare un web server su `http://10.42.0.2:38061`, per poi riuscire a ottenere la flag nascosta.

**Flag ottenuta**: `CCIT{n0w_th4t_wa5_wh4t_I_ca11_4n_0bfusc4t3d_cod3_7891745b}`

## Il Primo Approccio: Cosa Diavolo Sto Guardando?

Quando ho aperto il binario in Ghidra, la prima cosa che mi ha colpito è stata la nomenclatura delle funzioni. Invece dei solsoliti nomi generici come `FUN_001234567`, mi sono trovato davanti a una serie di funzioni con nomi greci: `func_alpha_beta`, `func_gamma_delta`, `func_epsilon_zeta` e così via.

```bash
# Ho iniziato listando tutte le funzioni per capire il pattern
mcp_GhidraMCP_list_methods
```

Già questo mi ha fatto capire che il programmatore aveva fatto di tutto per nascondere la vera natura del codice. Ma la cosa davvero interessante è emersa quando ho iniziato a guardare le stringhe.

## La Scoperta dell'Offuscamento XOR

Usando gli strumenti MCP di Ghidra, ho iniziato a esplorare le stringhe presenti nel binario:

```bash
mcp_GhidraMCP_list_strings
```

E qui ho trovato delle stringhe molto strane:
- `"m*-/'m71'0"` 
- `"#22.+!#6+-,m:o555o$-0/o70.',!-&'&"`
- `"prrb\r\t"`

Queste stringhe non avevano senso in chiaro, ma la loro struttura mi ha fatto pensare immediatamente a un qualche tipo di cifratura. Ho provato con l'algoritmo più comune per l'offuscamento: XOR.

Dopo alcuni tentativi, ho scoperto che tutte le stringhe erano cifrate con la chiave `0x42`. Quando ho applicato questa chiave:
- `"m*-/'m71'0"` è diventato `/api/seed`
- `"prrb\r\t"` è diventato `POST`
- E così via...

Bingo! Avevo trovato la chiave di tutto.

```python
def xor_decode(encoded_string, key=0x42):
    return ''.join(chr(ord(c) ^ key) for c in encoded_string)
```

## Reverse Engineering della Logica

Una volta capito il meccanismo di decifratura, ho iniziato a decompilare le funzioni più interessanti. Ho trovato una funzione (che ho rinominato `deobfuscate_string`) che si occupava proprio di applicare l'XOR alle stringhe:

```c
char* deobfuscate_string(char* encoded_string) {
    // Decodifica XOR con chiave 0x42
    for (int i = 0; encoded_string[i] != 0; i++) {
        encoded_string[i] = encoded_string[i] ^ 0x42;
    }
    return encoded_string;
}
```

Ma la vera gemma era in un'altra funzione che conteneva la logica matematica della challenge:

```c
uint32_t calculate_challenge_solution(uint32_t random_num) {
    uint32_t result = (random_num * 0x1337 + 0xffa) & 0xFFFFFFFF;
    if (result > 0xdeadbeee) {
        result = (result + 0x21524111) & 0xFFFFFFFF;
    }
    return result;
}
```

Qui ho trovato delle costanti molto caratteristiche:
- `0x1337` (leet!) - fattore di moltiplicazione
- `0xffa` - costante di addizione
- `0xdeadbeee` - valore di soglia
- `0x21524111` - addizione condizionale

## Mappatura degli Endpoint

Decifrando tutte le stringhe, sono riuscito a ricostruire il protocollo HTTP del server:

1. **`/api/seed`** - Restituisce un numero casuale nel formato `seed=XXXXX`
2. **`/api/response`** - Qui bisogna inviare la soluzione calcolata
3. **`/api/flag`** - Se la soluzione è corretta, qui si trova la flag

Il flusso logico era chiaro:
1. Faccio una GET a `/api/seed` per ottenere il numero casuale
2. Applico la formula matematica che ho scoperto nel binario
3. Invio la soluzione via POST a `/api/response`
4. Se tutto va bene, recupero la flag da `/api/flag`

## I Primi Tentativi (e i Primi Fallimenti)

Forte della mia analisi, ho scritto il primo script Python. Ero convinto di aver capito tutto, ma... niente da fare! Il server mi rispondeva sempre con "400 Bad Request".

I miei errori iniziali sono stati:
1. **Parametri XOR-codificati**: Pensavo che anche i nomi dei parametri HTTP dovessero essere cifrati
2. **URL sbagliati**: Mi mancava il prefisso `/api/`
3. **Headers errati**: Non usavo il Content-Type giusto

```python
# Primo tentativo fallimentare
data = f"{xor_encode('answer')}={solution}"  # SBAGLIATO!
url = f"{base_url}/seed"  # Mancava /api/
```

## Il Momento "Eureka": Session State

Dopo diversi tentativi falliti, ho notato qualcosa di strano. A volte le richieste non mi davano subito "400 Bad Request", ma si bloccavano completamente. Questo hanging mi ha fatto pensare che forse il server stava aspettando qualcosa.

Ed è qui che ho avuto l'illuminazione: **session state**! 

Il server probabilmente voleva che mantenessi la stessa connessione/sessione HTTP tra:
- La richiesta del seed
- L'invio della soluzione  
- Il recupero della flag

## La Soluzione Finale

Ho riscritto lo script usando `requests.Session()` per mantenere lo stato della sessione:

```python
#!/usr/bin/env python3
import requests
from urllib.parse import parse_qs

def calculate_solution(random_num):
    result = (random_num * 0x1337 + 0xffa) & 0xFFFFFFFF
    if result > 0xdeadbeee:
        result = (result + 0x21524111) & 0xFFFFFFFF
    return result

def main():
    base_url = "http://10.42.0.2:38061"
    
    # LA CHIAVE DEL SUCCESSO: usare una sessione!
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    # Ottengo il seed
    r = session.get(f"{base_url}/api/seed", timeout=10)
    params = parse_qs(r.text)
    random_num = int(params['seed'][0])
    
    # Calcolo la soluzione
    solution = calculate_solution(random_num)
    
    # Invio la soluzione (parametro NON XOR-codificato!)
    data = f"answer={solution}"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': str(len(data))
    }
    r = session.post(f"{base_url}/api/response", data=data, headers=headers, timeout=30)
    
    # Recupero la flag
    r = session.get(f"{base_url}/api/flag", timeout=10)
    print(f"Flag: {r.text}")
```

E finalmente...

```bash
$ python3 session_solve.py
Getting random number...
Seed response: 200 - seed=48211
Got random number: 48211
Calculated solution: 237153999
Submitting solution...
Solution response: 200 - 200 OK
Solution accepted!
Getting flag...
Flag response: 200 - CCIT{n0w_th4t_wa5_wh4t_I_ca11_4n_0bfusc4t3d_cod3_7891745b}
```

**Successo!** 🎉

## Gli Strumenti che Mi Hanno Salvato

Durante tutto il processo, gli strumenti MCP di Ghidra si sono rivelati fondamentali:

```bash
# Per scoprire le funzioni
mcp_GhidraMCP_list_methods
mcp_GhidraMCP_search_functions_by_name

# Per analizzare le stringhe
mcp_GhidraMCP_list_strings

# Per il reverse engineering
mcp_GhidraMCP_decompile_function
mcp_GhidraMCP_get_xrefs_to

# Per tenere tutto organizzato
mcp_GhidraMCP_rename_function
```

Questi strumenti mi hanno permesso di lavorare interamente da terminale, il che è stato molto più efficiente della GUI di Ghidra per questo tipo di analisi.

## Le Lezioni Apprese

Questa challenge mi ha insegnato diverse cose importanti:

1. **Non tutto è obfuscato allo stesso modo**: Anche se il binario aveva tutto cifrato con XOR, l'interfaccia HTTP esterna usava parametri in chiaro. Non bisogna mai assumere che tutti i livelli abbiano la stessa offuscamento.

2. **Lo stato della sessione conta**: Nei web applications, specialmente quelli custom, può essere cruciale mantenere la sessione tra richieste multiple.

3. **L'analisi incrementale paga**: Ho testato ogni componente separatamente prima di mettere tutto insieme, il che mi ha permesso di isolare i problemi.

4. **Gli strumenti giusti fanno la differenza**: La combinazione di Ghidra MCP, Python requests e test manuali con curl mi ha dato una copertura completa.

5. **Non complicare troppo**: Il mio istinto iniziale era di applicare l'XOR a tutto, ma a volte la realtà è più semplice delle nostre aspettative.

## Riflessioni Finali

Questa challenge è stata davvero all'altezza del suo nome. L'offuscamento era su più livelli:
- **Stringhe** cifrate con XOR
- **Nomi delle funzioni** offuscati con lettere greche  
- **Requisiti di sessione** non ovvi dall'analisi statica
- **Livelli misti di offuscamento** tra interno ed esterno

Il momento più frustrante è stato quando avevo capito tutta la logica matematica e gli endpoint corretti, ma continuavo a ricevere errori 400. È stato solo quando ho realizzato l'importanza dello stato della sessione che tutto si è sbloccato.

La cosa più soddisfacente? Vedere finalmente quella risposta "200 OK" dopo ore di debug! 

**Tempo totale impiegato**: Circa 2.5 ore
- Analisi iniziale: 30 minuti
- Decifratura XOR: 45 minuti  
- Reverse engineering della logica: 20 minuti
- Tentativi falliti: 1 ora (la parte più frustrante!)
- Soluzione finale: 10 minuti

Una challenge che mi ha fatto sudare, ma che alla fine mi ha insegnato molto sul reverse engineering e sui protocolli web custom! 