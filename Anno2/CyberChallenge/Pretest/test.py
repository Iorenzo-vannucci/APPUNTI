import random

# Parametri
N = 10  # Numero di intervalli da generare
min_val, max_val = 0, 10  # Range dei numeri negli intervalli
K = random.randint(1, 4)  # Numero casuale di intervalli per il controllo

# Generazione casuale degli intervalli
intervalli = [(random.randint(min_val, max_val - 1), random.randint(min_val + 1, max_val))
for _ in range(N)
]
intervalli = [(min(a, b), max(a, b)) for a, b in intervalli]  # Ordina correttamente ogni intervallo
print("Intervalli generati:", intervalli)
print("K scelto casualmente:", K)

# Dizionario per contare le occorrenze dei numeri
conteggio_numeri = {}

# Conta i numeri in ogni intervallo
for inizio, fine in intervalli:
    #scorri i numeri di ogni intervallo
    for numero in range(inizio, fine + 1):
        if numero not in conteggio_numeri:
            conteggio_numeri[numero] = 0
        conteggio_numeri[numero] += 1

# Filtra i numeri presenti esattamente in K intervalli
numeri_in_k_intervalli = [numero for numero, conteggio in conteggio_numeri.items() if conteggio == K]

# Risultati
print("Numeri che appaiono esattamente in", K, "intervalli:", numeri_in_k_intervalli)
print("Totale:", len(numeri_in_k_intervalli))