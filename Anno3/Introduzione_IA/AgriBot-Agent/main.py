import sys
import os
# Aggiunge la cartella aima al path (assumendo che sia nella stessa directory dello script)
sys.path.append(os.path.abspath("aima"))
import numpy as np
import time
import tensorflow as tf
from search import Problem, astar_search, uniform_cost_search,Node
from grid_cell_extractor import crop
from search import InstrumentedProblem
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

model = tf.keras.models.load_model("agribot_model.keras")
# Parametri griglia
N_ROWS = 6
N_COLS = 6
cells = crop("test3.png", N_ROWS, N_COLS)

grid_map = []
row = []

# Classi possibili 
LABELS = ['D', 'F', 'R', 'S', 'T', '.', 'V']


MAGENTA = '\033[95m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
NORMAL = '\033[0m'

class AgriBotProblem(Problem):
    move_cost=1
    cut_cost=1
    water_cost=1
    spray_cost=3
    refill_cost=1
    def __init__(self, grid, max_water=3,max_energy=30):
        self.grid = grid 
        self.n=len(grid)
        self.max_water=max_water
        #self.max_energy=max_energy
        
        
        self.start_position= None
        self.finish_position= None
        
        #weeds = set()
        dry = set()
        very_dry = set()
        self.rocks = set() #per memorizzare la posizione delle rocce uso un set per evitare duplicati
        self.station = set() #per memorizzare la posizione della stazione uso un set per evitare duplicati
        #pests= set()

        for i in range(self.n):
            for j in range(self.n):
                cell=grid[i][j]
                index = i*self.n+j   ##tipo (0,0) di una matrice 3*3 --> 0*3+0=0, (0,1) --> 0*3+1=1 ecc...
                if cell=="R":
                    self.rocks.add(index)
                elif cell=="S":
                    self.start_position=index
                elif cell=="F":
                    self.finish_position=index
                #elif cell == "W": #come memorizzare quando ho un erba infestante da tagliare, 
                    #weeds.add(index)  
                elif cell == "D":
                    dry.add(index)
                elif cell == "V":
                    very_dry.add(index)

                #elif cell == "P":
                    #pests.add(index)
                elif cell == "T":
                    self.station.add(index)
        initial= (self.start_position,self.max_water,frozenset(dry),frozenset(very_dry))#ho usato i set, invece che usare una griglia intera quindi
        #initial= (self.start_position,self.max_water,self.max_energy,frozenset(weeds),frozenset(dry),frozenset(pests),)#ho usato i set, invece che usare una griglia intera quindi
        #devo usare frozenset per rendere il set hasable sennò non poso usarlo su state di AIMA 
        super().__init__(initial=initial, goal=None)

    def actions(self, state):
        position, water, dry, very_dry = state
        #position, water, energy, weeds, dry, pests = state
        r= position // self.n #riga
        c= position % self.n #colonna

        possible_action = [] 
     
        #if energy>=self.move_cost: non controllo energia
        
        #--- AZIONI MOVIMENTO ---#
        #muoversi in su 
        if r >0:
            up_index = (r-1)*self.n+c 
            if up_index not in self.rocks:
                possible_action.append("UP")
        #muoversi in giù 
        if r < self.n - 1:
            down_index = (r+1)*self.n+c 
            if down_index not in self.rocks:
                possible_action.append("DOWN")
        #muoversi a destra 
        if c < self.n - 1:
            right_index = (r)*self.n+(c+1)
            if right_index not in self.rocks:
                possible_action.append("RIGHT")
        #muoversi a sinista
        if c > 0:
            left_index = (r)*self.n+(c-1)
            if left_index not in self.rocks:
                possible_action.append("LEFT")
        
        #if position in weeds and energy>self.cut_cost:
            #possible_action.append("CUT")
        if position in dry and water>0:
            possible_action.append("WATER")
        
        # Per le piante V serve 2 di acqua. Se ho solo 1, devo prima ricaricare.
        if position in very_dry and water>=2:
            possible_action.append("WATER")

        #if position in pests and energy>=self.spray_cost:
            #possible_action.append("SPRAY")

        if position in self.station and water < self.max_water: #se il serbatoio o l'energia non sono al max ha senso permettergli un refill 
            possible_action.append("REFILL")
        return possible_action

        
    def result(self, state, action):
        position, water, dry, very_dry = state
        #position, water, energy, weeds, dry, pests = state
        delta = {'UP': -self.n, 'DOWN': self.n, 'LEFT': -1, 'RIGHT': 1}
        #if action == "CUT": 
        #    new_weeds=weeds.difference({position})
        #    new_energy=energy-self.cut_cost
        #    return (position, water, new_energy, new_weeds, dry, pests)
       
        if action == "WATER" and position in dry:
            new_dry=dry.difference({position})
            new_water=water-1
            #new_energy=energy-self.water_cost
            return (position, new_water, new_dry,very_dry)
        if action == "WATER" and position in very_dry:
            new_very_dry=very_dry.difference({position})
            new_water=water-2
            return (position, new_water, dry,new_very_dry)
       
        #if action == "SPRAY":
        #    new_pests=pests.difference({position})
        #    new_energy=energy-self.spray_cost
        #    return (position, water, new_energy, weeds, dry, new_pests)
       
        if action == "REFILL": 
            #new_energy=energy-self.refill_cost
            return (position, self.max_water, dry,very_dry)

        new_position= position + delta[action]
        #new_energy= energy - self.move_cost
        return (new_position,water,dry,very_dry)
        

    def goal_test(self, state):
        position, water, dry, very_dry = state
        if (len(dry)==0) and (len(very_dry)==0) and position == self.finish_position:
            return True
        else:
            return False
    
    
    def rc(self,index):
            return index // self.n, index % self.n 
        
    def cal_manhattan(self,A,B):
        A_r, A_c = self.rc(A)
        B_r,B_c= self.rc(B)
        return abs(A_r - B_r)+abs(A_c-B_c)
#euristiche
    def h_manhattan(self,node):
       
        
        position, water, dry, very_dry = node.state
        
        #unisco le piante D e V
        all_plants = dry.union(very_dry)

        #se ho finito le dry 
        if len(all_plants)==0:
            return self.cal_manhattan(position,self.finish_position)
        
        # Caso: ho acqua a sufficienza (almeno 1)
        # Considero tutte le piante come target validi per l'euristica
        if water > 0:
            plant_dists=[]
            for index in all_plants:
                plant_dists.append(self.cal_manhattan(position,index))
            return min(plant_dists)
        # Caso: sono a secco
        if len(all_plants)>0 and water==0:
            station_dist=[]
            for index in self.station:
                station_dist.append(self.cal_manhattan(position,index))
            return min(station_dist)
        


    def h_max_pairwaise_Distance(self,node):
        position, water, dry, very_dry = node.state
        
        all_plants = dry.union(very_dry)
        
        if len(all_plants)==0:
            return self.cal_manhattan(position,self.finish_position)
            
        max_internal_distance = 0
        plants_list=list(all_plants) #ho convertito il set in una lista in modo tale da usare gli indici e calcolare ogni coppia una volta sola. 
        for i in range(len(plants_list)):
            for j in range(i + 1, len(plants_list)):
                dist = self.cal_manhattan(plants_list[i], plants_list[j])
                if dist > max_internal_distance:
                    max_internal_distance = dist
                    
        if(water==0):
            station_dist=[]
            for index in self.station:
                station_dist.append(self.cal_manhattan(position,index))
            return min(station_dist)+max_internal_distance
        
        if water > 0:
            plant_dists=[]
            for index in all_plants:
                plant_dists.append(self.cal_manhattan(position,index))
            most_close_plants=min(plant_dists)
            return max_internal_distance+most_close_plants


for i, j, cell_img in cells:
    # Preprocessing img
    normalized_cell = cell_img.astype("float32") / 255.0
    normalized_cell = normalized_cell.reshape(1, 28, 28, 1)
    
    # Predizione
    prediction = model.predict(normalized_cell, verbose=0) # verbose=0 per pulire output
    idx = np.argmax(prediction)
    char = LABELS[idx]
    
    row.append(char)
    
    # Se abbiamo finito la riga corrente (colonna == ultima colonna)
    if j == N_COLS - 1:
        grid_map.append(row)
        row = []



# Creazione del problema

def print_grid(problem, state, action=None):
    position, water, dry, very_dry = state
    n = problem.n
    
    print(f"\n--- Azione Eseguita: {action} ---")
    print(f"Stato: Acqua [{water}/{problem.max_water}] | Piante residue: {len(dry)+len(very_dry) }")

    for r in range(n):
        row_str = ""
        for c in range(n):
            idx = r * n + c
            char = "."
            
            # Logica di assegnazione simboli
            if idx == position:
                char = YELLOW + " B " +NORMAL # Robot
            elif idx in dry:
                char = GREEN+ " D " +NORMAL      # Pianta Secca
            elif idx in very_dry:
                char = GREEN+ " V " +NORMAL      # Pianta Molto Secca
            elif idx in problem.rocks:
                char = RED+ " R " +NORMAL     # Roccia
            elif idx in problem.station:
                char = BLUE + " T " +NORMAL    # Stazione
            elif idx == problem.finish_position:
                char = " F "    # Fine
            elif idx == problem.start_position:
                char = MAGENTA+ " S " + NORMAL
            else:
                char = " . "
            #time.sleep(3)
            row_str += char
            #print (row_str)
        print(row_str)
    print("-" * (n * 3))

            


def visualizza_semplice(problem, solution_node, pausa=0.8):
    # Mi prendo tutti i passi della soluzione.
    path = solution_node.path()
    n = problem.n

    # Uso pochi colori fissi per leggere la griglia velocemente.
    colors = {
        "R": "gray",
        "T": "deepskyblue",
        "F": "gold",
        "D": "orange",
        "V": "red",
        "B": "limegreen",
    }

    # Creo la figura e lascio spazio in basso per i pulsanti.
    fig, ax = plt.subplots(figsize=(8, 9))
    plt.subplots_adjust(bottom=0.18)
    stato = {"step": 0, "playing": False}

    def disegna(step):
        # Pulisco e ridisegno 
        ax.clear()
        node = path[step]
        position, water, dry, very_dry = node.state
        action = node.action if node.action else "PARTENZA"

        # Imposto assi e griglia in modo leggibile.
        ax.set_xlim(-0.5, n - 0.5)
        ax.set_ylim(n - 0.5, -0.5)
        ax.set_xticks(range(n))
        ax.set_yticks(range(n))
        ax.set_xticks(np.arange(-0.5, n, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, n, 1), minor=True)
        ax.grid(which="minor", color="black", linewidth=1)
        ax.tick_params(which="minor", bottom=False, left=False)
        ax.set_title(
            f"Step {step}/{len(path) - 1} - Azione: {action}\n"
            f"Acqua: {water}/{problem.max_water} | Piante rimaste: {len(dry) + len(very_dry)}"
        )
        trail_x = []
        trail_y = []
        for past_step in range(step + 1):
            past_pos = path[past_step].state[0]
            pr, pc = past_pos // n, past_pos % n
            trail_x.append(pc)
            trail_y.append(pr)
        ax.plot(trail_x, trail_y, color="limegreen", linewidth=2, alpha=0.6, zorder=1)
        for r in range(n):
            for c in range(n):
                idx = r * n + c
                x, y = c, r

                # Disegno prima gli elementi statici.
                if idx in problem.rocks:
                    ax.add_patch(patches.Rectangle((x - 0.5, y - 0.5), 1, 1, color=colors["R"]))
                    ax.text(x, y, "R", ha="center", va="center", color="white", fontweight="bold")
                elif idx in problem.station:
                    ax.add_patch(
                        patches.Rectangle((x - 0.5, y - 0.5), 1, 1, color=colors["T"], alpha=0.25)
                    )
                    ax.text(x, y, "T", ha="center", va="center", color="blue", fontweight="bold")
                elif idx == problem.finish_position:
                    ax.add_patch(
                        patches.Rectangle((x - 0.5, y - 0.5), 1, 1, fill=False, edgecolor=colors["F"], linewidth=3)
                    )
                    ax.text(x, y, "F", ha="center", va="center", color="black", fontweight="bold")

                # Disegno le piante ancora da irrigare.
                if idx in dry:
                    ax.add_patch(patches.Circle((x, y), 0.28, color=colors["D"]))
                    ax.text(x, y, "D", ha="center", va="center", color="white", fontsize=8)
                elif idx in very_dry:
                    ax.add_patch(patches.Circle((x, y), 0.28, color=colors["V"]))
                    ax.text(x, y, "V", ha="center", va="center", color="white", fontsize=8)

                # Disegno il bot per ultimo, così resta visibile.
                if idx == position:
                    ax.add_patch(
                        patches.Rectangle((x - 0.35, y - 0.35), 0.7, 0.7, color=colors["B"], ec="black")
                    )
                    ax.text(x, y, "B", ha="center", va="center", color="black", fontweight="bold")
        fig.canvas.draw_idle()

    def avanti(_event=None):
        # Avanzo di uno step manualmente.
        if stato["step"] < len(path) - 1:
            stato["step"] += 1
            disegna(stato["step"])

    def indietro(_event=None):
        # Torno indietro di uno step manualmente.
        if stato["step"] > 0:
            stato["step"] -= 1
            disegna(stato["step"])

    def play(_event):
        # Metto in play l'animazione.
        stato["playing"] = True

    def pausa_fn(_event):
        # Metto in pausa l'animazione.
        stato["playing"] = False

    def tick():
        # Se sono in play, avanzo automaticamente.
        if stato["playing"]:
            if stato["step"] < len(path) - 1:
                stato["step"] += 1
                disegna(stato["step"])
            else:
                stato["playing"] = False

    # Creo i pulsanti sotto alla griglia.
    ax_play = plt.axes([0.12, 0.05, 0.15, 0.07])
    ax_pause = plt.axes([0.30, 0.05, 0.15, 0.07])
    ax_prev = plt.axes([0.48, 0.05, 0.15, 0.07])
    ax_next = plt.axes([0.66, 0.05, 0.15, 0.07])
    btn_play = Button(ax_play, "Play")
    btn_pause = Button(ax_pause, "Pausa")
    btn_prev = Button(ax_prev, "Indietro")
    btn_next = Button(ax_next, "Avanti")
    btn_play.on_clicked(play)
    btn_pause.on_clicked(pausa_fn)
    btn_prev.on_clicked(indietro)
    btn_next.on_clicked(avanti)

    # Uso un timer per aggiornare l'animazione quando premo Play.
    timer = fig.canvas.new_timer(interval=max(100, int(pausa * 1000)))
    timer.add_callback(tick)
    timer.start()

    # Disegno il primo frame.
    disegna(0)
    plt.show()



problem = AgriBotProblem(grid_map, max_water=2)
def ucs(): 
    problem_per_ucs = InstrumentedProblem(problem) 
    print("Avvio ricerca UCS")
    solution_node = uniform_cost_search(problem_per_ucs)

    if solution_node:
        #statistiche
        print(f"Nodi esplorati da UCS: {problem_per_ucs.states}")
        print(f"Goal test effettuati: {problem_per_ucs.goal_tests}")
        print(f"Costo: {solution_node.path_cost}")
        print(f"passi: ({len(solution_node.solution())}):")
        print(solution_node.solution())
        visualizza_semplice(problem, solution_node)
    else:
        print("Nessuna soluzione trovata.")

def a_star():
    problem_per_astar = InstrumentedProblem(problem)
    print("Avvio ricerca A* con euristica max_pairwaise_Distance...")
    solution_node = astar_search(problem_per_astar, h=problem.h_max_pairwaise_Distance)
    
    if solution_node:
        print(f"Costo Totale: {solution_node.path_cost}")
        print(f"Numero passi: {len(solution_node.solution())}")
        print("Azioni:", solution_node.solution())
        print(f"Nodi esplorati da A*: {problem_per_astar.states}")
        print(f"Goal test effettuati: {problem_per_astar.goal_tests}")
        visualizza_semplice(problem, solution_node)
        
    else:
        print("Nessuna soluzione trovata.")

def a_star1():
    problem_per_astar = InstrumentedProblem(problem)
    print("Avvio ricerca A* con euristica Manhattan...")
    solution_node = astar_search(problem_per_astar, h=problem.h_manhattan)

    if solution_node:
        print(f"Costo Totale: {solution_node.path_cost}")
        print(f"Numero passi: {len(solution_node.solution())}")
        print("Azioni:", solution_node.solution())
        print(f"Nodi esplorati da A*: {problem_per_astar.states}")
        print(f"Goal test effettuati: {problem_per_astar.goal_tests}")
        visualizza_semplice(problem, solution_node)
        path = solution_node.path()
        for n in path:
            print_grid(problem, n.state, n.action)
        # mostra la grid
        #for n in path:
        #    print_grid(problem, n.state, n.action)
    else:
        print("Nessuna soluzione trovata.")

print("\n\n")
ucs()
print("\n\n")
a_star()
print("\n\n")
a_star1()
