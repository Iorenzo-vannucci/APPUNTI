# The password policy for our website is very hard to verify, in particular, when a user is changing it, the new password should follow all these requirements:
# 1. The new password must be at least 8 characters long.
# 2. The new password must be at most 16 characters long.
# 3. The new password must contains both lowercase and uppercase letters.
# 4. The new password must contains at least one digit and one special character.
# 5. The new password must not contain two consecutive identical characters.
# 6. The new password must not be derivable by deleting, substituting or adding exactly one character from the old password.

import os
from string import *

def check_password(stringa):
    maiuscola = False
    if (len(stringa)<8):
        print("PASSWORD TROPPO CORTA")
        return
    else:
        if(len(stringa)>16):
            print("PASSWORD TROPPO LUNGA")
            return
        else:
            for i in range (len(stringa)):
                if(stringa[i]!=stringa[i].upper()):
                    continue
                else:
                    maiuscola = True
                    break

            if(maiuscola==True):
                print("trovata")
                if(stringa==stringa.upper()):
                    print("SOLO MAIUSCOLE\n\n")
                    return
                
            else:
                print("non trovata")


def valid2(p):
    return (
        check_password(p)  # Verifica i requisiti definiti nella funzione valid1 (lunghezza, almeno una minuscola, almeno una maiuscola).
        and any(c in digits for c in p)  # La stringa deve contenere almeno una cifra.
        and any(c in punctuation for c in p)  # La stringa deve contenere almeno un carattere speciale.
        and all(p[i] != p[i+1] for i in range(len(p)-1))  # Non ci devono essere caratteri consecutivi uguali.
    )

def valid3(p, old):
    # Cancellazione da old
    check1 = not any(p == (old[:i] + old[i+1:]) for i in range(len(old)-1)) # Sostituzione da old
    check2 = len(p) == len(old) and not any(
        (p[:i] + p[i+1:]) == (old[:i] + old[i+1:]) for i in range(len(old)-1)) # Aggiunta da old
    check3 = not any(old == (p[:i] + p[i+1:])
        for i in range(len(old)-1))
    
    return valid2(p) and check1 and check2 and check3




                    
                
def process_passwords(folder_path):
    # Trova tutti i file nella cartella
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    
    for file in files:
        with open(file, 'r') as f:
            lines = f.readlines()
            N = int(input())
            for _ in range(N):
                p1, p2 = input().split(" ")
                print(1 if valid3(p1, p2) else 0)
            
            #old_password = lines[0].strip()  # Vecchia password
            #new_password = lines[1].strip()  # Nuova password
            
            # Valida le password
            result = valid3(p1, p2)
            print(f"File: {file} -> Risultato: {'Valida' if result else 'Non valida'}")

# Esempio di utilizzo
#password_in = input("Scrivi una password: ")

folder = "/Users/lorenzovannucci/Desktop/2022-ppo-dataset/input"  # Sostituisci con il percorso della tua cartella
process_passwords(folder)
                