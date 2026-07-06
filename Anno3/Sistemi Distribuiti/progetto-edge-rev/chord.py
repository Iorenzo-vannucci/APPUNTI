import hashlib


class ChordNode:

    def __init__(self, ip, porta, m=160, r=3):
        self.ip = ip
        self.porta = porta
        self.m = m
        self.r = r
        self.id = int(hashlib.sha1(f"{ip}:{porta}".encode()).hexdigest(), 16) % (2**m)
        self.finger = [None] * m
        self.successor_list = [self.ref()]
        self.predecessor = None

    @property
    def successor(self):
        return self.successor_list[0] if self.successor_list else self.ref()

    def ref(self):
        return {"ip": self.ip, "porta": self.porta, "id": self.id}

    # Controlla se val è nell'intervallo (lo, hi] (inclusivo) o (lo, hi) (escluso) con wrap-around
    def _in_range(self, val, lo, hi, inclusivo=True):
        if lo == hi:
            return True if inclusivo else val != lo
        if inclusivo:
            return (lo < val <= hi) if lo < hi else (val > lo or val <= hi)
        return (lo < val < hi) if lo < hi else (val > lo or val < hi)

    def is_responsible(self, key) -> bool:
        if self.predecessor is None:
            return True
        return self._in_range(key, self.predecessor["id"], self.id)
    
    # Trova il successore di key #restituisce il nodo a cui devo andare per avvicinarmi alla chiave
    def find_successor(self, key):
        if self._in_range(key, self.id, self.successor["id"]):
            return self.successor, True
        n_prime = self.closest_preceding_node(key)
        if n_prime["id"] == self.id:
            return self.successor, True
        return n_prime, False

    def closest_preceding_node(self, key): #scorre la fingher table
        for i in range(self.m - 1, -1, -1):#salto più lungo possibile che rimanga prima della chiave
            f = self.finger[i]
            if f and self._in_range(f["id"], self.id, key, inclusivo=False):
                return f
        return self.ref()

    def join(self, successor_ref=None):
        if successor_ref is None:
            self.successor_list = [self.ref()]
            self.predecessor = self.ref()
            self.finger = [self.ref()] * self.m
        else:
            self.successor_list = [successor_ref]
            self.predecessor = None
            self.finger[0] = successor_ref
    # Funzione eseguita periodicamente dal thread stabilizzatore per mantenere la struttura dell'anello aggiornata.
    def stabilize(self, successor_predecessor, successor_successor_list=None):
        x = successor_predecessor
        cambiato = False
        if x and x["id"] != self.id: # Non sono piu' il predecessore del mio successore, devo aggiornare la lista successori e la finger table
            if self._in_range(x["id"], self.id, self.successor["id"], inclusivo=False):
                self.successor_list = [x] + self.successor_list
                self.finger[0] = x
                cambiato = True
        # Dopo aver aggiunto il nuovo successore, aggiorno la lista dei successori rimuovendo l'ultimo elemento se la lunghezza supera r
        if successor_successor_list:
            new_list = [self.successor]
            for s in successor_successor_list:
                if s["id"] not in [n["id"] for n in new_list]:
                    new_list.append(s)
            self.successor_list = new_list[:self.r]
        return cambiato

    def remove_successor(self):
        if len(self.successor_list) > 1:
            self.successor_list.pop(0)
            self.finger[0] = self.successor_list[0]
            return True
        return False
    # Funzione eseguita periodicamente dal thread stabilizzatore per notificare al successore che si e' diventati suo predecessore
    def notify(self, n_prime_ref):
        if self.predecessor is None or self._in_range(
                n_prime_ref["id"], self.predecessor["id"], self.id, inclusivo=False):
            self.predecessor = n_prime_ref
            return True
        return False
