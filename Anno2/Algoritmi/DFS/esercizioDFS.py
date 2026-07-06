import networkx as nx
import matplotlib.pyplot as plt
import time
import sys # Usato per flushare l'output di print

# --- Classe Visualizer ---
class GraphVisualizer:
    """
    Visualizza passo-passo l'algoritmo IsTree usando NetworkX e Matplotlib.
    Include controllo interattivo della velocità tramite tastiera.
    """
    # Stati interni
    WHITE, GRAY, BLACK = 0, 1, 2
    # Colori per la visualizzazione
    COLOR_MAP_VIZ = {
        WHITE: 'lightblue', GRAY: 'orange', BLACK: 'dimgray',
        'CYCLE': 'red', 'START': 'lime'
    }

    def __init__(self, graph_dict, fig, ax, initial_pause=0.8, min_pause=0.05, max_pause=5.0, pause_step=0.1):
        """
        Inizializza il visualizzatore su una figura/asse esistente.

        Args:
            graph_dict (dict): Rappresentazione del grafo.
            fig (matplotlib.figure.Figure): La figura su cui disegnare.
            ax (matplotlib.axes.Axes): L'asse su cui disegnare.
            initial_pause (float): Pausa iniziale tra i passi.
            min_pause (float): Pausa minima consentita.
            max_pause (float): Pausa massima consentita.
            pause_step (float): Incremento/decremento della pausa per tasto.
        """
        self.graph_dict = graph_dict
        self.fig = fig
        self.ax = ax
        self.pause_duration = initial_pause
        self.min_pause = min_pause
        self.max_pause = max_pause
        self.pause_step = pause_step

        # Connetti l'handler degli eventi da tastiera
        self.fig.canvas.mpl_connect('key_press_event', self._on_key_press)

        # Crea il grafo NetworkX
        self.nx_graph = nx.Graph()
        if graph_dict:
            all_nodes = set(graph_dict.keys())
            for node, neighbors in graph_dict.items():
                 all_nodes.update(neighbors)
                 for neighbor in neighbors:
                     self.nx_graph.add_edge(node, neighbor)
            for node in all_nodes:
                if node not in self.nx_graph:
                    self.nx_graph.add_node(node)
        self.nodes = list(self.nx_graph.nodes())

        # Stato algoritmo
        self.node_colors_state = {}
        self.predecessors = {}
        self.visited_nodes_count = 0
        self.cycle_detected = False
        self.cycle_edge = None
        self.current_message = "" # Messaggio da mostrare nel titolo

        # Calcola layout fisso per questo grafo
        if self.nodes:
             try:
                 self.pos = nx.kamada_kawai_layout(self.nx_graph)
             except Exception: # Fallback generico
                 print("Warning: Layout calculation failed, using spring layout.")
                 self.pos = nx.spring_layout(self.nx_graph, seed=42)
        else:
             self.pos = {}

    def _on_key_press(self, event):
        """Gestisce la pressione dei tasti per cambiare velocità."""
        # print(f"Key pressed: {event.key}") # Debug
        if event.key == '-' or event.key == '_':
            self.pause_duration = min(self.max_pause, self.pause_duration + self.pause_step)
            print(f"\nVelocità diminuita. Pausa attuale: {self.pause_duration:.2f}s", flush=True)
        elif event.key == '+' or event.key == '=':
            self.pause_duration = max(self.min_pause, self.pause_duration - self.pause_step)
            print(f"\nVelocità aumentata. Pausa attuale: {self.pause_duration:.2f}s", flush=True)

        # Aggiorna subito il titolo per mostrare la nuova velocità (se stiamo disegnando)
        if hasattr(self, 'ax') and self.ax.get_title():
             self._update_title() # Metodo helper per aggiornare titolo
             plt.draw()


    def _initialize_state(self):
        """Resetta lo stato dell'algoritmo."""
        self.visited_nodes_count = 0
        self.cycle_detected = False
        self.cycle_edge = None
        for node in self.nodes:
            self.node_colors_state[node] = self.WHITE
            self.predecessors[node] = None
        # Reset messaggio
        self.current_message = ""

    def _update_title(self):
        """Aggiorna il titolo della figura con messaggio e velocità."""
        title = "Algoritmo IsTree | Speed +/- | "
        title += f"Pausa: {self.pause_duration:.2f}s\n"
        title += self.current_message
        self.ax.set_title(title, fontsize=10)


    def _draw_graph(self, message=""):
        """Disegna lo stato corrente del grafo."""
        if message:
            self.current_message = message # Aggiorna messaggio corrente

        self.ax.cla() # Pulisce l'asse

        if not self.nodes: # Gestisce grafo vuoto nel disegno
            self.ax.text(0.5, 0.5, "Grafo Vuoto", ha='center', va='center')
            self._update_title()
            self.ax.axis('off')
            plt.draw()
            plt.pause(self.pause_duration)
            return

        # Colori nodi e archi
        viz_colors = [self.COLOR_MAP_VIZ[self.node_colors_state.get(node, self.WHITE)] for node in self.nx_graph.nodes()]
        edge_colors = ['gray'] * self.nx_graph.number_of_edges()
        edge_widths = [1] * self.nx_graph.number_of_edges()

        if self.cycle_detected and self.cycle_edge:
            try:
                edges_list = list(self.nx_graph.edges())
                u, v = self.cycle_edge
                if (u, v) in edges_list:
                    idx = edges_list.index((u, v))
                elif (v, u) in edges_list:
                    idx = edges_list.index((v, u))
                else:
                    raise ValueError # Arco non trovato
                edge_colors[idx] = 'red'
                edge_widths[idx] = 2.5
            except ValueError:
                 # print(f"Warning: Could not find cycle edge {self.cycle_edge} in edge list.")
                 pass # Ignora se non trovato


        # Disegno
        nx.draw_networkx_nodes(self.nx_graph, self.pos, node_color=viz_colors, node_size=700, ax=self.ax)
        nx.draw_networkx_edges(self.nx_graph, self.pos, edge_color=edge_colors, width=edge_widths, alpha=0.6, ax=self.ax)
        nx.draw_networkx_labels(self.nx_graph, self.pos, font_size=12, font_weight='bold', ax=self.ax)

        self._update_title() # Imposta/Aggiorna il titolo
        self.ax.axis('off')
        plt.draw()
        # Pausa critica per vedere lo step e permettere interazione
        self.fig.canvas.start_event_loop(self.pause_duration)
        # NOTA: plt.pause() può avere problemi con l'event handling in alcuni backend.
        # start_event_loop è più robusto per interattività durante la pausa.

    def _dfs_visit_visual(self, u, parent):
        """DFS ricorsiva con aggiornamenti visuali."""
        if self.cycle_detected: return

        # 1. Marca GRIGIO e visualizza
        self.node_colors_state[u] = self.GRAY
        self.visited_nodes_count += 1
        self.predecessors[u] = parent
        self._draw_graph(message=f"Visitando nodo {u} (GRIGIO)")

        # 2. Esplora vicini
        for v in self.graph_dict.get(u, []):
            if v == parent: continue

            neighbor_state = self.node_colors_state.get(v)

            if neighbor_state == self.WHITE:
                self._draw_graph(message=f"Da {u}, esplorando arco albero verso {v}")
                self._dfs_visit_visual(v, u)
                if self.cycle_detected: return
            elif neighbor_state == self.GRAY:
                self.cycle_detected = True
                self.cycle_edge = (u, v)
                self._draw_graph(message=f"CICLO! Da {u}, arco ({u}-{v}) verso nodo GRIGIO {v}")
                return # Ciclo trovato, interrompi

        # 3. Marca NERO e visualizza
        self.node_colors_state[u] = self.BLACK
        self._draw_graph(message=f"Fine visita nodo {u} (NERO)")

    def run_visualization(self):
        """Esegue l'algoritmo IsTree visualizzandone i passi."""
        print(f"\n--- Analizzando Grafo: {list(self.nx_graph.nodes())} ---", flush=True)
        if not self.nodes:
            self.current_message = "Grafo Vuoto - Non è un Albero"
            self._draw_graph() # Mostra messaggio grafo vuoto
            print("Grafo vuoto. Considerato non un albero.")
            return False

        # 1. Inizializzazione e stato iniziale
        self._initialize_state()
        start_node = self.nodes[0]
        self._draw_graph(message=f"Inizio DFS da {start_node}. Tutti BIANCHI.")

        # 2. Esegui DFS visuale
        self._dfs_visit_visual(start_node, None)

        # 3. Verifica finale e mostra risultato
        num_total_nodes = len(self.nodes)
        is_connected = (self.visited_nodes_count == num_total_nodes)
        is_acyclic = not self.cycle_detected
        is_it_a_tree = is_acyclic and is_connected

        final_message = "Risultato: "
        if is_it_a_tree:
            final_message += "È un ALBERO."
        else:
            final_message += "NON è un albero ("
            reasons = []
            if not is_acyclic: reasons.append(f"Ciclo rilevato arco ~{self.cycle_edge}")
            if not is_connected: reasons.append(f"Non connesso - Visitati: {self.visited_nodes_count}/{num_total_nodes}")
            final_message += ", ".join(reasons) + ")"

        # Mostra l'ultimo stato con il risultato finale
        self._draw_graph(message=final_message)
        print(final_message, flush=True)

        return is_it_a_tree


# --- Esecuzione Principale ---

if __name__ == "__main__":
    # Definisci i grafi
    graph_tree = {
        0: [1, 2], 1: [0, 3, 4], 2: [0], 3: [1], 4: [1]
    }
    graph_cycle = {
        'A': ['B', 'C'], 'B': ['A', 'D'], 'C': ['A', 'D'], 'D': ['B', 'C', 'E'], 'E': ['D']
    } # Grafo con ciclo B-C-D

    # Setup Matplotlib per interattività
    plt.ion() # Attiva modalità interattiva
    fig, ax = plt.subplots(figsize=(10, 7)) # Crea UNA figura e UN asse

    # --- Esempio 1: Grafo Albero ---
    print("*"*10 + " ESEMPIO 1: GRAFO ALBERO " + "*"*10)
    print("Controlli: Premi '-' per rallentare, '+' per accelerare nella finestra del grafico.")
    vis_tree = GraphVisualizer(graph_tree, fig, ax, initial_pause=0.8)
    vis_tree.run_visualization()

    print("\nVisualizzazione Albero completata. Premi Invio per continuare con il grafo con ciclo...")
    # Pausa aggiuntiva per vedere il risultato finale dell'albero
    # E attende l'utente per passare al prossimo
    fig.canvas.start_event_loop(0.1) # Processa eventi GUI residui
    input("...") # Attende l'input dell'utente sulla console


    # --- Esempio 2: Grafo con Ciclo ---
    print("\n" + "*"*10 + " ESEMPIO 2: GRAFO CON CICLO " + "*"*10)
    print("Controlli: Premi '-' per rallentare, '+' per accelerare nella finestra del grafico.")
    # Riutilizza la stessa figura/asse, crea un nuovo visualizer per il nuovo grafo
    vis_cycle = GraphVisualizer(graph_cycle, fig, ax, initial_pause=0.8)
    vis_cycle.run_visualization()

    # --- Fine ---
    print("\nVisualizzazioni completate.")
    plt.ioff() # Disattiva modalità interattiva
    ax.set_title(ax.get_title() + "\nFine. Chiudi la finestra per uscire.")
    plt.show() # Mantieni aperta l'ultima finestra finché non viene chiusa