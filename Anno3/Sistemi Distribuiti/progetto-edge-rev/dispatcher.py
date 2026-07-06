import socket, threading, json, subprocess, os, sys, time, hashlib, signal, tempfile
from collections import Counter #usato per il voto di maggioranza 
from chord import ChordNode

HOST = '0.0.0.0'
PORT = 5005


CHORD_LOCK = threading.Lock()
NODO_CHORD = None

TASK_CACHE = {}
TASK_CACHE_LOCK = threading.Lock()

ERRORE_PREFISSI = ("Errore:", "Runtime Error", "Errore interno")

SHARED_TASKS_LOCAL = os.environ.get("LOCAL_SHARED_TASKS", os.path.join(os.getcwd(), "shared_tasks"))
SHARED_TASKS_HOST = os.environ.get("HOST_SHARED_TASKS", SHARED_TASKS_LOCAL)#per volumi docker  fargli capire dove sta shared tasks

EXECUTOR = os.environ.get("SDEP_EXECUTOR", "local").lower()
TASK_TIMEOUT = float(os.environ.get("SDEP_TASK_TIMEOUT", "30"))


def prepara_shared_tasks_dir(): #funzione per creare se non esiste la cartella per i task
    try:
        os.makedirs(SHARED_TASKS_LOCAL, exist_ok=True)
    except OSError as e:
        print(f"[Worker] Directory shared_tasks non inizializzabile: {SHARED_TASKS_LOCAL} ({e})")


def writable_task_dir(): #garantisce che il dispatcher abbia permessi di scrittura creando un file e eliminandolo poi 
    candidates = [
        SHARED_TASKS_LOCAL,
        os.path.join(tempfile.gettempdir(), "sdep_shared_tasks"),
    ]
    last_error = None
    for path in candidates:
        try:
            os.makedirs(path, exist_ok=True)
            fd, probe = tempfile.mkstemp(prefix=".write-test-", dir=path)
            os.close(fd)
            os.remove(probe)
            return path
        except OSError as e:
            last_error = e
    raise OSError(f"Nessuna directory task scrivibile. Ultimo errore: {last_error}")


prepara_shared_tasks_dir()


def is_risultato_valido(result):
    return result is not None and not any(result.startswith(p) for p in ERRORE_PREFISSI) #verifichiamo che il risultato non sia un errore


def send_json(sock, msg):
    sock.sendall((json.dumps(msg) + "\n").encode('utf-8')) #mandiamo il messaggio sottoforma di json al socket


def resolve_connect_host(ip):
    if NODO_CHORD is not None and ip == NODO_CHORD.ip:
        return "127.0.0.1"
    return ip


def rpc_call(ip, porta, payload):
    #chiamata rpc sincrona verso un nodo remoto
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5.0)
    try:
        sock.connect((resolve_connect_host(ip), porta))
        send_json(sock, payload)
        risposta = sock.makefile("r", encoding="utf-8").readline()
        return json.loads(risposta) if risposta else None
    finally:
        sock.close()


def rpc_find_successor(ip, porta, key, self_ref=None):
    #cerchiamo il successore per una chiave dell'anello chord 
    for _ in range(30):
        try:
            if self_ref and ip == self_ref["ip"] and porta == self_ref["porta"]:
                with CHORD_LOCK:
                    node, found = NODO_CHORD.find_successor(key)
                if found:
                    return node
                ip, porta = node["ip"], node["porta"]
                continue
            r = rpc_call(ip, porta, {"type": "FIND_SUCCESSOR", "key": key})
            if r is None:
                return None
            if r.get("found"):
                return r["node"]
            ip, porta = r["node"]["ip"], r["node"]["porta"]
        except Exception as e:
            print(f"[RPC] find_successor fallito per {ip}:{porta}: {e}")
            return None
    return None


def rpc_is_alive(ip, porta):#verifica se un nodo è attivo tramite BEAT
    try:
        r = rpc_call(ip, porta, {"type": "BEAT", "ip": ip, "porta": porta})
        return r is not None and r.get("status") == "OK"
    except Exception:
        return False


def is_self_node(node, self_ref):
    return node and node.get("ip") == self_ref["ip"] and node.get("porta") == self_ref["porta"]


def is_reachable_node(node, self_ref):
    if not node:
        return False
    if is_self_node(node, self_ref):
        return True
    return rpc_is_alive(node["ip"], node["porta"])


def print_ring_structure():
    """Percorre l'intero anello per stampare la topologia."""
    with CHORD_LOCK:
        if not NODO_CHORD:
            return
        self_ref = NODO_CHORD.ref() #informazioni sul nodo corrente
        current = NODO_CHORD.successor #successore
        
    ring = [str(self_ref["id"])]
    visited = {self_ref["id"]}
    
    for _ in range(32):
        if not current or current["id"] == self_ref["id"]:
            break
        ring.append(str(current["id"]))
        if current["id"] in visited:
            ring[-1] += " (loop)"
            break
        visited.add(current["id"])
        
        try:
            r = rpc_call(
            current["ip"],
            current["porta"],
            {"type": "GET_SUCCESSOR_LIST"}
            )

            if r and r.get("successor_list"):
                current = r["successor_list"][0]
            else:
                ring.append("(interrotto)")
                break

        except OSError:
            ring.append(f"{current['id']} (non raggiungibile)")
            break

        except Exception as e:
            ring.append(f"(errore: {e})")
            break

    if ring[-1] != "(interrotto)" and not ring[-1].endswith("(loop)"):
        ring.append(str(self_ref["id"]))
        
    print(f"[Struttura Anello] {' --> '.join(ring)}\n")


# Stabilizzazione periodica 

def stabilization_loop():
    while True:
        time.sleep(5)
        if NODO_CHORD is None:
            continue
        try:
            with CHORD_LOCK:
                succ = NODO_CHORD.successor
                self_ref = NODO_CHORD.ref()

            # Verifica che il successore sia vivo
            if not is_self_node(succ, self_ref) and not rpc_is_alive(succ["ip"], succ["porta"]):
                print(f"[Stabilize] Il successore {succ['id']} ({succ['ip']}:{succ['porta']}) non risponde al BEAT.")
                raise OSError("Successore irraggiungibile")

            # Chiedi al successore chi è il suo predecessore e la sua lista successori
            if is_self_node(succ, self_ref):
                with CHORD_LOCK:
                    pred_of_succ = NODO_CHORD.predecessor
                    sl = list(NODO_CHORD.successor_list)
            else:
                resp_pred = rpc_call(succ["ip"], succ["porta"], {"type": "GET_PREDECESSOR"})
                if resp_pred is None:
                    print(f"[Stabilize] Fallito GET_PREDECESSOR verso {succ['id']}")
                    raise OSError("Successore non risponde a GET_PREDECESSOR")
                pred_of_succ = resp_pred.get("predecessor")

                resp_sl = rpc_call(succ["ip"], succ["porta"], {"type": "GET_SUCCESSOR_LIST"})
                sl = resp_sl.get("successor_list", []) if resp_sl else []

            if pred_of_succ and not is_reachable_node(pred_of_succ, self_ref):
                pred_of_succ = None

            with CHORD_LOCK: 
                if NODO_CHORD.stabilize(pred_of_succ, sl):# aggiornamento del nodo con il succ. e predecessore
                    print(f"[Stabilize] Successore aggiornato a {NODO_CHORD.successor['id']}")
                succ_attuale = NODO_CHORD.successor
                pred_attuale = NODO_CHORD.predecessor
                sl_attuale = list(NODO_CHORD.successor_list)

            print(f"\n[Stato Nodo {self_ref['id']}] Pred: {pred_attuale['id'] if pred_attuale else 'Nessuno'} | Succ: {succ_attuale['id']}")
            print(f"[Stato Nodo {self_ref['id']}] Lista Successori: {[n['id'] for n in sl_attuale]}")
            threading.Thread(target=print_ring_structure, daemon=True).start()

            # Notifica il successore se il nodo locale non è se stesso
            if not is_self_node(succ_attuale, self_ref):
                rpc_call(succ_attuale["ip"], succ_attuale["porta"], {"type": "NOTIFY", "node": self_ref})

            # Pulisci la finger table dai nodi morti
            fingers_to_check = set()
            with CHORD_LOCK:
                for f in NODO_CHORD.finger:
                    if f and not is_self_node(f, self_ref) and f["id"] != succ_attuale["id"]:
                        fingers_to_check.add((f["ip"], f["porta"], f["id"]))
            
            dead_fingers = set()
            for ip, porta, fid in fingers_to_check:
                if not rpc_is_alive(ip, porta):
                    print(f"[Stabilize] Rimosso dito morto dalla finger table: {fid} ({ip}:{porta})")
                    dead_fingers.add(fid)
                    
            if dead_fingers:
                with CHORD_LOCK:
                    for i in range(NODO_CHORD.m):
                        if NODO_CHORD.finger[i] and NODO_CHORD.finger[i]["id"] in dead_fingers:
                            NODO_CHORD.finger[i] = None

            # Aggiornamento dei nodi della finger table periodicamente 
            with CHORD_LOCK:
                i = random.randint(0, NODO_CHORD.m - 1)
                start = (NODO_CHORD.id + 2**i) % (2**NODO_CHORD.m)
                sf, is_final = NODO_CHORD.find_successor(start)

            if is_final:
                with CHORD_LOCK:
                    NODO_CHORD.finger[i] = sf
            elif sf:
                result = rpc_find_successor(sf["ip"], sf["porta"], start, self_ref)
                if result:
                    with CHORD_LOCK:
                        NODO_CHORD.finger[i] = result

            #  verifico il predecsione locale, se non risponde lo azzero ( none)
            with CHORD_LOCK:
                pred = NODO_CHORD.predecessor
            if pred and not is_self_node(pred, self_ref):
                if not rpc_is_alive(pred["ip"], pred["porta"]):
                    print(f"[Stabilize] Predecessore {pred['id']} ({pred['ip']}:{pred['porta']}) non risponde. Azzero.")
                    with CHORD_LOCK:
                        NODO_CHORD.predecessor = None

        except OSError:
            print(f"[Stabilize] Rimuovo successore morto {succ['id']}")
            with CHORD_LOCK:
                if NODO_CHORD.remove_successor():
                    print(f"[Stabilize] Promosso nuovo successore: {NODO_CHORD.successor['id']}")
                else:
                    print(f"[Stabilize] Nessun altro successore disponibile nella lista. Rimango solo.")
        except Exception as e:
            print(f"[Stabilize] Errore inaspettato: {e}")


import random  # per fix_fingers

#trva le repliche per l'esecuzione di task ridondante 
def trova_repliche(k=3):
    with CHORD_LOCK:
        self_ref = NODO_CHORD.ref()
        return [dict(n) for n in NODO_CHORD.successor_list
                if not is_self_node(n, self_ref)][:k-1] #info dei primi k-1 nodi successori


def inoltra_task(client_socket, request, ip_hop, porta_hop, retry=3):#con gestione di guasti 
    """Inoltra il task al prossimo hop e fa relay delle risposte."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(15.0)
        sock.connect((resolve_connect_host(ip_hop), porta_hop))
        send_json(sock, request)
        settled = False
        for linea in sock.makefile('r', encoding='utf-8'): #lettura della risposta riga per riga 
            risposta = json.loads(linea)
            send_json(client_socket, risposta) #inoltrso la risposta al client
            if risposta.get("status") == "SETTLED":#terminato e risultato pronto
                settled = True
                break
        sock.close() 
        if not settled:
            raise OSError("Connessione chiusa prematuramente senza terminare il task correttamenrte")
    except OSError:#se non risponde o cade nel mentre
        task_id = request.get("task_id", "Unknown")
        if retry > 0:
            print(f"[Routing] Fallito inoltro a {ip_hop}:{porta_hop}, retry...")
            with CHORD_LOCK:
                if NODO_CHORD.successor["ip"] == ip_hop and NODO_CHORD.successor["porta"] == porta_hop:
                    NODO_CHORD.remove_successor() #rimuovo il nodo irraggiungibile
                next_node, _ = NODO_CHORD.find_successor(request.get("task_hash"))#nuova ricerca 
            if next_node and next_node["id"] != NODO_CHORD.id:
                inoltra_task(client_socket, request, next_node["ip"], next_node["porta"], retry - 1) #provo per 3 volte max 
            else:
                send_json(client_socket, {"status": "SETTLED", "task_id": task_id,
                                          "result": "Errore: nodo irraggiungibile"})
        else:
            send_json(client_socket, {"status": "SETTLED", "task_id": task_id,
                                      "result": "Errore: nodo irraggiungibile dopo 3 tentativi"})
    except Exception as e:
        send_json(client_socket, {"status": "SETTLED", "task_id": request.get("task_id", "Unknown"),
                                  "result": f"Errore nel routing: {e}"})


def contatta_replica(ip, porta, request, risultati, lock): #thread contata un nodo di replica e gli chiede eseguire il task
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(45.0)
        sock.connect((resolve_connect_host(ip), porta))
        send_json(sock, request)
        for linea in sock.makefile('r', encoding='utf-8'):
            r = json.loads(linea)
            if r.get("status") == "SETTLED":
                with lock:
                    risultati.append(r.get("result"))
                break
        sock.close()
    except Exception as e:
        print(f"[Coordinatore] Errore replica {ip}:{porta} → {e}")


def propaga_cache(code_hash, risultato, repliche, entry_point): #propagazione del risultato coerente alle repliche e all'entry point in maniera asncrona
    destinatari = list(repliche)
    if entry_point:
        with CHORD_LOCK:
            my_id = NODO_CHORD.id
        if entry_point["id"] != my_id: #aggiungo il nodo iniziale a cui si era arrivati ( entry_point) al liste di destinatari 
            destinatari.append({"ip": entry_point["ip"], "porta": entry_point["porta"]})

    msg = {"type": "CACHE_STORE", "code_hash": code_hash, "result": risultato}
    for dest in destinatari:
        def invia(ip=dest["ip"], porta=dest["porta"]):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3.0)
                s.connect((resolve_connect_host(ip), porta))
                send_json(s, msg)
                s.close()
            except Exception:
                pass
        threading.Thread(target=invia, daemon=True).start() #thread che esegue la funzione invia in background chachestore


def esegui_python_locale(task_id, payload_code):
    filepath = None
    try:
        work_dir = writable_task_dir()
        fd, filepath = tempfile.mkstemp(prefix=f"{task_id}_", suffix=".py", dir=work_dir, text=True)
        with os.fdopen(fd, "w") as f:
            f.write(payload_code)
        r = subprocess.run( #stesso interorete corrente 
            [sys.executable, filepath],
            capture_output=True,
            text=True,
            timeout=TASK_TIMEOUT,
            cwd=work_dir,
        )
        if r.returncode == 0:
            return r.stdout.strip()
        return f"Runtime Error:\n{r.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "Errore: Limite di tempo massimo superato (Possibile loop infinito)."
    except Exception as e:
        return f"Errore interno Worker: {e}"
    finally:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)


def esegui_sandbox_docker(task_id, payload_code):
#sandbox isolata per la sicurezza 
    tid = threading.get_ident()
    filepath_local = os.path.join(SHARED_TASKS_LOCAL, f"task_{tid}.py")
    filepath_host = os.path.join(SHARED_TASKS_HOST, f"task_{tid}.py")
    container_name = f"edgerev_sandbox_{tid}"
    try:
        with open(filepath_local, "w") as f:
            f.write(payload_code)
        r = subprocess.run(
            ["docker", "run", "--rm", "--name", container_name,
             "-m", "500m", "--cpus", "0.5", "--network", "none",
             "-v", f"{filepath_host}:/app/task.py", "edgerev-sandbox"], #parametri per limitare container e script interno  
            capture_output=True, text=True, timeout=TASK_TIMEOUT)
        return r.stdout.strip() if r.returncode == 0 else f"Runtime Error nella Sandbox:\n{r.stderr.strip()}"
    except subprocess.TimeoutExpired:
        subprocess.run(["docker", "kill", container_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return "Errore: Limite di tempo massimo superato (Possibile loop infinito)."
    except Exception as e:
        return f"Errore interno Worker: {e}"
    finally:
        if os.path.exists(filepath_local):
            os.remove(filepath_local)


def esegui_sandbox(task_id, payload_code): # a seconda della configurazione o usa locale o docker
    if EXECUTOR == "local":
        return esegui_python_locale(task_id, payload_code)
    return esegui_sandbox_docker(task_id, payload_code)


def gestisci_task_con_routing(client_socket, client_address, request):#calcola hash se il task non lo ha 
    task_id = request.get("task_id", "Unknown")
    task_hash = request.get("task_hash")

    # Primo hop: calcoliamo hash dal codice
    if task_hash is None:
        with CHORD_LOCK:
            m = NODO_CHORD.m
        code = request.get("code", "")
        code_hash_hex = hashlib.sha1(code.encode()).hexdigest()
        task_hash = int(code_hash_hex, 16) % (2**m)
        request.update({"task_hash": task_hash, "code_hash": code_hash_hex, "type": "ROUTE"})
        with CHORD_LOCK:
            request["entry_point"] = NODO_CHORD.ref() #memorizziamo il nodo corrente come entry point 

    print(f"[Routing] Task '{task_id}' (hash={task_hash}) da {client_address}")

    with CHORD_LOCK:
        responsabile = NODO_CHORD.is_responsible(task_hash) #interroga se stesso per capire se è il responsabnile 

    if responsabile: #se sono il responsabile del task
        ##se ho già l'hash  ed è presente nalla cache lo restituisco al client 
        code_hash = request.get("code_hash")
        if code_hash:
            with TASK_CACHE_LOCK:
                cached = TASK_CACHE.get(code_hash)
            if cached is not None:
                print(f"[Cache] HIT code_hash={code_hash[:8]}...")
                send_json(client_socket, {"status": "SETTLED", "task_id": task_id, "result": cached, "cache_hit": True})
                client_socket.close()
                return
        ## se non ho l'hash devo eseguire il task in locale e poi lo propago alle repliche
        print(f"[Routing] Responsabile (ID={NODO_CHORD.id}). Coordinamento replicazione.")
        repliche_candidate = trova_repliche(k=3)
        with CHORD_LOCK:
            self_ref = NODO_CHORD.ref()
        repliche = []
        for rep in repliche_candidate:
            if is_reachable_node(rep, self_ref):
                repliche.append(rep)
            else:
                print(f"[Coordinatore] Replica non raggiungibile, esclusa dal quorum → {rep['ip']}:{rep['porta']}")

        risultati, lock, threads = [], threading.Lock(), []
        #adeeso il nodo si comporta come coordinatore 
        ##esegue il task in locale 
        ##contatta le repliche candidate per la replicazione (con thread)
        def esecuzione_locale():
            risultato = esegui_sandbox(task_id, request.get("code", ""))
            with lock:
                risultati.append(risultato)

        t = threading.Thread(target=esecuzione_locale)
        threads.append(t)
        t.start()

        req_replica = {**request, "type": "REPLICA_EXEC"}
        for rep in repliche:
            print(f"[Coordinatore] Replica → {rep['ip']}:{rep['porta']}")
            t = threading.Thread(target=contatta_replica, args=(rep['ip'], rep['porta'], req_replica, risultati, lock))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        totale = len(repliche) + 1
        maggioranza = (totale // 2) + 1 #qourum 
        print(f"[Coordinatore] Risposte: {len(risultati)}/{totale}")

        risultati_validi = [str(r) for r in risultati if is_risultato_valido(str(r))]
        if len(risultati_validi) >= maggioranza:
            risultato_finale, consenso = Counter(risultati_validi).most_common(1)[0]
            if consenso < maggioranza:
                risultato_finale = "Errore: Quorum di risultati uguali non raggiunto."

            if code_hash and is_risultato_valido(risultato_finale): #se ho l'hash e il risultato è valido lo salvo nella cache
                with TASK_CACHE_LOCK:
                    TASK_CACHE[code_hash] = risultato_finale
                print(f"[Cache] Salvato code_hash={code_hash[:8]}...")
                propaga_cache(code_hash, risultato_finale, repliche, request.get("entry_point"))#propragazione in background 
            elif risultato_finale:
                print(f"[Cache] NON cachato (errore): {risultato_finale[:60]}")

            send_json(client_socket, {"status": "SETTLED", "task_id": task_id, "result": risultato_finale})
        else:
            send_json(client_socket, {"status": "SETTLED", "task_id": task_id,
                                      "result": "Errore: Quorum di risultati validi non raggiunto."})
        client_socket.close()
    else:
       #se non è il responsabile delega al nodo più vicino seguendo la hash table 
        with CHORD_LOCK:
            prossimo, _ = NODO_CHORD.find_successor(task_hash)
        if prossimo:
            print(f"[Routing] Inoltro a nodo {prossimo['id']} ({prossimo['ip']}:{prossimo['porta']})")
            inoltra_task(client_socket, request, prossimo["ip"], prossimo["porta"])
        else:
            send_json(client_socket, {"status": "SETTLED", "task_id": task_id,
                                      "result": "Errore: nodo responsabile non trovato"})
        client_socket.close()

def registra_nodo_nella_rete(ip_annuncio, porta, seed_peers): #join all'anello 
    global NODO_CHORD
    NODO_CHORD = ChordNode(ip_annuncio, porta, m=8)
    print(f"[Chord] Nodo creato: ID={NODO_CHORD.id} ({ip_annuncio}:{porta})")

    if not seed_peers: #se non ci sono si nodi di avvio primo in assoluto 
        NODO_CHORD.join(None)
        print("[Chord] Primo nodo nell'anello.")
        return
#altrimenti se ci sono altri seed prova a join in modo sequenziale per capire chi sono i successori 
    require_seed = os.environ.get("SDEP_REQUIRE_SEED", "0").lower() in ("1", "true", "yes")
    while True:
        for ip_seed, porta_seed in seed_peers:
            for tentativo in range(1, 6):
                try:
                    successore = rpc_find_successor(ip_seed, porta_seed, NODO_CHORD.id)
                    if successore:
                        NODO_CHORD.join(successore) #join alla rete una volta trovato il successore 
                        print(f"[Chord] Join completato. Successore: {successore['id']}")
                        return
                except Exception as e:
                    print(f"[Chord] Seed {ip_seed}:{porta_seed} (tentativo {tentativo}/5): {e}")
                if tentativo < 5:
                    time.sleep(2)

        if not require_seed:
            break
        print("[Chord] Seed non raggiungibile. Riprovo invece di avviare un anello separato.")
        time.sleep(5)

    print("[Chord] Nessun seed raggiungibile. Avvio come primo nodo.")
    NODO_CHORD.join(None) #se dopo 5 secondi non trova un seed diventa il primo nodo di un nuovo anello 


def connection_handler(client_socket, client_address): #per ogni singola connessione in arrivo smista in base al tipo di richiesta 
    try:
        client_socket.settimeout(5.0)
        raw_request = client_socket.makefile("r", encoding="utf-8").readline().strip()
        if not raw_request: #se non c'è la richiesta chiudo la connessione 
            client_socket.close()
            return
        request = json.loads(raw_request)
        tipo = request.get("type", "TASK")

        # Handler Chord semplici (request-response)
        if tipo == "FIND_SUCCESSOR":
            with CHORD_LOCK:
                nodo, found = NODO_CHORD.find_successor(request["key"]) #nodo resposnsanile di una determianta chiave
            send_json(client_socket, {"status": "OK", "node": nodo, "found": found})
        elif tipo == "GET_PREDECESSOR":
            with CHORD_LOCK:
                send_json(client_socket, {"status": "OK", "predecessor": NODO_CHORD.predecessor})
        elif tipo == "GET_SUCCESSOR":
            with CHORD_LOCK:
                send_json(client_socket, {"status": "OK", "successor": NODO_CHORD.successor})
        elif tipo == "GET_SUCCESSOR_LIST": 
            with CHORD_LOCK:
                send_json(client_socket, {"status": "OK", "successor_list": list(NODO_CHORD.successor_list)})
        elif tipo == "NOTIFY": #notifica sa un nodo che si propone come nuovo predecessione
            with CHORD_LOCK:
                aggiornato = NODO_CHORD.notify(request["node"])
            if aggiornato:
                print(f"[Chord] Predecessore aggiornato a {request['node']['id']}")
            send_json(client_socket, {"status": "OK"})
        elif tipo == "BEAT": #funziona come keepalive per ilstabilizzatore 
            send_json(client_socket, {"status": "OK"})
        elif tipo == "GET_RING": #lista ordinata di tutti i nodi attivi nel chord
            with CHORD_LOCK:
                self_ref = NODO_CHORD.ref()
                current = NODO_CHORD.successor
            nodes, visited = [self_ref], {self_ref["id"]}
            while current and current["id"] not in visited:
                visited.add(current["id"])
                nodes.append(current)
                try:
                    r = rpc_call(current["ip"], current["porta"], {"type": "GET_SUCCESSOR"})
                    current = r.get("successor") if r else None
                except Exception:
                    break
            send_json(client_socket, {"status": "OK", "nodes": nodes})
        elif tipo == "CACHE_STORE": #propagazione asincrona ( memorizza nella cache locale un risultato di un altro nodo )
            code_hash, result = request.get("code_hash"), request.get("result")
            if code_hash and is_risultato_valido(result):
                with TASK_CACHE_LOCK:
                    TASK_CACHE[code_hash] = result
                print(f"[Cache] Salvato code_hash={code_hash[:8]}... (propagazione)")
            send_json(client_socket, {"status": "OK"})
        elif tipo == "TASK_QUERY": #controlla se la cache locale contiene un risultato di un task identificato da code-hash
            code_hash = request.get("code_hash")
            with TASK_CACHE_LOCK:
                risultato = TASK_CACHE.get(code_hash) if code_hash else None
            if risultato is not None:
                print(f"[Cache] HIT code_hash={code_hash[:8]}.")
                send_json(client_socket, {"status": "FOUND", "task_id": request.get("task_id"), "result": risultato})
            else:
                send_json(client_socket, {"status": "NOT_FOUND", "task_id": request.get("task_id")})
        elif tipo == "REPLICA_EXEC": #messaggio da un coordinatore alla replica per eseguire il task in una sandbox
            task_id = request.get("task_id", "Unknown")
            risultato = esegui_sandbox(task_id, request.get("code", ""))
            send_json(client_socket, {"status": "SETTLED", "task_id": task_id, "result": risultato})
        elif tipo in ("ROUTE", "TASK"): #routing del task tramite chord
            gestisci_task_con_routing(client_socket, client_address, request)
            return  # chiusura dei socket con la funzione chiamata sopra 
        else:
            send_json(client_socket, {"status": "ERROR", "message": f"Tipo sconosciuto: {tipo}"})

        client_socket.close()
    except json.JSONDecodeError as e:
        print(f"Richiesta JSON non valida da {client_address}: {e}")
        client_socket.close()
    except Exception as e:
        print(f"Errore connessione da {client_address}: {e}")
        client_socket.close()


def parse_args(): #parsing degli argomenti 
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else PORT #valore di default 5005
    ip_annuncio = "127.0.0.1"
    porta_annuncio = int(os.environ.get("SDEP_ANNOUNCE_PORT", porta)) #se non definita su Sdep_announce la porta di annuncio è quella locale
    seed_peers = []
    for arg in sys.argv[2:]:
        if ":" in arg:
            h, p = arg.rsplit(":", 1)
            seed_peers.append((h, int(p)))
        else:
            ip_annuncio = arg
    ip_annuncio = os.environ.get("SDEP_ANNOUNCE_HOST", ip_annuncio)
    return porta, ip_annuncio, porta_annuncio, seed_peers


def dispatcher_server(): #avvio dei servizi del dispatcher 
    threading.current_thread().name = "Dispatcher-Main"
    porta, ip_annuncio, porta_annuncio, seed_peers = parse_args() #prende gli argomenti specificati 
    registra_nodo_nella_rete(ip_annuncio, porta_annuncio, seed_peers) #processo di registrazione alla rete 

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #crea socket tcp 
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #riutilizza indirizzo 
    try: 
        server.bind((HOST, porta)) #porta selta 
        server.listen(5) #max 5 connessioni in attesa 
        print(f"[Dispatcher-Main] Server in ascolto sulla porta {porta} (annuncio: {ip_annuncio}:{porta_annuncio})...")
        threading.Thread(target=stabilization_loop, daemon=True, name="Stabilize").start() #inizia il ciclo di stabilizzazione in background 
        while True: #accetta connessioni in arrivo 
            cs, ca = server.accept()
            threading.Thread(target=connection_handler, args=(cs, ca), name=f"H-{ca[1]}").start() #avvia un thread per ogni connessione 
    except KeyboardInterrupt:
        print("[Dispatcher-Main] Spegnimento.")
    finally:
        server.close()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda *_: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    dispatcher_server()
