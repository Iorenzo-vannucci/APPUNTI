from collections import defaultdict
import os

def solve(code):
    current = 0
    var_values = defaultdict(int)

    while current < len(code):
        inst = code[current][:3]
        if inst == "add": 
             var_values[code[current][4]] += int(code[current].split()[-1])
        elif inst == "sub":
            var_values[code[current][4]] -= int(code[current].split()[-1])
        elif inst == "mul":
            var_values[code[current][4]] *= int(code[current].split()[-1])
        elif inst == "jmp":
            var, val, lab = code[current].split()[1:]
            if var_values[var] == int(val):
                current = code.index(f"lab {lab}")
        current += 1
    return sum(var_values[x] for x in 'abcdef')

def read_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines()]

# Directory contenente i file di input
input_directory = "/Users/lorenzovannucci/Downloads/2024-emulation-dataset/input"  # Sostituisci con il percorso corretto

# Lista dei nomi dei file di input
input_files = [f"input{i}.txt" for i in range(1, 16)]

# Test per ogni file
for filename in input_files:
    filepath = os.path.join(input_directory, filename)  # Costruisci il percorso completo
    try:
        code = read_file(filepath)  # Leggi le righe del file
        sol = solve(code)  # Esegui il programma
        print(f"Risultato per {filepath}: {sol}")
    except FileNotFoundError:
        print(f"File {filepath} non trovato.")
    except Exception as e:
        print(f"Errore durante l'elaborazione di {filepath}: {e}")