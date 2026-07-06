from collections import defaultdict
import sys

def trova_coppie_valide_ottimizzato(n, sequenza):
    # Passo 1: Trova tutte le triple valide (i, j, k) con indici distinti e a_i * a_j = a_k^2
    triplette = 0  # Inizializziamo a 0 per contare le triplette valide
    indici_zero = [i for i, valore in enumerate(sequenza) if valore == 0]

    for k in range(n):
        obiettivo = sequenza[k] ** 2
        # Crea un dizionario delle frequenze, escludendo sequenza[k]
        frequenze = defaultdict(int)
        for i in range(n):
            if i != k:
                frequenze[sequenza[i]] += 1

        if sequenza[k] == 0:
            # Gestiamo il caso degli zeri (più complesso)
            pass
        else:
            for i in range(n):
                if i == k:
                    continue
                ai = sequenza[i]
                if ai == 0:
                    if obiettivo != 0:
                        continue
                    continue
                if obiettivo % ai != 0:
                    continue
                richiesto = obiettivo // ai
                conta = frequenze[richiesto]
                if richiesto == ai:
                    conta -= 1  # Escludi j == i
                if conta > 0:
                    triplette += conta  # Aggiungi il numero di triplette valide

    return triplette


def principale():
    # Sostituisci con il percorso del file
    percorso_file = '/Users/lorenzovannucci/Downloads/input-4.txt'

    with open(percorso_file, 'r') as f:
        dati_input = f.read().split()
    
    puntatore = 0
    numero_sequenze = int(dati_input[puntatore])
    puntatore += 1
    
    for _ in range(numero_sequenze):
        lunghezza_sequenza = int(dati_input[puntatore])
        puntatore += 1
        sequenza = list(map(int, dati_input[puntatore:puntatore+lunghezza_sequenza]))
        puntatore += lunghezza_sequenza
        risultato = trova_coppie_valide_ottimizzato(lunghezza_sequenza, sequenza)
        print(risultato)

if __name__ == '__main__':
    principale()
