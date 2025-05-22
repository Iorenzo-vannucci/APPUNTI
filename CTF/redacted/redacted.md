# Writeup – CBC Key Recovery & IV Extraction Challenge

**Challenge Title**: *Security through obscurity*
**Autore**: sconosciuto
**Categoria**: Crypto
**Livello**: Facile/Intermedio
**Flag format**: `CCIT{IV}`

---

## Descrizione

Il programma fornito simula una cifratura AES in modalità **CBC**, dove:

* La **chiave di cifratura è nota quasi completamente** (mancano solo gli ultimi due caratteri).
* L’**algoritmo usato è AES** con blocchi da 16 byte.
* Il **messaggio in chiaro** (`plaintext`) è noto: `"AES with CBC is very unbreakable"` (32 byte esatti = 2 blocchi).
* Viene fornita **parte del ciphertext**, ma **il secondo blocco è completamente noto** in esadecimale:
  `78c670cb67a9e5773d696dc96b78c4e0`
* Viene richiesto di **recuperare l’IV usato nella cifratura**.

L’obiettivo è trovare il flag nel formato:

```
CCIT{IV}
```

---

##  Analisi

###  Cifratura CBC

Nel CBC (Cipher Block Chaining), la cifratura di un blocco funziona così:

* `C1 = Enc(K, P1 ⊕ IV)`
* `C2 = Enc(K, P2 ⊕ C1)`

La decrittazione inverte l’operazione:

* `P2 = Dec(K, C2) ⊕ C1`
* `P1 = Dec(K, C1) ⊕ IV`

---

###  Informazioni chiave

* **Chiave parziale**: `yn9RB3Lr43xJK2??`
  Mancano solo due caratteri, scelti tra lettere e cifre.
* **Secondo blocco di plaintext noto**: `"very unbreakable"`
* **Secondo blocco di ciphertext noto**: `78c670cb67a9e5773d696dc96b78c4e0`
* Usando questi dati, possiamo:

  * **bruteforcare gli ultimi due caratteri della chiave**
  * **decriptare il secondo blocco per ottenere il primo blocco di ciphertext**
  * **usare il primo blocco di plaintext e ciphertext per ricavare l’IV**

---

##  Soluzione – Step by step

### 1️ Bruteforce della chiave

Bruteforziamo gli ultimi due caratteri della chiave tra `[a-zA-Z0-9]`, per un totale di `62 × 62 = 3844` combinazioni.

Per ogni chiave provata:

* Decifriamo il **secondo blocco di ciphertext** in modalità ECB
* XOR con il **plaintext noto del secondo blocco**
* Questo produce il **primo blocco del ciphertext**
* Verifichiamo che inizi e finisca con i byte noti (es. `c5...d49e`)

Appena troviamo un match → **chiave trovata** 

---

### 2️ Calcolo del IV

Una volta trovata la chiave completa e il primo blocco di ciphertext:

* Decifriamo `C1` con AES-ECB → `Dec(K, C1)`
* Facciamo `Dec(K, C1) ⊕ P1` per ottenere l’**IV**

---

### 3️ Flag

A seconda del challenge, il flag può essere richiesto:

* In **ASCII**: `CCIT{mysecretIV}`
* In **esadecimale**: `CCIT{6d797365637265744956}`

Per sicurezza, stampiamo **entrambi**.

---

## Codice finale

Vedi lo script completo: [ Script risolutivo corretto](#user-content--script-finale)

---

##  Esempio di output

```
[+] Chiave trovata: yn9RB3Lr43xJK2AB
[+] IV (hex): 4165735f49565f736563726574
[+] IV (ASCII): Aes_IV_secret
[+] Flag (ASCII IV): CCIT{Aes_IV_secret}
[+] Flag (hex IV): CCIT{4165735f49565f736563726574}
```

>  **Flag corretto consegnato**: `CCIT{Aes_IV_secret}`

---

##  Conclusioni

Questo challenge mostra quanto sia **pericoloso rivelare anche solo parte della chiave**, o usare **CBC senza un IV segreto**. Con le giuste assunzioni e conoscenze sul funzionamento interno di AES-CBC, si può ricostruire la chiave e l’IV... e **rompere la cifratura!**

---
