import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx

# === Costruzione grafo ===
edges = [
    (0, 1, 6), (0, 2, 7),
    (1, 2, 8), (1, 3, 5), (1, 4, -4),
    (2, 3, -3), (2, 4, 9),
    (3, 1, -2),
    (4, 0, 2), (4, 3, 7)
]

G = nx.DiGraph()
G.add_weighted_edges_from(edges)
pos = nx.shell_layout(G)

# === Precalcolo Bellman-Ford passo per passo ===
dist = {node: float('inf') for node in G.nodes}
dist[0] = 0

distances_history = []
updated_nodes_history = []
highlighted_edges = []

for i in range(len(G.nodes) - 1):
    updated = set()
    changed = False
    for u, v, data in G.edges(data=True):
        weight = data['weight']
        if dist[u] + weight < dist[v]:
            dist[v] = dist[u] + weight
            updated.add(v)
            distances_history.append(dist.copy())
            updated_nodes_history.append(updated.copy())
            highlighted_edges.append((u, v))
            changed = True
    if not changed:
        break

distances_history.append(dist.copy())
updated_nodes_history.append(set())
highlighted_edges.append(None)

# === Funzioni GUI ===
class BellmanFordGUI:
    def __init__(self, master):
        self.master = master
        master.title("Bellman-Ford Visualizer")
        master.minsize(700, 600)  # Imposta una dimensione minima della finestra

        self.step = 0
        self.running = False
        self.animating_edge = False

        # Bottoni in alto
        controls = tk.Frame(master, bg="#f0f0f0")
        controls.pack(side=tk.TOP, fill=tk.X, pady=5)

        style = ttk.Style()
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)

        self.play_button = ttk.Button(controls, text="▶️ Play", style="TButton", command=self.toggle_play)
        self.play_button.pack(side=tk.LEFT, padx=10)

        self.prev_button = ttk.Button(controls, text="⏮️ Indietro", style="TButton", command=self.step_back)
        self.prev_button.pack(side=tk.LEFT, padx=10)

        self.next_button = ttk.Button(controls, text="⏭️ Avanti", style="TButton", command=self.step_forward)
        self.next_button.pack(side=tk.LEFT, padx=10)

        # Setup Matplotlib Figure
        self.fig, self.ax = plt.subplots(figsize=(6, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)

        self.draw_step()

    def draw_step(self, animated=False):
        self.ax.clear()

        dist = distances_history[self.step]
        updated_nodes = updated_nodes_history[self.step]
        highlight_edge = highlighted_edges[self.step]

        node_labels = {
            node: f"{node}\n{dist[node] if dist[node] != float('inf') else '∞'}"
            for node in G.nodes
        }

        node_colors = [
            'lightgreen' if node in updated_nodes else 'skyblue'
            for node in G.nodes
        ]

        # Disegna archi base
        nx.draw_networkx_edges(G, pos, ax=self.ax, edge_color='gray', width=1.5, arrows=True)

        # Evidenzia arco aggiornato
        if highlight_edge and animated:
            self.animate_edge(highlight_edge)
        else:
            edge_colors = ['red' if (u, v) == highlight_edge else 'gray' for u, v in G.edges]
            nx.draw(G, pos, ax=self.ax, with_labels=True,
                    labels=node_labels, node_color=node_colors, node_size=1500,
                    edge_color=edge_colors, width=2, arrows=True)

        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=self.ax)

        self.ax.set_title(f"Step {self.step + 1}/{len(distances_history)}")
        self.canvas.draw()

    def animate_edge(self, edge):
        self.animating_edge = True
        u, v = edge
        x_start, y_start = pos[u]
        x_end, y_end = pos[v]
        steps = 10
        for i in range(steps + 1):
            self.ax.clear()
            # Static background
            nx.draw_networkx_edges(G, pos, ax=self.ax, edge_color='gray', width=1.5, arrows=True)

            dist = distances_history[self.step]
            updated_nodes = updated_nodes_history[self.step]
            node_labels = {
                node: f"{node}\n{dist[node] if dist[node] != float('inf') else '∞'}"
                for node in G.nodes
            }
            node_colors = [
                'lightgreen' if node in updated_nodes else 'skyblue'
                for node in G.nodes
            ]
            nx.draw_networkx_nodes(G, pos, ax=self.ax, node_color=node_colors, node_size=1500)
            nx.draw_networkx_labels(G, pos, labels=node_labels, ax=self.ax)

            edge_labels = nx.get_edge_attributes(G, 'weight')
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=self.ax)

            # Punto rosso in movimento
            x = x_start + (x_end - x_start) * (i / steps)
            y = y_start + (y_end - y_start) * (i / steps)
            self.ax.plot([x], [y], 'ro', markersize=8)

            self.ax.set_title(f"Step {self.step + 1}/{len(distances_history)}")
            self.canvas.draw()
            self.master.update()
            self.master.after(50)

        self.animating_edge = False

    def toggle_play(self):
        if not self.running:
            self.running = True
            self.play_button.config(text="⏸️ Pausa")
            self.auto_step()
        else:
            self.running = False
            self.play_button.config(text="▶️ Play")

    def auto_step(self):
        if self.running and self.step < len(distances_history) - 1:
            self.step += 1
            self.draw_step(animated=True)
            self.master.after(900, self.auto_step)
        else:
            self.running = False
            self.play_button.config(text="▶️ Play")

    def step_forward(self):
        if self.step < len(distances_history) - 1 and not self.animating_edge:
            self.step += 1
            self.draw_step(animated=True)

    def step_back(self):
        if self.step > 0 and not self.animating_edge:
            self.step -= 1
            self.draw_step()

# === Avvio GUI ===
root = tk.Tk()
gui = BellmanFordGUI(root)
root.mainloop()