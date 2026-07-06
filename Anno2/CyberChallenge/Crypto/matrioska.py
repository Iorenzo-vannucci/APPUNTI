import base64
import gzip
import sys
import os

# --- Funzione per decodificare e decomprimere ---
def decode_and_decompress(input_filepath):
    try:
        # 1. Leggi il contenuto Base64 dal file specificato
        print(f"Lettura del file: {input_filepath}")
        with open(input_filepath, 'r') as f:
            b64_data = f.read()

        # Rimuovi eventuali spazi bianchi extra o newline che potrebbero interferire
        b64_data = "".join(b64_data.split())

        if not b64_data:
            print("Errore: Il file di input è vuoto.")
            return

        print("Decodifica Base64...")
        # 2. Decodifica da Base64
        compressed_data = base64.b64decode(b64_data)

        print("Decompressione Gzip...")
        # 3. Decomprimi con Gzip
        original_data_bytes = gzip.decompress(compressed_data)

        # --- Salva e mostra i dati decompressi ---

        # Genera un nome file di output basato sull'input
        # Rimuove spazi e caratteri potenzialmente problematici dal nome base per il file di output
        safe_base_name = os.path.basename(input_filepath).replace(" ", "_").replace("2", "two") # Esempio di sostituzione
        base_name_no_ext = os.path.splitext(safe_base_name)[0]
        output_filename_text = f"{base_name_no_ext}_decompressed.mml"
        output_filename_bin = f"{base_name_no_ext}_decompressed.bin"


        # 4. Prova a decodificare come testo (UTF-8)
        try:
            original_data_text = original_data_bytes.decode('utf-8')
            # Salva il risultato su un file
            with open(output_filename_text, "w", encoding='utf-8') as f:
                f.write(original_data_text)
            print(f"\nDati decompressi (testo) salvati in: {output_filename_text}")
            print("\n--- Inizio Anteprima Dati Decompressi ---")
            print(original_data_text[:2000]) # Stampa solo l'inizio per l'anteprima
            print("--- Fine Anteprima Dati Decompressi ---")

        except UnicodeDecodeError:
            print("\nAttenzione: I dati decompressi non sono testo UTF-8 valido.")
            # Salva comunque i dati binari.
            with open(output_filename_bin, "wb") as f:
                f.write(original_data_bytes)
            print(f"Dati binari decompressi salvati in: {output_filename_bin}")
            print("Analizza il file binario con strumenti appropriati (es. un editor esadecimale).")

    except FileNotFoundError:
        print(f"Errore: File non trovato '{input_filepath}'")
        print("Verifica che il percorso sia corretto e che il file esista.")
    except base64.binascii.Error as e:
        print(f"Errore durante la decodifica Base64: {e}")
        print("Assicurati che il file contenga dati Base64 validi e completi.")
    except gzip.BadGzipFile:
        print("Errore: I dati dopo la decodifica Base64 non sembrano essere un file Gzip valido.")
    except Exception as e:
        print(f"Si è verificato un errore imprevisto: {e}")

# --- Esecuzione dello script ---
if __name__ == "__main__":
    # *** Modifica qui: Specifica direttamente il path del file ***
    # Assicurati che il path sia corretto per il tuo sistema
    hardcoded_input_path = "/Users/lorenzovannucci/Desktop/zk6uCiN6F9nhBMIA 2.txt"

    # Chiama la funzione con il path hardcoded
    decode_and_decompress(hardcoded_input_path)