import subprocess
import time
import re

# Dati dell'app
host = "faas.challs.cyberchallenge.it"
app_id = "16dcf030-b5a0-47a7-aa4e-28f2fa8cd7a8"

def ask_auth():
    print("🔐 Chiedo autorizzazione...")
    result = subprocess.run(
        ["python3", "faas.py", host, app_id, "ask_auth"],
        capture_output=True, text=True
    )
    output = result.stdout.strip()
    print(output)
    match = re.search(r"wait token: ([a-f0-9\-]+)", output)
    if match:
        return match.group(1)
    else:
        print("❌ Impossibile trovare il wait token.")
        exit(1)

def check_auth(wait_token):
    result = subprocess.run(
        ["python3", "faas.py", host, app_id, "check_auth", wait_token],
        capture_output=True, text=True
    )
    return result.stdout.strip()

def main():
    wait_token = ask_auth()
    print(f"⏳ Attendo autorizzazione per il wait token: {wait_token}\n")

    while True:
        output = check_auth(wait_token)
        print(output)

        if "refresh_token" in output or "authorized" in output.lower():
            print("\n✅ Autorizzazione concessa!")
            break

        if "No auth for the moment" in output:
            print("⏱️ Ancora niente... riprovo tra 5 secondi.")
            time.sleep(5)
        else:
            print("⚠️ Risposta inaspettata, interrompo.")
            break

if __name__ == "__main__":
    main()