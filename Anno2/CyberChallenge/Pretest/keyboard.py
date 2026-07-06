def cerca_lettera(file_path):
    # Legge il contenuto del file
    with open(file_path, 'r') as file:
        data = file.readlines()
    
    # La prima riga contiene il numero di stringhe
    N = int(data[0].strip())
    
    alfabeto = 'abcdefghijklmnopqrstuvwxyz'
    
    # lettere mancanti
    lettere_mancante = []
    
    # Check coppia
    for i in range(N):
        # Le stringhe da considerare vanno a coppie cone le rispettive lunghezze
        string = data[2 * i + 2].strip()

        # Controllo lettera per lettera
        for letter in alfabeto:
            if letter not in string:
                lettere_mancante.append(letter)
                break  
    
    # Stampa i risultati
    for lettera in lettere_mancante:
        print(lettera)

path = '/Users/lorenzovannucci/Downloads/2025-keyboard_keyboard-2_1738075266.txt'
cerca_lettera(path)