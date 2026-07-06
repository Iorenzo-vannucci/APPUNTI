from Crypto.Util.number import long_to_bytes
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad # Importa unpad per la decifratura
import sys # Per uscire in caso di errore

# Valori forniti direttamente nello script
p = 139379733354483189501227871110064527157682987958433427156390202678064149815642568826477911770307752913621426076298507790818439936280449152741721879461096492477608431936689120104356856262262510907004792117855182041421333215157243722734389759734373030448619917500336774214725967664965383449965717319942422012769
g = 141766002927079634436012416932426270195633516375074194269497658683856933939749443631920896002088564385320471756930651924877164463775158556657562652267307493472917448586968014693578189551533885711413705919878486107011929558061609254391556828943430904948541065524176574683093670163402084986719526042666437454093
pubA = 66016709400498362636875074602841729207604794529650288520206492814919780360783708766932535497512319649726274113961638853865431404545264600640090701462114753302958560839001532056864200400813840304804168459012583090289433312917793089693811381875506133051726976084529081221968387648987529391439097289229126508657
pubB = 133227005774287036263116319213286327328023826794360062545765483165358414788214818135925261563492163513299648752612241934102242044547030469122144101231822302310174491118256008699381279457737273945228911100642427945143296557018573202722398182706517728025099779057026709510256921227257159199663754440944499687527
ct_hex = "fe7d573c3f2bd0320ca5e175ca7ba52586f1da4354644b641e775fed1fddc3988a689ab5b0e5ed557093bb0c24690e75"

# Convert hex ciphertext to bytes
ct_bytes = bytes.fromhex(ct_hex)

# --- Brute-force per trovare privA (assumendo sia piccolo) ---
print("Tentativo di trovare la chiave privata privA tramite brute-force...")
privA = -1
# Imposta un limite ragionevole. Se nbits era 1024 o 2048, questo dovrebbe bastare.
# Puoi aumentare questo valore se non trova la chiave.
max_s_to_check = 4096 

for s in range(max_s_to_check + 1):
    if pow(g, s, p) == pubA:
        privA = s
        print(f"Trovato! privA = {privA}")
        break
    # Stampa un progresso ogni tanto (opzionale)
    if s % 500 == 0 and s != 0:
        print(f"  ... controllato fino a s = {s}")

if privA == -1:
    print(f"Errore: Impossibile trovare privA entro il limite di {max_s_to_check}.")
    print("Potrebbe essere necessario aumentare 'max_s_to_check' o provare a trovare privB.")
    sys.exit(1) # Esce dallo script se non trova la chiave

# --- Calcola il segreto condiviso usando privA e pubB ---
shared_secret = pow(pubB, privA, p)
print(f"Shared secret calcolato: {shared_secret}") # Stampa opzionale

# --- Deriva la chiave AES dal segreto condiviso ---
key = hashlib.sha256(long_to_bytes(shared_secret)).digest()[:16]
print(f"Chiave AES derivata (hex): {key.hex()}") # Stampa opzionale

# --- Decifra il ciphertext ---
try:
    cipher = AES.new(key, AES.MODE_ECB)
    padded_flag = cipher.decrypt(ct_bytes)
    # Rimuovi il padding PKCS#7
    flag_bytes = unpad(padded_flag, AES.block_size) # AES.block_size è 16
    flag = flag_bytes.decode('utf-8') # Decodifica in stringa (assumendo sia UTF-8)

    print("-" * 30)
    print(f"FLAG DECIFRATO: {flag}")
    print("-" * 30)

except ValueError as e:
    print(f"\nErrore durante la decifratura o l'unpadding: {e}")
    print("Questo può accadere se la chiave calcolata è errata o il padding è corrotto.")
except Exception as e:
    print(f"\nErrore generico durante la decifratura: {e}")