
import time
import tracemalloc
import random
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from collections import deque

# ============================================================
#  PARTIE 1 : CONFIGURATION DU LABYRINTHE DE BASE (4x4)
# ============================================================

# 0 = case libre (.),  1 = mur (#)
maze = {
    (0, 0): 0, (0, 1): 1, (0, 2): 0, (0, 3): 0,
    (1, 0): 0, (1, 1): 1, (1, 2): 0, (1, 3): 1,
    (2, 0): 0, (2, 1): 0, (2, 2): 0, (2, 3): 1,
    (3, 0): 0, (3, 1): 1, (3, 2): 0, (3, 3): 0,
}

# Directions possibles : haut, bas, gauche, droite
directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

# Point de départ et d'arrivée
start = (0, 0)
goal  = (3, 3)


# ============================================================
#  FONCTION : Voisins valides d'un nœud
# ============================================================
def get_neighbors(node, maze_dict):
    x, y = node
    neighbors = []
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if (nx, ny) in maze_dict and maze_dict[(nx, ny)] == 0:
            neighbors.append((nx, ny))
    return neighbors


# ============================================================
#  FONCTION : Affichage du labyrinthe dans le terminal
# ============================================================
def print_maze(maze_dict, size=4, path=None):
    for x in range(size):
        for y in range(size):
            if path and (x, y) in path:
                print("P", end=" ")
            elif maze_dict[(x, y)] == 1:
                print("#", end=" ")
            else:
                print(".", end=" ")
        print()


# ============================================================
#  PARTIE 2 : ALGORITHME BFS
#  Explore niveau par niveau avec une file
# ============================================================
def bfs(start, goal, maze_dict=None):
    if maze_dict is None:
        maze_dict = maze

    queue     = deque([start])          # File d'attente
    came_from = {start: None}           # Pour reconstruire le chemin

    while queue:
        current = queue.popleft()       # Prend le premier élément (FIFO)
        if current == goal:
            break
        for neighbor in get_neighbors(current, maze_dict):
            if neighbor not in came_from:
                came_from[neighbor] = current
                queue.append(neighbor)

    # Reconstruction du chemin
    if goal not in came_from:
        return []   # Pas de chemin trouvé

    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = came_from[node]
    return path[::-1]   # Inverser pour avoir start → goal


# ============================================================
#  PARTIE 2 : ALGORITHME DFS
#  Explore en profondeur avec une pile
# ============================================================
def dfs(start, goal, maze_dict=None):
    if maze_dict is None:
        maze_dict = maze

    stack     = [start]                 # Pile
    came_from = {start: None}           # Pour reconstruire le chemin

    while stack:
        current = stack.pop()           # Prend le dernier élément (LIFO)
        if current == goal:
            break
        for neighbor in get_neighbors(current, maze_dict):
            if neighbor not in came_from:
                came_from[neighbor] = current
                stack.append(neighbor)

    # Reconstruction du chemin
    if goal not in came_from:
        return []

    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = came_from[node]
    return path[::-1]


# ============================================================
#  PARTIE 3 : MESURE DES PERFORMANCES
#  Mesure le temps d'exécution et la mémoire utilisée
# ============================================================
def measure_performance(algorithm, start, goal, maze_dict=None):
    if maze_dict is None:
        maze_dict = maze

    # Mesure du temps
    start_time = time.time()

    # Mesure de la mémoire
    tracemalloc.start()

    path = algorithm(start, goal, maze_dict)

    # Arrêt des mesures
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    elapsed_time = time.time() - start_time

    return path, elapsed_time, peak_mem / 1024   # Mémoire en KB


# ============================================================
#  PARTIE 4 : GÉNÉRATION D'UN LABYRINTHE ALÉATOIRE
# ============================================================
def generate_random_maze(rows, cols, wall_prob=0.3):
    """Génère un labyrinthe aléatoire de taille rows x cols."""
    maze_dict = {}
    for x in range(rows):
        for y in range(cols):
            # Le départ et l'arrivée sont toujours libres
            if (x, y) == (0, 0) or (x, y) == (rows-1, cols-1):
                maze_dict[(x, y)] = 0
            else:
                maze_dict[(x, y)] = 1 if random.random() < wall_prob else 0
    return maze_dict


# ============================================================
#  PARTIE 5 : VISUALISATIONS MATPLOTLIB
# ============================================================
def plot_comparaison(results):
    """Affiche 3 graphiques : temps, mémoire, longueur du chemin."""
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(14, 5))

    names   = [res[0] for res in results]
    times   = [res[2] * 1000 for res in results]   # en millisecondes
    memory  = [res[3] for res in results]            # en KB
    lengths = [res[1] for res in results]            # nombre de nœuds

    # --- Graphique 1 : Temps d'exécution ---
    ax1.bar(names, times, color='skyblue')
    ax1.set_title("Temps d'exécution")
    ax1.set_ylabel("Millisecondes")
    ax1.grid(axis='y', linestyle='--')

    # --- Graphique 2 : Mémoire utilisée ---
    ax2.bar(names, memory, color='lightgreen')
    ax2.set_title("Mémoire utilisée")
    ax2.set_ylabel("Kilobytes")
    ax2.grid(axis='y', linestyle='--')

    # --- Graphique 3 : Longueur du chemin ---
    ax3.bar(names, lengths, color='salmon')
    ax3.set_title("Longueur du chemin")
    ax3.set_ylabel("Nombre de nœuds")
    ax3.grid(axis='y', linestyle='--')

    plt.suptitle("Comparaison BFS vs DFS", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()


def plot_multiple_sizes():
    """Compare BFS et DFS sur des labyrinthes de tailles variées."""
    sizes       = [4, 8, 12, 16, 20]
    bfs_times   = []
    dfs_times   = []
    bfs_lengths = []
    dfs_lengths = []

    for s in sizes:
        maze_dict = generate_random_maze(s, s)
        s_start   = (0, 0)
        s_goal    = (s-1, s-1)

        _, bt, _ = measure_performance(bfs, s_start, s_goal, maze_dict)
        _, dt, _ = measure_performance(dfs, s_start, s_goal, maze_dict)

        bp = bfs(s_start, s_goal, maze_dict)
        dp = dfs(s_start, s_goal, maze_dict)

        bfs_times.append(bt * 1000)
        dfs_times.append(dt * 1000)
        bfs_lengths.append(len(bp))
        dfs_lengths.append(len(dp))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    ax1.plot(sizes, bfs_times, marker='o', label='BFS', color='blue')
    ax1.plot(sizes, dfs_times, marker='s', label='DFS', color='red')
    ax1.set_title("Temps d'exécution selon la taille")
    ax1.set_xlabel("Taille du labyrinthe (N x N)")
    ax1.set_ylabel("Millisecondes")
    ax1.legend()
    ax1.grid(True, linestyle='--')

    ax2.plot(sizes, bfs_lengths, marker='o', label='BFS', color='blue')
    ax2.plot(sizes, dfs_lengths, marker='s', label='DFS', color='red')
    ax2.set_title("Longueur du chemin selon la taille")
    ax2.set_xlabel("Taille du labyrinthe (N x N)")
    ax2.set_ylabel("Nombre de nœuds")
    ax2.legend()
    ax2.grid(True, linestyle='--')

    plt.suptitle("Analyse comparative BFS vs DFS - Tailles variées", fontsize=13)
    plt.tight_layout()
    plt.show()


# ============================================================
#  PARTIE 6 : INTERFACE GRAPHIQUE TKINTER (GUI)
# ============================================================
class MazeGUI:
    def __init__(self, root):
        self.root  = root
        self.root.title("Labyrinthe avec Algorithmes de Recherche")

        self.rows      = 10
        self.cols      = 11
        self.cell_size = 50
        self.maze_dict = {}
        self.path      = []

        self._build_controls()
        self._build_canvas()
        self.init_maze()

    def _build_controls(self):
        """Panneau de contrôle en haut."""
        ctrl = tk.Frame(self.root)
        ctrl.pack(side=tk.TOP, pady=5)

        tk.Label(ctrl, text="Hauteur:").grid(row=0, column=0)
        self.entry_rows = tk.Entry(ctrl, width=5)
        self.entry_rows.insert(0, "10")
        self.entry_rows.grid(row=0, column=1)

        tk.Label(ctrl, text="Largeur:").grid(row=1, column=0)
        self.entry_cols = tk.Entry(ctrl, width=5)
        self.entry_cols.insert(0, "11")
        self.entry_cols.grid(row=1, column=1)

        tk.Button(ctrl, text="Initialiser Labyrinthe",
                  command=self.init_maze).grid(row=2, column=0, columnspan=2, pady=3)

        tk.Label(ctrl, text="Algorithme (DFS, BFS):").grid(row=3, column=0)
        self.algo_var = tk.StringVar(value="bfs")
        self.entry_algo = tk.Entry(ctrl, textvariable=self.algo_var, width=8)
        self.entry_algo.grid(row=3, column=1)

        tk.Button(ctrl, text="Lancer l'Algorithme",
                  command=self.run_algorithm,
                  bg="#4CAF50", fg="white").grid(row=4, column=0, columnspan=2, pady=3)

    def _build_canvas(self):
        """Canvas pour dessiner le labyrinthe."""
        self.canvas = tk.Canvas(self.root,
                                width=self.cols * self.cell_size,
                                height=self.rows * self.cell_size,
                                bg="white")
        self.canvas.pack(padx=10, pady=10)

    def init_maze(self):
        """Génère et affiche un nouveau labyrinthe aléatoire."""
        try:
            self.rows = int(self.entry_rows.get())
            self.cols = int(self.entry_cols.get())
        except ValueError:
            pass

        self.maze_dict = generate_random_maze(self.rows, self.cols)
        self.path      = []

        self.canvas.config(width=self.cols * self.cell_size,
                           height=self.rows * self.cell_size)
        self.draw_maze()

    def draw_maze(self):
        """Dessine le labyrinthe sur le canvas."""
        self.canvas.delete("all")
        cs = self.cell_size

        for (x, y), val in self.maze_dict.items():
            x1, y1 = y * cs, x * cs
            x2, y2 = x1 + cs, y1 + cs

            if (x, y) in self.path:
                color = "yellow"           # Chemin trouvé
            elif (x, y) == (0, 0):
                color = "green"            # Départ
            elif (x, y) == (self.rows-1, self.cols-1):
                color = "red"              # Arrivée
            elif val == 1:
                color = "black"            # Mur
            else:
                color = "white"            # Case libre

            self.canvas.create_rectangle(x1, y1, x2, y2,
                                         fill=color, outline="gray")
            # Afficher les coordonnées
            if val == 0 and (x, y) not in self.path:
                self.canvas.create_text(x1 + cs//2, y1 + cs//2,
                                        text=f"{x},{y}", font=("Arial", 7),
                                        fill="gray")

    def run_algorithm(self):
        """Lance l'algorithme sélectionné et affiche le chemin."""
        algo_name = self.algo_var.get().lower().strip()
        s = (0, 0)
        g = (self.rows - 1, self.cols - 1)

        if algo_name == "bfs":
            self.path = bfs(s, g, self.maze_dict)
        elif algo_name == "dfs":
            self.path = dfs(s, g, self.maze_dict)
        else:
            self.path = []

        self.draw_maze()

        if self.path:
            print(f"[{algo_name.upper()}] Chemin trouvé : {len(self.path)} nœuds")
        else:
            print(f"[{algo_name.upper()}] Aucun chemin trouvé.")


# ============================================================
#  POINT D'ENTRÉE PRINCIPAL
# ============================================================
if __name__ == "__main__":

    # ---- TEST 1 : Labyrinthe 4x4 de base ----
    print("=" * 50)
    print("  Labyrinthe initial (4x4) :")
    print("=" * 50)
    print_maze(maze, size=4)

    bfs_path = bfs(start, goal)
    print("\nChemin BFS :")
    print_maze(maze, size=4, path=set(bfs_path))

    dfs_path = dfs(start, goal)
    print("\nChemin DFS :")
    print_maze(maze, size=4, path=set(dfs_path))

    # ---- TEST 2 : Mesure des performances ----
    print("\n" + "=" * 50)
    print("  Comparaison des performances :")
    print("=" * 50)
    print(f"{'Algorithme':<12} {'Temps (ms)':<15} {'Mémoire (KB)':<15} {'Longueur chemin'}")
    print("-" * 55)

    algorithms = [(bfs, "BFS"), (dfs, "DFS")]
    results    = []

    for algo, name in algorithms:
        path, t, mem = measure_performance(algo, start, goal)
        results.append((name, len(path), t, mem))
        print(f"{name:<12} {t*1000:<15.5f} {mem:<15.2f} {len(path)}")

    # ---- TEST 3 : Visualisations graphiques ----
    plot_comparaison(results)

    # ---- TEST 4 : Labyrinthes de tailles variées ----
    print("\n[INFO] Génération des graphiques multi-tailles...")
    plot_multiple_sizes()

    # ---- TEST 5 : Interface Graphique GUI ----
    print("\n[INFO] Lancement de l'interface graphique...")
    root = tk.Tk()
    app  = MazeGUI(root)
    root.mainloop()