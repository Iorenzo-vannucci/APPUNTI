def colorDFS(grafo, nodo, colore, etichette):
    etichette[nodo] = colore
    for vicino in grafo[nodo]:
        if vicino not in etichette:
            colorDFS(grafo, vicino, 1 - colore, etichette)

# Esempio: albero rappresentato come dizionario di adiacenza
grafo = {
    0: [1, 2],
    1: [0, 3, 4],
    2: [0],
    3: [1],
    4: [1]
}

etichette = {}
colorDFS(grafo, 0, 0, etichette)

print("Etichette:", etichette)