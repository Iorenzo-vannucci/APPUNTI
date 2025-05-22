# Sfruttamento del Token di Login CBC — Writeup

## Panoramica della Sfida

La sfida implementa un semplice sistema di autenticazione basato su token e esecuzione di comandi utilizzando AES in modalità CBC. Le funzionalità principali sono:

1.  **Registrazione utente** → Genera un `login_token` cifrando `login_token:{username}` con un IV casuale e una chiave AES condivisa.
2.  **Generazione del command token** → Prende un `login_token` valido, lo decifra ed emette un `command_token` per eseguire comandi cifrati.
3.  **Esecuzione del comando** → Utilizza il `command_token` per eseguire comandi come `get_flag`.
4.  **Visualizzazione del database** → Permette di visualizzare gli IV utilizzati durante la registrazione.

Formato della flag: `CCIT{...}`

---

## Protezioni Intese

*   `admin` è pre-registrato; non puoi registrarlo tu stesso.
*   L'IV utilizzato durante la registrazione viene salvato per ogni utente.
*   Il padding è utilizzato correttamente, e gli errori di unpad sono gestiti.
*   Un semplice controllo sul prefisso `login_token:` deve corrispondere in fase di decifratura.

Ma c'è un **difetto critico**.

---

## Vulnerabilità

La modalità AES-CBC decifra ogni blocco come segue:
content_copy
download
Use code with caution.
Markdown
P1 = D(C1) ⊕ IV
P2 = D(C2) ⊕ C1
... ecc.

Il difetto è che **possiamo modificare liberamente l'IV** nel token di login.
Questo significa che possiamo manipolare il **primo blocco di plaintext** (che è `login_token:XXXX`) per farlo leggere `login_token:admin` cambiando l'IV di conseguenza.

---

## Passi di Sfruttamento

### Passo 1️ — Registra un utente controllato

Registriamo un utente con un nome utente di 5 caratteri, dove **solo i primi 4 caratteri vengono alterati tramite IV**:

```text
0000n → verrà modificato in admin usando la manipolazione dell'IV
content_copy
download
Use code with caution.
Passo 2️ — Estrai il token e calcola l'IV falso
Supponiamo tu ottenga:

IV = IV_1
ciphertext = C1 + C2
content_copy
download
Use code with caution.
Allora:

blocco di plaintext P1 = D(C1) ⊕ IV_1 = 'login_token:0000'
content_copy
download
Use code with caution.
Desideri P1 = 'login_token:admi', quindi:

new_IV = IV_1 ⊕ ('login_token:0000') ⊕ ('login_token:admi')
content_copy
download
Use code with caution.
Applica la differenza XOR solo ai byte che controlli (in questo caso, gli ultimi 4).

Crea un nuovo token di login con:

login_token = new_IV + ciphertext
content_copy
download
Use code with caution.
Passo 3️ — Forgia il command token come admin
Usa il tuo token falsificato nell'opzione 2, inserisci l'esadecimale di get_flag e ottieni un command token emesso utilizzando l'IV di admin.

Passo 4️ — Ottieni la flag!
Usa il command token dal passo 3 nell'opzione 3 — se l'IV corrisponde a quello salvato per admin, ottieni la flag.

Perché Funziona
AES CBC decifra il primo blocco usando l'IV. Se controlliamo l'IV, controlliamo il plaintext di quel blocco.
Il server si basa sulla stringa di plaintext login_token:admin ma non si assicura che sia stata generata in modo sicuro.
Gli IV sono prevedibili e riutilizzati. La chiave è la stessa per tutte le operazioni.
Script finale (Python)
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import os

# token_login originale: IV + ciphertext("login_token:0000n")
IV = bytes.fromhex("...")  # replace with original IV
ciphertext = bytes.fromhex("...")  # ciphertext from registration

old = b"login_token:0000"
target = b"login_token:admi"

# Calcola nuovo IV
new_iv = bytes([a ^ b ^ c for a, b, c in zip(IV, old, target)])

# Ricostruisce il nuovo login token
forged_token = new_iv.hex() + ciphertext.hex()
print("Token di login falsificato:", forged_token)
content_copy
download
Use code with caution.
Python
Flag
CCIT{...}
content_copy
download
Use code with caution.
(Sostituisci ... con la flag ottenuta.)

Note
CBC non è sicuro se l'IV è controllato dall'utente.
L'IV deve essere imprevedibile e la sua integrità deve essere verificata.
Non fidarti mai dell'input decifrato senza autenticazione (es. HMAC).
**Come salvare questo contenuto come file:**

1.  Copia tutto il testo che trovi nel blocco di codice qui sopra (dal primo `# CBC Login Token Exploit...` fino all'ultima riga `*   Non fidarti mai dell'input...`).
2.  Apri un semplice editor di testo sul tuo computer (come Blocco note su Windows, TextEdit su macOS, o Gedit/Nano/Vim su Linux).
3.  Incolla il testo copiato nell'editor.
4.  Salva il file. Quando ti chiede il nome e il tipo, scegli un nome (es. `cbc_writeup.md`) e assicurati che l'estensione sia `.md`. Se l'editor salva per default come `.txt`, potresti dover selezionare "Tutti i file" come tipo e poi scrivere l'estensione `.md` manualmente nel nome del file. Assicurati anche che la codifica sia UTF-8.

In questo modo avrai un file Markdown contenente il writeup tradotto.
content_copy
download
Use code with caution.
