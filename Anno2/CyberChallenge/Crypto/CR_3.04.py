#!/usr/bin/env python3
import socket

def find_lcg_parameters(values):
    """Trova i parametri LCG a partire da una sequenza di valori"""
    
    # Assumiamo n = 2^31 - 1 (numero primo di Mersenne, valore comune per LCG)
    n = 2147483647  # 2^31 - 1
    
    # Verifichiamo altre opzioni comuni di n
    potential_n_values = [
        2147483647,  # 2^31 - 1
        4294967295,  # 2^32 - 1
        4294967296,  # 2^32
    ]
    
    for n in potential_n_values:
        try:
            # Calcoliamo m usando i primi 3 valori
            diff_v = (values[1] - values[0]) % n
            diff_next = (values[2] - values[1]) % n
            
            # Verifichiamo che diff_v abbia un inverso moltiplicativo modulo n
            # Necessario solo se n non è primo
            gcd = lambda a, b: a if b == 0 else gcd(b, a % b)
            if gcd(diff_v, n) != 1:
                continue
                
            m = (diff_next * pow(diff_v, -1, n)) % n
            
            # Calcoliamo c
            c = (values[1] - (m * values[0]) % n) % n
            
            # Verifichiamo che i parametri trovati generino i valori successivi
            valid = True
            for i in range(len(values) - 1):
                if (m * values[i] + c) % n != values[i + 1]:
                    valid = False
                    break
                    
            if valid:
                return m, c, n
        except:
            continue
    
    # Se arriviamo qui, non abbiamo trovato parametri validi
    # Proviamo con l'approccio più generico per il sistema modulare
    n = 2147483647  # Riprova con il valore più probabile
    
    # Calcola m e c usando i primi 3 valori
    diff_v = (values[1] - values[0]) % n
    diff_next = (values[2] - values[1]) % n
    m = (diff_next * pow(diff_v, -1, n)) % n
    c = (values[1] - (m * values[0]) % n) % n
    
    return m, c, n

def try_multiple_combinations(values):
    """Prova diverse combinazioni di trasformazioni per LCG"""
    result = []
    
    # Parametri di base
    m, c, n = find_lcg_parameters(values)
    
    # Verifica l'accuratezza
    valid = True
    for i in range(len(values) - 1):
        if (m * values[i] + c) % n != values[i + 1]:
            valid = False
            break
    
    print(f"Parametri base: m = {m}, c = {c}, n = {n}")
    print(f"Accuratezza: {'Validi' if valid else 'Non validi'}")
    
    # Lista di possibili trasformazioni
    transformations = [
        ("identity", lambda x: x),
        ("complement", lambda x: (~x) & 0xFFFFFFFF),
        ("reverse_bits", lambda x: int(format(x, '032b')[::-1], 2)),
        ("negate", lambda x: (-x) % n),
        ("rotate_left_13", lambda x: ((x << 13) | (x >> (32-13))) & 0xFFFFFFFF),
        ("rotate_right_13", lambda x: ((x >> 13) | (x << (32-13))) & 0xFFFFFFFF),
        ("xor_self_shift", lambda x: x ^ (x >> 13)),
        ("byte_swap", lambda x: ((x & 0xFF) << 24) | ((x & 0xFF00) << 8) | ((x & 0xFF0000) >> 8) | ((x >> 24) & 0xFF)),
    ]
    
    # Genera tutti i possibili valori
    next_value = values[-1]
    
    # Genera predizioni per il prossimo valore usando diverse trasformazioni
    for name, transform in transformations:
        raw_next = (m * next_value + c) % n
        transformed = transform(raw_next)
        result.append((name, transformed))
        print(f"Predizione {name}: {transformed}")
    
    # Aggiungi altri schemi comuni di generatori PRNG
    # XORshift
    x = next_value
    x ^= (x << 13) & 0xFFFFFFFF
    x ^= (x >> 17) & 0xFFFFFFFF
    x ^= (x << 5) & 0xFFFFFFFF
    result.append(("xorshift", x))
    print(f"Predizione xorshift: {x}")
    
    # Mersenne Twister style (semplificato)
    mt_next = (1812433253 * (next_value ^ (next_value >> 30)) + 1) & 0xFFFFFFFF
    result.append(("mersenne_twister", mt_next))
    print(f"Predizione mersenne_twister: {mt_next}")
    
    # Add Xor (come PCG generators)
    pcg_next = ((next_value * 6364136223846793005 + 1442695040888963407) & 0xFFFFFFFF)
    pcg_next = ((pcg_next >> ((pcg_next >> 28) + 4)) ^ pcg_next) & 0xFFFFFFFF
    result.append(("pcg", pcg_next))
    print(f"Predizione PCG: {pcg_next}")
    
    return result, m, c, n

def main():
    # Valori noti
    values = [
        1180552760,
        1346555300,
        1257227113,
        2122109152,
        1619023512,
        1664547291,
        394287731
    ]
    
    # Prova diverse combinazioni
    combinations, m, c, n = try_multiple_combinations(values)
    
    # Connessione al servizio
    host = "gtn4.challs.cyberchallenge.it"
    port = 9063
    
    # Funzione per testare una sequenza
    def test_sequence(name, sequence):
        print(f"\nTest sequenza: {name}")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        
        # Leggi l'output iniziale
        while True:
            data = sock.recv(1024)
            if b"v[7] =" in data:
                break
        
        # Invia i primi 5 valori
        for i, val in enumerate(sequence[:5]):
            sock.send(f"{val}\n".encode())
            response = sock.recv(1024)
            
            if b"flag" in response.lower():
                print(f"Successo! Flag ottenuta con {name}:")
                print(response.decode())
                sock.close()
                return True
            
            if b"sorry" in response.lower() or b"harder" in response.lower():
                print(f"Sequenza fallita dopo {i+1} valori")
                sock.close()
                return False
        
        # Se arriviamo qui, continuiamo con il resto dei valori
        for i, val in enumerate(sequence[5:]):
            sock.send(f"{val}\n".encode())
            response = sock.recv(1024)
            
            if b"flag" in response.lower():
                print(f"Successo! Flag ottenuta con {name} dopo {i+6} valori:")
                print(response.decode())
                sock.close()
                return True
            
            if b"sorry" in response.lower() or b"harder" in response.lower():
                print(f"Sequenza fallita dopo {i+6} valori")
                sock.close()
                return False
        
        print(f"Fine della sequenza {name}")
        sock.close()
        return False
    
    # Test con approccio LCG standard
    standard_next_value = values[-1]
    standard_sequence = []
    
    for i in range(50):
        standard_next_value = (m * standard_next_value + c) % n
        standard_sequence.append(standard_next_value)
    
    if test_sequence("LCG Standard", standard_sequence):
        return
    
    # Prova altre trasformazioni
    for name, first_value in combinations:
        modified_sequence = [first_value]
        next_value = first_value
        
        # Funzione di trasformazione corrispondente al nome
        transform = next(tr for nm, tr in [t for t in [
            ("identity", lambda x: x),
            ("complement", lambda x: (~x) & 0xFFFFFFFF),
            ("reverse_bits", lambda x: int(format(x, '032b')[::-1], 2)),
            ("negate", lambda x: (-x) % n),
            ("rotate_left_13", lambda x: ((x << 13) | (x >> (32-13))) & 0xFFFFFFFF),
            ("rotate_right_13", lambda x: ((x >> 13) | (x << (32-13))) & 0xFFFFFFFF),
            ("xor_self_shift", lambda x: x ^ (x >> 13)),
            ("byte_swap", lambda x: ((x & 0xFF) << 24) | ((x & 0xFF00) << 8) | ((x & 0xFF0000) >> 8) | ((x >> 24) & 0xFF)),
            ("xorshift", lambda x: (lambda y: (lambda z: z ^ ((z << 5) & 0xFFFFFFFF))(y ^ ((y >> 17) & 0xFFFFFFFF)))(x ^ ((x << 13) & 0xFFFFFFFF))),
            ("mersenne_twister", lambda x: (1812433253 * (x ^ (x >> 30)) + 1) & 0xFFFFFFFF),
            ("pcg", lambda x: (lambda pcg_val: ((pcg_val >> ((pcg_val >> 28) + 4)) ^ pcg_val) & 0xFFFFFFFF)((x * 6364136223846793005 + 1442695040888963407) & 0xFFFFFFFF))
        ]] if nm == name)
        
        # Genera 49 valori aggiuntivi con la trasformazione specificata
        for i in range(49):
            raw_next = (m * next_value + c) % n
            next_value = transform(raw_next)
            modified_sequence.append(next_value)
        
        if test_sequence(f"LCG con {name}", modified_sequence):
            return
    
    # Test con inverso di complemento a due (-x)
    inverse_sequence = []
    inverse_value = values[-1]
    
    for i in range(50):
        raw_next = (m * inverse_value + c) % n
        inverse_value = (2**32 - raw_next) % (2**32)  # Complemento a due
        inverse_sequence.append(inverse_value)
    
    test_sequence("LCG con complemento a due", inverse_sequence)
    
    # Prova con 2^32 - 1 come modulo alternativo
    alt_n = 4294967295  # 2^32 - 1
    alt_next_value = values[-1]
    alt_sequence = []
    
    for i in range(50):
        alt_next_value = (m * alt_next_value + c) % alt_n
        alt_sequence.append(alt_next_value)
    
    test_sequence("LCG con modulo 2^32-1", alt_sequence)
    
    print("Fine dei test")

if __name__ == "__main__":
    main()