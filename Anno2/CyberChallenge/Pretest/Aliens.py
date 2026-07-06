import sys
#funzioni
def aggiungi_carattere(stringa_aggiungi, carattere_add):
    return stringa_aggiungi + carattere_add

def cancella_carattere(stringa_cancella):
    return stringa_cancella[:-1] if stringa_cancella else ""

def scambia_carattere(stringa_swap, primo_carattere, secondo_carattere):
    temp = ""
    for char in stringa_swap:
        if char == primo_carattere:
            temp += secondo_carattere
        elif char == secondo_carattere:
            temp += primo_carattere
        else:
            temp += char
    return temp

def ruota_stringa(stringa_ruota, num_posizioni_ruota, alfabeto):
    temp = ""
    for carattere in stringa_ruota:
        if carattere in alfabeto:
            posizione = alfabeto.index(carattere)
            #il resto è per gestire possibile numeri superiori al numero totale di caratteri
            new_pos = (posizione + num_posizioni_ruota) % len(alfabeto)
            temp += alfabeto[new_pos]
        else:
            temp += carattere
    return temp

def esegui(code):
    alfabeto = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    stringa = ""
    
    for operation in code:
        pezzo = operation.split()
        
        if pezzo[0] == "add":
            stringa = aggiungi_carattere(stringa, pezzo[1])
            
        elif pezzo[0] == "del":
            stringa = cancella_carattere(stringa)

#TERZA SUBTASK USO TUTTO
        elif pezzo[0] == "swap":
            stringa = scambia_carattere(stringa, pezzo[1], pezzo[2])
            
        elif pezzo[0] == "rot":
            stringa = ruota_stringa(stringa, int(pezzo[1]), alfabeto)
    
    return stringa


#input e lettura
input_path = "/Users/lorenzovannucci/Downloads/2025-aliens_aliens-3_1738078676.txt"
with open(input_path, 'r') as fin:
    code = [fin.readline().strip() for _ in range(int(fin.readline().strip()))]
    print(esegui(code))
