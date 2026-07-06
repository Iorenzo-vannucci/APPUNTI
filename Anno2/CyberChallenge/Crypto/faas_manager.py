import subprocess
import time
import re
import os

host = "faas.challs.cyberchallenge.it"
app_id = "ffedd69a-cc25-4511-838f-14c5fb167ba0"
token_file = "refresh_token.txt"


def run_cmd(args):
    result = subprocess.run(["python3", "faas.py", host, app_id] + args, capture_output=True, text=True)
    print(result.stdout.strip())
    return result.stdout.strip()


def ask_auth():
    print("🔐 Chiedo autorizzazione...")
    output = run_cmd(["ask_auth"])
    match = re.search(r"wait token: ([a-f0-9\-]+)", output)
    if match:
        return match.group(1)
    else:
        print("❌ Wait token non trovato.")
        return None


def check_auth(wait_token):
    print("⏳ Controllo autorizzazione...")
    output = run_cmd(["check_auth", wait_token])
    if "Auth token:" in output:
        match = re.search(r"Auth token: ([a-f0-9\-]+)", output)
        if match:
            refresh_token = match.group(1)
            with open(token_file, "w") as f:
                f.write(refresh_token)
            print(f"✅ Autorizzazione ottenuta! Token salvato in {token_file}")
        else:
            print("❌ Token non trovato.")
    elif "No auth" in output:
        print("⏱️ Ancora niente, riprova più tardi.")
    else:
        print("⚠️ Risposta inaspettata.")


def get_token():
    if not os.path.exists(token_file):
        print("⚠️ Nessun refresh_token salvato. Richiedilo prima.")
        return None
    with open(token_file) as f:
        return f.read().strip()


def get_key():
    token = get_token()
    if not token:
        return
    key = input("🔑 Inserisci la chiave da leggere: ")
    run_cmd(["get", key, token])


def set_key():
    token = get_token()
    if not token:
        return
    key = input("🔑 Inserisci la chiave da scrivere: ")
    value = input("✏️ Inserisci il valore da scrivere: ")
    run_cmd(["set", key, value, token])


def main():
    while True:
        print("\n== FaaS Manager ==")
        print("[1] Chiedi autorizzazione (ask_auth)")
        print("[2] Controlla autorizzazione (check_auth)")
        print("[3] Leggi chiave (get)")
        print("[4] Scrivi chiave (set)")
        print("[5] Esci")

        choice = input("Scegli: ").strip()

        if choice == "1":
            wait = ask_auth()
            if wait:
                print(f"🔁 Il tuo wait_token è: {wait}")
        elif choice == "2":
            wait_token = input("🔁 Inserisci il wait_token: ").strip()
            check_auth(wait_token)
        elif choice == "3":
            get_key()
        elif choice == "4":
            set_key()
        elif choice == "5":
            print("👋 Ciao!")
            break
        else:
            print("❌ Scelta non valida.")


if __name__ == "__main__":
    main()