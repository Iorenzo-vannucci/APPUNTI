def calcolo_tempo(N, M, tempo_blocco, ritardo, minuti_invio):
    tempo_tot = 0
    
    for tempoDiInvio in minuti_invio:
        tempo = tempoDiInvio
        
        
        for i in range(N):
            t = tempo_blocco[i]  
            f = ritardo[i]  
            if tempo % t != 0:
                tempo = (tempo // t + 1) * t
            tempo += f
        
        tempo_tot += tempo
    
    return tempo_tot

with open('/Users/lorenzovannucci/Downloads/2025-emails_emails-3_1738080663.txt', 'r') as file:
    # Prima riga
    N, M = map(int, file.readline().split())
    
    # Seconda riga
    tempo_blocco = list(map(int, file.readline().split()))
    
    # Terza riga
    ritardo = list(map(int, file.readline().split()))
    
    # Quarta riga
    minuti_invio = list(map(int, file.readline().split()))


result = calcolo_tempo(N, M, tempo_blocco, ritardo, minuti_invio)


print(result)
