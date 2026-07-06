import socket, json, sys, time, hashlib


def send_json(sock, msg):
    sock.sendall((json.dumps(msg) + "\n").encode('utf-8'))


def task_query(ip, porta, task_id, code_hash):
    # Chiede a un nodo se ha in cache il risultato per code_hash
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        sock.connect((ip, porta))
        send_json(sock, {"type": "TASK_QUERY", "task_id": task_id, "code_hash": code_hash})
        data = json.loads(sock.makefile('r', encoding='utf-8').readline())
        sock.close()
        return data.get("result") if data.get("status") == "FOUND" else None
    except Exception as e:
        print(f"[Client Stub] Errore contattando {ip}:{porta}: {e}")
        return None


def stampa_risultato(risultato, sorgente=""):
    # Stampa il risultato con un'intestazione
    print(f"\n[Client Stub] Risultato finale ({sorgente}):")
    print(f"--------------------------------------------------")
    print(risultato)
    print(f"--------------------------------------------------")


def invia_task(task_id, codice_payload, endpoints):
    # Invia la task ad un entry-point con failover e cache lookup
    code_hash = hashlib.sha1(codice_payload.encode()).hexdigest()
    request = {"task_id": task_id, "code": codice_payload, "code_hash": code_hash}
    tentativo_fatto = False

    for ip, porta in endpoints:
        # Dopo un fallimento, prima chiediamo alla cache
        if tentativo_fatto:
            print(f"[Client Stub] Provo endpoint di backup {ip}:{porta}...")
            risultato = task_query(ip, porta, task_id, code_hash)
            if risultato is not None:
                stampa_risultato(risultato, f"CACHE del nodo {ip}:{porta}")
                return

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(60.0)
            sock.connect((ip, porta))
            print(f"[Client Stub] Inviando task '{task_id}' all'entry-point {ip}:{porta}...")
            send_json(sock, request)

            ricevuto_errore = False
            for linea in sock.makefile('r', encoding='utf-8'):
                risposta = json.loads(linea)
                if risposta.get("status") == "ACK":
                    print(f"[Client Stub] ACK: {risposta.get('message', '')}")
                elif risposta.get("status") == "SETTLED":
                    risultato = str(risposta.get('result'))
                    if risultato.startswith("Errore"):
                        print(f"[Client Stub] Errore cluster: {risultato}")
                        ricevuto_errore = True
                        break
                    sorgente = "Recuperato da CACHE del cluster" if risposta.get("cache_hit") else "Quorum raggiunto lato cluster"
                    stampa_risultato(risultato, sorgente)
                    sock.close()
                    return
            sock.close()
            if not ricevuto_errore:
                print(f"[Client Stub] Connessione persa con {ip}:{porta}.")
            print(f"[Client Stub] Provo un altro endpoint...")
            tentativo_fatto = True
            time.sleep(2)
        except Exception as e:
            print(f"[Client Stub] Errore contattando {ip}:{porta}: {e}")
            tentativo_fatto = True

    # Ultimo tentativo via cache
    print(f"\n[Client Stub] Tutti gli endpoint esauriti. Ultimo tentativo via cache...")
    for ip, porta in endpoints:
        risultato = task_query(ip, porta, task_id, code_hash)
        if risultato is not None:
            stampa_risultato(risultato, f"CACHE del nodo {ip}:{porta}")
            return
    print(f"[Client Stub] FALLIMENTO: Nessun risultato ottenibile per '{task_id}'.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and ":" not in sys.argv[1]:
        with open(sys.argv[1], "r") as f:
            codice_payload = f.read()
    else:
        codice_payload = 'i=0\nwhile i<2:\n\ti=i+1\n\tprint("Test")'

    code_hash = hashlib.sha1(codice_payload.encode()).hexdigest()
    task_id = f"TASK-{code_hash[:8].upper()}"

    # Parsiamo endpoint dalla CLI
    endpoints = []
    endpoint_args = sys.argv[2:] if len(sys.argv) > 1 and ":" not in sys.argv[1] else sys.argv[1:]
    for arg in endpoint_args:
        if ":" in arg:
            h, p = arg.rsplit(":", 1)
            endpoints.append((h, int(p)))
    if not endpoints:
        endpoints = [("127.0.0.1", 5005)]

    invia_task(task_id, codice_payload, endpoints)
