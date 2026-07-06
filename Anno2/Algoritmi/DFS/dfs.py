# --- START OF FILE dfs_directed_choice.py ---

# --- Backend Setting (Optional) ---
import matplotlib
try:
    # matplotlib.use('TkAgg')
    # matplotlib.use('Qt5Agg') # Requires pip install PyQt5
    pass # Use default first
except Exception as e:
    print(f"Could not set backend: {e}")
# ----------------------------------

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.animation as animation
from matplotlib.widgets import Button, TextBox, CheckButtons # Import CheckButtons
from functools import partial
import copy
import ast
import sys

# --- Dependency Checks ---
try:
    import scipy
    _SCIPY_AVAILABLE = True
except ImportError:
    _SCIPY_AVAILABLE = False

_PYDOT_AVAILABLE = False
try:
    import pydot
    if hasattr(nx, 'nx_pydot') and hasattr(nx.nx_pydot, 'graphviz_layout'):
        _PYDOT_AVAILABLE = True
        print("Pydot (for hierarchical layout) is available.")
    else:
        print("Pydot found, but NetworkX interface missing. Update NetworkX? Falling back.")
except ImportError:
    print("Pydot not found. Hierarchical layout disabled.")
    print("To enable: 1) Install Graphviz (system-wide) 2) pip install pydot")
# -------------------------


animation_frames = []

# --- Helper and DFS Functions (Identical to previous version) ---
def capture_frame(description, current_node, current_edge, time, color, d, f, edge_types, parent):
    global animation_frames
    frame_data = {
        'description': description, 'current_node': current_node, 'current_edge': current_edge,
        'time': time, 'color': copy.deepcopy(color), 'd': copy.deepcopy(d), 'f': copy.deepcopy(f),
        'edge_types': copy.deepcopy(edge_types), 'parent': copy.deepcopy(parent)
    }
    animation_frames.append(frame_data)

def dfs_visit_classify_animated(u, graph, state):
    time = state['time']; color = state['color']; d = state['d']; f = state['f']; parent = state['parent']; edge_types = state['edge_types']
    time += 1; d[u] = time; color[u] = 'GRAY'; state['time'] = time
    capture_frame(f"Visitando {u} (Scoperto t={d[u]})", u, None, time, color, d, f, edge_types, parent)
    if u in graph:
        for v in graph.get(u, []):
            # For undirected graphs conceptually represented by directed edges for DFS:
            # Avoid immediately going back to the parent if it's not a self-loop
            # This check is primarily for the logic if you were adapting DFS *itself* for undirected.
            # Since we keep the directed DFS logic, this check isn't strictly needed here,
            # but it's good practice to think about.
            # if parent.get(u) == v and u != v: # Check if v is the direct parent
            #      continue # Skip exploring the edge back to the parent immediately

            capture_frame(f"Esaminando arco ({u} -> {v})", u, (u, v), time, color, d, f, edge_types, parent)
            edge_type = None
            if color[v] == 'WHITE':
                edge_type = 'Tree'; edge_types[(u, v)] = edge_type; parent[v] = u
                capture_frame(f"({u} -> {v}): TREE EDGE", u, (u, v), time, color, d, f, edge_types, parent)
                state['parent'] = parent; state['edge_types'] = edge_types
                dfs_visit_classify_animated(v, graph, state)
                time = state['time']
            elif color[v] == 'GRAY':
                # In an undirected context treated as directed, this is an edge to an ancestor (could be parent).
                # We'll still label it "Backward" based on the directed exploration.
                edge_type = 'Backward'; edge_types[(u, v)] = edge_type
                capture_frame(f"({u} -> {v}): BACKWARD EDGE", u, (u, v), time, color, d, f, edge_types, parent)
            elif color[v] == 'BLACK':
                # Forward/Cross edges can still technically occur in the directed representation
                # of an undirected graph if components/branches are involved.
                edge_type = 'Forward' if d[u] < d[v] else 'Cross'; edge_types[(u, v)] = edge_type
                capture_frame(f"({u} -> {v}): {edge_type.upper()} EDGE", u, (u, v), time, color, d, f, edge_types, parent)
            state['edge_types'] = edge_types
    color[u] = 'BLACK'; time += 1; f[u] = time; state['time'] = time
    capture_frame(f"Finito {u} (Fine t={f[u]})", u, None, time, color, d, f, edge_types, parent)

def dfs_classify_edges_animated(graph):
    global animation_frames; animation_frames = []
    all_nodes = set(graph.keys())
    for neighbors in graph.values():
        if isinstance(neighbors, (list, tuple, set)): all_nodes.update(neighbors)
    for node in list(all_nodes):
        if node not in graph: graph[node] = []
    initial_color = {node: 'WHITE' for node in all_nodes}; initial_parent = {node: None for node in all_nodes}
    initial_d = {node: 0 for node in all_nodes}; initial_f = {node: 0 for node in all_nodes}
    initial_time = 0; initial_edge_types = {}
    state = {'time': initial_time, 'color': initial_color, 'd': initial_d, 'f': initial_f, 'parent': initial_parent, 'edge_types': initial_edge_types}
    print("=== Inizio Classificazione Archi DFS (Animato) ===")
    print(f"Nodi: {list(all_nodes)}")
    capture_frame("Inizio DFS", None, None, state['time'], state['color'], state['d'], state['f'], state['edge_types'], state['parent'])
    # Sort keys to ensure consistent traversal order for reproducibility
    sorted_nodes = sorted(list(all_nodes), key=str)
    for u in sorted_nodes:
        if state['color'][u] == 'WHITE':
            capture_frame(f"Nuova Radice DFS: {u}", u, None, state['time'], state['color'], state['d'], state['f'], state['edge_types'], state['parent'])
            dfs_visit_classify_animated(u, graph, state)
    print("\n=== Fine Classificazione Archi DFS ===")
    print("Tempi Scoperta (d):", state['d']); print("Tempi Fine (f):", state['f'])
    print("Genitori (pi):", state['parent']); print(f"Classificazione Archi: {state['edge_types']}")
    print(f"Numero di frame catturati: {len(animation_frames)}")
    capture_frame("DFS Completata", None, None, state['time'], state['color'], state['d'], state['f'], state['edge_types'], state['parent'])
    return animation_frames, state['edge_types']


# --- Funzione di Animazione Finale (MODIFICATA) ---
def animate_dfs(graph_dict, is_directed, frames, final_edge_types): # Aggiunto is_directed
    """Crea e mostra l'animazione della DFS con layout, tabella dinamica, controlli e vista albero finale."""
    # 1. Setup Grafo NetworkX Originale (rispettando is_directed)
    if is_directed:
        print("Costruendo grafo come Diretto (DiGraph)")
        G_orig = nx.DiGraph()
    else:
        print("Costruendo grafo come Non Diretto (Graph)")
        G_orig = nx.Graph()

    all_nodes = set(graph_dict.keys())
    for u, neighbors in graph_dict.items():
        if isinstance(neighbors, (list, tuple, set)):
            for v in neighbors:
                G_orig.add_edge(u, v) # nx.Graph gestisce automaticamente coppie inverse
                all_nodes.add(v)
        else:
             print(f"Attenzione: Vicini non validi per '{u}', ignorati.")
             graph_dict[u] = []
    for node in all_nodes:
         if node not in G_orig: G_orig.add_node(node) # Aggiungi nodi isolati

    # 2. Calcolo Layout Animazione
    pos_animation = None
    # ... (codice layout animazione come prima) ...
    if _SCIPY_AVAILABLE:
        try: pos_animation = nx.kamada_kawai_layout(G_orig); print("Layout Kamada-Kawai calcolato.")
        except Exception: pos_animation = nx.spring_layout(G_orig, seed=42); print("Fallback a Spring Layout.")
    else: pos_animation = nx.spring_layout(G_orig, seed=42); print("Uso Spring Layout per animazione.")
    if pos_animation is None: pos_animation = nx.spring_layout(G_orig, seed=42)


    # 3. Pre-calcola grafo e layout per la vista albero
    if is_directed:
        G_tree = nx.DiGraph()
    else:
        G_tree = nx.Graph() # Albero non diretto per grafo non diretto

    tree_edges_list = []
    for node in G_orig.nodes(): G_tree.add_node(node)
    for edge, edge_type in final_edge_types.items():
        if edge_type == 'Tree':
            # Per grafo non orientato, aggiungiamo comunque come diretto per coerenza con DFS
            # ma il tipo G_tree è nx.Graph
            G_tree.add_edge(edge[0], edge[1])
            tree_edges_list.append(edge) # Manteniamo la direzione per edgelist

    pos_tree = None
    tree_layout_type = "Spring" # Default
    if tree_edges_list:
        # --- MODIFICA QUI: Tenta Graphviz se disponibile, anche per Undirected ---
        if _PYDOT_AVAILABLE:
            print("Tentativo layout gerarchico/dot per l'albero (richiede Graphviz/Pydot)...")
            try:
                # Prova 'dot' anche per grafi non orientati (potrebbe funzionare per alberi)
                pos_tree = nx.nx_pydot.graphviz_layout(G_tree, prog='dot')
                print("Layout basato su Graphviz 'dot' calcolato.")
                tree_layout_type = "Hierarchical (dot)"
            except Exception as e:
                print(f"--> Layout 'dot' fallito: {e}. Fallback a Spring.")
                pos_tree = nx.spring_layout(G_tree, seed=43) # Fallback
                tree_layout_type = "Spring (Fallback)"
        # -----------------------------------------------------------------------
        else:
             # Se pydot non era disponibile
             print("Pydot/Graphviz non disponibili, uso Spring layout per albero.")
             pos_tree = nx.spring_layout(G_tree, seed=43)

        # Fallback finale se pos_tree è ancora None
        if pos_tree is None:
             print("Layout albero fallito, uso Spring layout.")
             pos_tree = nx.spring_layout(G_tree, seed=43)
             tree_layout_type = "Spring (Fallback)"

    # 4. Setup Figura e Assi Principali (invariato)
    fig, ax = plt.subplots(figsize=(13, 11))
    plt.subplots_adjust(bottom=0.4, top=0.95, left=0.05, right=0.95)

    # --- TENTATIVO SCHERMO INTERO (invariato) ---
    manager = plt.get_current_fig_manager()
    if manager:
        try: manager.full_screen_toggle(); print("Tentativo schermo intero.")
        except Exception as e: print(f"Errore schermo intero: {e}")
    else: print("Attenzione: Gestore finestra non trovato.")
    # ------------------------------------

    # 5. Definizioni Colori e Stili (invariato)
    edge_color_map = {'Tree': 'blue', 'Backward': 'red', 'Forward': 'green', 'Cross': 'purple'}
    default_edge_color = 'lightgray'; node_color_map = {'WHITE': 'white', 'GRAY': 'cyan', 'BLACK': 'darkgray'}
    node_outline_color = 'black'

    # 6. Creazione Handles Legenda (invariato)
    legend_handles = [mpatches.Patch(color=c, label=f'{t} Edge') for t, c in edge_color_map.items()]
    legend_handles.extend([
        mpatches.Patch(facecolor=node_color_map['WHITE'], edgecolor='black', label='Nodo WHITE'),
        mpatches.Patch(facecolor=node_color_map['GRAY'], edgecolor='black', label='Nodo GRAY'),
        mpatches.Patch(facecolor=node_color_map['BLACK'], edgecolor='black', label='Nodo BLACK'),
        mpatches.Patch(facecolor='white', edgecolor='orange', linewidth=2, label='Nodo/Arco Attuale')
    ])

    # 7. Creazione Assi Tabella e Legenda (invariato)
    bottom_y = 0.12; element_height = 0.23
    table_x = 0.10; table_width = 0.55
    legend_x = table_x + table_width + 0.02; legend_width = 0.23
    table_ax_pos = [table_x, bottom_y, table_width, element_height]
    legend_ax_pos = [legend_x, bottom_y, legend_width, element_height]
    table_ax = fig.add_axes(table_ax_pos)
    legend_ax = fig.add_axes(legend_ax_pos)
    def draw_static_legend(ax_legend): ax_legend.clear(); ax_legend.axis('off'); ax_legend.legend(handles=legend_handles, loc='center left', fontsize='small', frameon=False)
    draw_static_legend(legend_ax)
    def update_table_display(ax_table, current_edge_types):
        ax_table.clear(); ax_table.axis('off')
        if not current_edge_types: ax_table.text(0.5, 0.5, "Nessun arco classificato finora.", ha='center', va='center', fontsize=9); return
        table_data = [[f"{u} -> {v}", edge_type] for (u,v), edge_type in sorted(current_edge_types.items(), key=lambda item: str(item[0]))]
        columns = ("Arco", "Tipo")
        table = ax_table.table(cellText=table_data, colLabels=columns, cellLoc='center', loc='center', colColours=['lightgrey']*len(columns))
        table.auto_set_font_size(False); table.set_fontsize(9); table.scale(1, 1.3)

    # 8. Stato Animazione (invariato)
    current_frame_index = 0; is_paused = True; total_frames = len(frames)
    display_mode = 'animation'

    # 9. Funzione Aggiornamento Display Principale (MODIFICATA per frecce condizionali)
    def update_display():
        nonlocal display_mode, current_frame_index

        if display_mode == 'animation':
            ax.clear()
            if not (0 <= current_frame_index < total_frames): current_frame_index = 0
            frame_data = frames[current_frame_index]
            node_colors_state = frame_data['color']; edge_types_state = frame_data['edge_types']
            current_node = frame_data['current_node']; current_edge = frame_data['current_edge']
            d_times = frame_data['d']; f_times = frame_data['f']; description = frame_data['description']
            pos_to_use = pos_animation

            # Disegno Nodi e Etichette (invariato)
            node_colors_plot = [node_color_map.get(node_colors_state.get(n, 'WHITE'), 'white') for n in G_orig.nodes()]
            node_outlines_plot = ['orange' if n == current_node else node_outline_color for n in G_orig.nodes()]
            node_outline_widths = [3.0 if n == current_node else 1.0 for n in G_orig.nodes()]
            nx.draw_networkx_nodes(G_orig, pos_to_use, ax=ax, node_size=700, node_color=node_colors_plot, edgecolors=node_outlines_plot, linewidths=node_outline_widths)
            labels = {}
            for node in G_orig.nodes():
                d_val, f_val = d_times.get(node, 0), f_times.get(node, 0)
                labels[node] = f"{node}\n" + (f"d={d_val}" if d_val > 0 else "") + (f"\nf={f_val}" if f_val > 0 else "")
                labels[node] = labels[node].strip()
            nx.draw_networkx_labels(G_orig, pos_to_use, ax=ax, labels=labels, font_size=9, font_weight='bold')

            # Disegno Archi (con frecce condizionali)
            edge_colors_plot = []; edge_widths_plot = []
            for u, v in G_orig.edges():
                edge = (u, v); edge_type = edge_types_state.get(edge)
                color = default_edge_color; width = 1.0
                if edge_type: color = edge_color_map.get(edge_type, default_edge_color); width = 2.0
                if edge == current_edge: color = 'orange'; width = 3.0
                edge_colors_plot.append(color); edge_widths_plot.append(width)
            nx.draw_networkx_edges(G_orig, pos_to_use, ax=ax, edge_color=edge_colors_plot, width=edge_widths_plot,
                                   alpha=0.8,
                                   arrows=is_directed, # <<< CONDIZIONALE QUI
                                   arrowstyle='->' if is_directed else '-', # Stile freccia solo se diretto
                                   arrowsize=15 if is_directed else 0, # Dimensione freccia solo se diretto
                                   connectionstyle='arc3,rad=0.1')

            ax.set_title(f"DFS Step {current_frame_index + 1}/{total_frames}: {description} (Time={frame_data['time']})")
            update_table_display(table_ax, frame_data['edge_types'])

        elif display_mode == 'tree':
            ax.clear(); table_ax.clear(); table_ax.axis('off')
            if not tree_edges_list or pos_tree is None:
                ax.text(0.5, 0.5, "Nessun Tree Edge trovato\no impossibile calcolare layout.", ha='center', va='center', fontsize=12)
                ax.set_title("DFS Tree/Forest (Vuoto)")
            else:
                pos_to_use = pos_tree
                nx.draw_networkx_nodes(G_tree, pos_to_use, ax=ax, node_size=700, node_color='skyblue', alpha=0.9)
                nx.draw_networkx_edges(G_tree, pos_to_use, ax=ax,
                                    edgelist=tree_edges_list, edge_color='blue', width=1.5, alpha=0.7,
                                    arrows=is_directed, # <<< CONDIZIONALE QUI
                                    arrowstyle='->' if is_directed else '-',
                                    arrowsize=15 if is_directed else 0,
                                    connectionstyle='arc3,rad=0.1')
                tree_labels = {node: str(node) for node in G_tree.nodes()}
                nx.draw_networkx_labels(G_tree, pos_to_use, ax=ax, labels=tree_labels, font_size=12, font_weight='bold')
                ax.set_title(f"DFS Tree/Forest ({tree_layout_type} Layout)")
                table_ax.text(0.5, 0.5, "Vista Albero DFS", ha='center', va='center', fontsize=10, style='italic')

        ax.axis('off')
        fig.canvas.draw_idle()

    # 10. Funzione Animazione Step (invariato)
    def animation_step(frame_unused):
        nonlocal current_frame_index, is_paused, display_mode
        if not is_paused and display_mode == 'animation':
            next_index = min(current_frame_index + 1, total_frames - 1)
            if next_index != current_frame_index:
                 current_frame_index = next_index; update_display()
                 if current_frame_index == total_frames - 1: pause_animation()
            elif current_frame_index == total_frames - 1: pause_animation()

    # 11. Funzioni Controllo Pause/Resume (invariato)
    def pause_animation():
        nonlocal is_paused
        if ani.event_source: ani.event_source.stop()
        is_paused = True;
        if hasattr(fig, '_btn_pause'): fig._btn_pause.label.set_text('Resume')
        if fig.canvas: fig.canvas.draw_idle()
    def resume_animation():
        nonlocal is_paused
        if display_mode == 'tree': return
        if ani.event_source: ani.event_source.start()
        is_paused = False;
        if hasattr(fig, '_btn_pause'): fig._btn_pause.label.set_text('Pause ')
        if fig.canvas: fig.canvas.draw_idle()

    # 12. Callbacks Pulsanti (invariato)
    def toggle_pause(event):
        if is_paused and display_mode == 'tree': go_home(event); return
        if is_paused and current_frame_index == total_frames - 1 and display_mode == 'animation': go_home(event); return
        if is_paused: resume_animation()
        else: pause_animation()
    def go_next(event):
        nonlocal current_frame_index, display_mode; pause_animation()
        if display_mode == 'animation':
            if current_frame_index < total_frames - 1: current_frame_index += 1
            elif current_frame_index == total_frames - 1: display_mode = 'tree'; print("Passaggio a vista Albero DFS")
        update_display()
    def go_prev(event):
        nonlocal current_frame_index, display_mode; pause_animation()
        if display_mode == 'tree': display_mode = 'animation'; print("Ritorno all'ultimo frame animazione")
        elif display_mode == 'animation':
            if current_frame_index > 0: current_frame_index -= 1
        update_display()
    def go_home(event):
        nonlocal current_frame_index, display_mode; pause_animation()
        current_frame_index = 0; display_mode = 'animation'
        print("Reset alla visualizzazione iniziale.")
        update_display()

    # 13. Creazione Oggetto Animazione (invariato)
    ani = animation.FuncAnimation(fig, animation_step, frames=total_frames, interval=1500, repeat=False)

    # 14. Creazione e Posizionamento Pulsanti (invariato)
    btn_h = 0.04; btn_w = 0.08; spacing = 0.02
    total_width_buttons = 4 * btn_w + 3 * spacing; start_x_buttons = 0.5 - total_width_buttons / 2
    btn_bottom_pos = 0.03
    ax_home = fig.add_axes ([start_x_buttons, btn_bottom_pos, btn_w, btn_h])
    ax_prev = fig.add_axes ([start_x_buttons + btn_w + spacing, btn_bottom_pos, btn_w, btn_h])
    ax_pause = fig.add_axes([start_x_buttons + 2 * (btn_w + spacing), btn_bottom_pos, btn_w, btn_h])
    ax_next = fig.add_axes ([start_x_buttons + 3 * (btn_w + spacing), btn_bottom_pos, btn_w, btn_h])
    fig._btn_home = Button(ax_home, 'Reset'); fig._btn_prev = Button(ax_prev, '< Prev')
    fig._btn_pause = Button(ax_pause, 'Resume'); fig._btn_next = Button(ax_next, 'Next >')
    fig._btn_home.on_clicked(go_home); fig._btn_prev.on_clicked(go_prev)
    fig._btn_pause.on_clicked(toggle_pause); fig._btn_next.on_clicked(go_next)

    # 15. Disegno Stato Iniziale e Avvio GUI
    update_display()
    plt.show()


# --- Funzione per Input Grafo Utente (MODIFICATA) ---
def get_user_graph():
    """Mostra una finestra per inserire grafo e scegliere tipo (diretto/non diretto)."""
    # Usiamo un dizionario condiviso per ritornare i risultati
    result_data = {'graph': None, 'is_directed': True} # Default a diretto

    input_fig, ax = plt.subplots(figsize=(8, 4.5)) # Leggermente più alta per checkbox
    input_fig.canvas.manager.set_window_title('Definisci Grafo')
    plt.subplots_adjust(bottom=0.45, top=0.9) # Più spazio sotto
    ax.axis('off')
    instructions = ("Inserisci il grafo come dizionario Python (liste di adiacenza).\n"
                    "Es: {'A': ['B', 'D'], 'B': ['E'], 'C': [], 'D': ['A']}")
    plt.text(0.05, 0.95, instructions, ha='left', va='top', wrap=True, fontsize=9)
    ax_box = plt.axes([0.1, 0.30, 0.8, 0.15]) # Textbox
    default_graph_str = "{'A': ['B', 'D'], 'B': ['E'], 'C': ['F', 'G'], 'D': ['B', 'H'], 'E': ['A', 'H'], 'F': ['C', 'G'], 'G': [], 'H': ['I'], 'I': ['H']}"
    text_box = TextBox(ax_box, '', initial=default_graph_str, textalignment="left")

    # --- Checkbox per Diretto/Non Diretto ---
    ax_check = plt.axes([0.1, 0.18, 0.3, 0.08]) # Posizione checkbox
    # Stato iniziale: Diretto è selezionato (True)
    check = CheckButtons(ax_check, [' Diretto'], [result_data['is_directed']])
    def func(label):
        # Aggiorna lo stato nel dizionario quando il checkbox cambia
        result_data['is_directed'] = check.get_status()[0]
        print(f"Tipo grafo impostato a: {'Diretto' if result_data['is_directed'] else 'Non Diretto'}")
    check.on_clicked(func)
    # ----------------------------------------

    ax_submit = plt.axes([0.4, 0.05, 0.2, 0.075]) # Bottone Submit
    btn_submit = Button(ax_submit, 'Esegui DFS')
    error_label = plt.text(0.5, 0.13, '', ha='center', va='center', color='red', fontsize=9) # Etichetta errore

    def submit(event):
        graph_text = text_box.text; error_label.set_text('')
        try:
            parsed_graph = ast.literal_eval(graph_text)
            if not isinstance(parsed_graph, dict): raise TypeError("Input non è un dizionario.")
            valid_graph = {}; all_nodes_check = set()
            for node, neighbors in parsed_graph.items():
                all_nodes_check.add(node)
                if not isinstance(neighbors, (list, tuple, set)):
                     raise TypeError(f"Vicini di '{node}' non validi.")
                valid_graph[node] = list(neighbors); all_nodes_check.update(neighbors)
            for n in all_nodes_check:
                if n not in valid_graph: valid_graph[n] = []
            print("Grafo inserito valido:", valid_graph)
            result_data['graph'] = valid_graph # Memorizza grafo nel dizionario
            plt.close(input_fig) # Chiude finestra input
        except (SyntaxError, ValueError, TypeError) as e:
            error_message = f"Errore formato:\n{e}"; print(error_message)
            error_label.set_text(error_message); input_fig.canvas.draw_idle()
        except Exception as e:
            error_message = f"Errore inatteso:\n{e}"; print(error_message)
            error_label.set_text(error_message); input_fig.canvas.draw_idle()

    btn_submit.on_clicked(submit)
    plt.show(block=True)

    # Ritorna il grafo e lo stato del checkbox
    return result_data['graph'], result_data['is_directed']


# --- Esecuzione Principale Modificata ---
if __name__ == "__main__":
    # 1. Ottieni grafo e tipo dall'utente
    user_defined_graph, is_directed_choice = get_user_graph()

    # 2. Procedi solo se grafo valido
    if user_defined_graph is not None:
        # 3. Esegui DFS
        graph_to_process = copy.deepcopy(user_defined_graph)
        captured_frames, final_edge_types_result = dfs_classify_edges_animated(graph_to_process)

        # 4. Avvia animazione se ci sono frame
        if captured_frames:
            print("\nAvvio animazione DFS...")
            # Passa il tipo di grafo scelto ad animate_dfs
            animate_dfs(user_defined_graph, is_directed_choice, captured_frames, final_edge_types_result)
            print("Finestra animazione chiusa.")
        else:
            print("Nessun frame catturato per l'animazione.")
    else:
        print("Nessun grafo valido fornito. Uscita.")
        sys.exit()

# --- END OF FILE dfs_directed_choice.py ---