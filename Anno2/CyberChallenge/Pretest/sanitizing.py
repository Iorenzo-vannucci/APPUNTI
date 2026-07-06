def main():
    # Percorso del file sul desktop
    file_path = "/Users/lorenzovannucci/Downloads/2024-sanitization_sanitization-2_1738061837.txt"  # Sostituisci con il percorso corretto
    
    try:
        # Leggi il file
        with open(file_path, 'r') as file:
            data = file.read().splitlines()
        
        # Read N and M
        N, M = map(int, data[0].split())
        
        # Read banned words
        banned_words = set()
        for i in range(1, M + 1):
            banned_words.add(data[i].strip())
        
        # Process input strings
        results = []
        for i in range(M + 1, M + N + 1):
            input_string = data[i].strip()
            is_banned = False
            for word in banned_words:
                if word in input_string:  # Case-sensitive substring check
                    is_banned = True
                    break
            if is_banned:
                results.append("BANNED")
            else:
                results.append("SAFE")
        
        # Print results
        for result in results:
            print(result)
    
    except FileNotFoundError:
        print(f"File {file_path} non trovato.")
    except Exception as e:
        print(f"Errore durante l'elaborazione del file: {e}")

if __name__ == "__main__":
    main()