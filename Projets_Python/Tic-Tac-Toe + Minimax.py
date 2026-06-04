

import math
import time
import tkinter as tk
from tkinter import messagebox

# ============================================================
#  CONSTANTES
# ============================================================
PLAYER_X = 'X'   # Joueur humain
PLAYER_O = 'O'   # Ordinateur (IA)
EMPTY    = ' '   # Case vide


# ============================================================
#  PARTIE 1 : AFFICHAGE DU PLATEAU (terminal)
# ============================================================
def print_board(board):
    """Affiche le plateau Tic-Tac-Toe dans la console."""
    for row in board:
        print("|".join(row))
        print("-" * 5)


# ============================================================
#  PARTIE 2 : VÉRIFICATION DE L'ÉTAT TERMINAL
#  Retourne True si le jeu est terminé (victoire ou match nul)
# ============================================================
def is_game_over(board):
    # Vérification des lignes
    for row in board:
        if row.count(row[0]) == 3 and row[0] != EMPTY:
            return True

    # Vérification des colonnes
    for col in range(3):
        if (board[0][col] == board[1][col] == board[2][col]
                and board[0][col] != EMPTY):
            return True

    # Vérification des diagonales
    if (board[0][0] == board[1][1] == board[2][2] != EMPTY):
        return True
    if (board[0][2] == board[1][1] == board[2][0] != EMPTY):
        return True

    # Match nul : toutes les cases remplies
    if all(cell != EMPTY for row in board for cell in row):
        return True

    return False


# ============================================================
#  PARTIE 3 : ÉVALUATION HEURISTIQUE DU PLATEAU
#  +1 si O gagne, -1 si X gagne, 0 sinon
# ============================================================
def evaluate_board(board):
    # Vérification des lignes
    for row in board:
        if row.count(PLAYER_O) == 3:
            return 1    # O gagne
        if row.count(PLAYER_X) == 3:
            return -1   # X gagne

    # Vérification des colonnes
    for col in range(3):
        if (board[0][col] == board[1][col] == board[2][col]
                and board[0][col] != EMPTY):
            return 1 if board[0][col] == PLAYER_O else -1

    # Vérification des diagonales
    if board[0][0] == board[1][1] == board[2][2] != EMPTY:
        return 1 if board[1][1] == PLAYER_O else -1
    if board[0][2] == board[1][1] == board[2][0] != EMPTY:
        return 1 if board[1][1] == PLAYER_O else -1

    return 0   # Match nul ou jeu en cours


# ============================================================
#  PARTIE 4 : ALGORITHME MINIMAX
#  is_maximizing = True  → c'est le tour de O (ordinateur)
#  is_maximizing = False → c'est le tour de X (humain)
# ============================================================
def minimax(board, depth, is_maximizing):
    """
    Algorithme Minimax récursif.
    - Explore tous les coups possibles
    - Retourne le meilleur score pour le joueur actuel
    """
    # Cas de base : état terminal
    if is_game_over(board):
        return evaluate_board(board)

    if is_maximizing:
        # Joueur O (ordinateur) maximise son score
        best_score = -math.inf
        for i in range(3):
            for j in range(3):
                if board[i][j] == EMPTY:
                    board[i][j] = PLAYER_O
                    score = minimax(board, depth + 1, False)
                    board[i][j] = EMPTY
                    best_score = max(score, best_score)
        return best_score
    else:
        # Joueur X (humain) minimise le score
        best_score = math.inf
        for i in range(3):
            for j in range(3):
                if board[i][j] == EMPTY:
                    board[i][j] = PLAYER_X
                    score = minimax(board, depth + 1, True)
                    board[i][j] = EMPTY
                    best_score = min(score, best_score)
        return best_score


# ============================================================
#  PARTIE 5 : MINIMAX AVEC ÉLAGAGE ALPHA-BETA (BONUS)
#  Plus efficace : élimine les branches inutiles
# ============================================================
def minimax_alpha_beta(board, depth, is_maximizing, alpha, beta):
    """
    Minimax avec élagage Alpha-Beta.
    alpha = meilleur score garanti pour MAX
    beta  = meilleur score garanti pour MIN
    """
    if is_game_over(board):
        return evaluate_board(board)

    if is_maximizing:
        best_score = -math.inf
        for i in range(3):
            for j in range(3):
                if board[i][j] == EMPTY:
                    board[i][j] = PLAYER_O
                    score = minimax_alpha_beta(board, depth + 1, False, alpha, beta)
                    board[i][j] = EMPTY
                    best_score = max(score, best_score)
                    alpha = max(alpha, best_score)
                    if beta <= alpha:
                        break   # Élagage Beta
        return best_score
    else:
        best_score = math.inf
        for i in range(3):
            for j in range(3):
                if board[i][j] == EMPTY:
                    board[i][j] = PLAYER_X
                    score = minimax_alpha_beta(board, depth + 1, True, alpha, beta)
                    board[i][j] = EMPTY
                    best_score = min(score, best_score)
                    beta = min(beta, best_score)
                    if beta <= alpha:
                        break   # Élagage Alpha
        return best_score


# ============================================================
#  PARTIE 6 : TROUVER LE MEILLEUR COUP POUR L'ORDINATEUR
# ============================================================
def find_best_move(board, use_alpha_beta=True):
    """
    Trouve le meilleur coup pour l'ordinateur (PLAYER_O).
    Retourne (i, j) = position du meilleur coup.
    """
    best_score = -math.inf
    move       = (-1, -1)

    start_time = time.time()

    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                board[i][j] = PLAYER_O

                if use_alpha_beta:
                    score = minimax_alpha_beta(board, 0, False,
                                               -math.inf, math.inf)
                else:
                    score = minimax(board, 0, False)

                board[i][j] = EMPTY

                if score > best_score:
                    best_score = score
                    move       = (i, j)

    elapsed = time.time() - start_time
    print(f"[IA] Meilleur coup : {move}  |  Score : {best_score}  "
          f"|  Temps de calcul : {elapsed*1000:.2f} ms")
    return move


# ============================================================
#  PARTIE 7 : JEU EN MODE TERMINAL (Console)
# ============================================================
def play_terminal():
    """Lance une partie de Tic-Tac-Toe dans le terminal."""
    board = [[EMPTY] * 3 for _ in range(3)]

    print("\n" + "="*40)
    print("   Bienvenue au Tic-Tac-Toe !")
    print("   Vous jouez X, l'IA joue O")
    print("   Entrez ligne et colonne (0, 1 ou 2)")
    print("="*40 + "\n")
    print_board(board)

    while not is_game_over(board):

        # --- Tour du joueur X (humain) ---
        while True:
            try:
                x, y = map(int, input(
                    "Entrez votre coup (ligne colonne) : ").split())
                if board[x][y] == EMPTY:
                    board[x][y] = PLAYER_X
                    break
                else:
                    print("Case déjà occupée ! Réessayez.")
            except (ValueError, IndexError):
                print("Entrée invalide ! Entrez deux chiffres (0, 1 ou 2).")

        print_board(board)

        if is_game_over(board):
            break

        # --- Tour de l'ordinateur O ---
        print("Tour de l'ordinateur...")
        move = find_best_move(board)
        if move != (-1, -1):
            board[move[0]][move[1]] = PLAYER_O
        print_board(board)

    # --- Résultat final ---
    result = evaluate_board(board)
    print("\n" + "="*40)
    if result == 1:
        print("   L'ordinateur (O) gagne !")
    elif result == -1:
        print("   Vous (X) gagnez !")
    else:
        print("   Match nul !")
    print("="*40 + "\n")


# ============================================================
#  PARTIE 8 : INTERFACE GRAPHIQUE TKINTER (GUI)
# ============================================================
class TicTacToeGUI:
    def __init__(self, root):
        self.root  = root
        self.root.title("Tic-Tac-Toe — Minimax IA")
        self.root.resizable(False, False)
        self.board = [[EMPTY] * 3 for _ in range(3)]
        self.buttons = [[None]*3 for _ in range(3)]
        self.game_over = False
        self._build_ui()

    def _build_ui(self):
        # Titre
        tk.Label(self.root, text="Tic-Tac-Toe  —  Minimax IA",
                 font=("Helvetica", 16, "bold"),
                 bg="#1A237E", fg="white",
                 padx=10, pady=8).grid(row=0, column=0,
                                        columnspan=3, sticky="ew")

        # Info joueur
        self.info_label = tk.Label(
            self.root,
            text="Votre tour (X)",
            font=("Helvetica", 12),
            bg="#E3F2FD", fg="#1A237E",
            pady=5)
        self.info_label.grid(row=1, column=0, columnspan=3, sticky="ew")

        # Plateau de jeu
        for i in range(3):
            for j in range(3):
                btn = tk.Button(
                    self.root, text=" ",
                    font=("Helvetica", 36, "bold"),
                    width=4, height=2,
                    bg="#FFFFFF",
                    activebackground="#E3F2FD",
                    relief="groove",
                    command=lambda r=i, c=j: self._on_click(r, c)
                )
                btn.grid(row=i+2, column=j, padx=4, pady=4)
                self.buttons[i][j] = btn

        # Bouton rejouer
        tk.Button(self.root, text="🔄  Nouvelle Partie",
                  font=("Helvetica", 11),
                  bg="#1565C0", fg="white",
                  padx=10, pady=5,
                  command=self._reset).grid(
                      row=5, column=0, columnspan=3,
                      pady=8, sticky="ew", padx=10)

    def _on_click(self, row, col):
        """Gère le clic du joueur humain."""
        if self.game_over or self.board[row][col] != EMPTY:
            return

        # Coup du joueur X
        self.board[row][col] = PLAYER_X
        self.buttons[row][col].config(text="X", fg="#D32F2F",
                                       bg="#FFEBEE")
        self.info_label.config(text="Tour de l'IA (O)...")

        if self._check_end():
            return

        # Coup de l'IA O
        self.root.after(300, self._ai_move)

    def _ai_move(self):
        """Calcule et joue le coup de l'IA."""
        move = find_best_move(self.board)
        if move != (-1, -1):
            i, j = move
            self.board[i][j] = PLAYER_O
            self.buttons[i][j].config(text="O", fg="#1565C0",
                                       bg="#E3F2FD")
        self.info_label.config(text="Votre tour (X)")
        self._check_end()

    def _check_end(self):
        """Vérifie si la partie est terminée."""
        if is_game_over(self.board):
            self.game_over = True
            result = evaluate_board(self.board)
            if result == 1:
                msg = "L'IA (O) gagne !"
                self.info_label.config(text="❌ L'IA gagne !",
                                        bg="#FFCDD2", fg="#B71C1C")
            elif result == -1:
                msg = "Vous (X) gagnez !"
                self.info_label.config(text="🎉 Vous gagnez !",
                                        bg="#C8E6C9", fg="#1B5E20")
            else:
                msg = "Match nul !"
                self.info_label.config(text="🤝 Match nul !",
                                        bg="#FFF9C4", fg="#F57F17")

            # Désactiver tous les boutons
            for i in range(3):
                for j in range(3):
                    self.buttons[i][j].config(state="disabled")

            messagebox.showinfo("Fin de partie", msg)
            return True
        return False

    def _reset(self):
        """Remet le jeu à zéro."""
        self.board     = [[EMPTY]*3 for _ in range(3)]
        self.game_over = False
        self.info_label.config(text="Votre tour (X)",
                                bg="#E3F2FD", fg="#1A237E")
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(
                    text=" ", fg="black", bg="white",
                    state="normal")


# ============================================================
#  POINT D'ENTRÉE PRINCIPAL
# ============================================================
def main():
    board = [[EMPTY] * 3 for _ in range(3)]

    print("="*40)
    print("   Welcome to Tic Tac Toe!")
    print("="*40)
    print_board(board)

    while not is_game_over(board):

        # Tour du joueur X
        while True:
            try:
                x, y = map(int, input(
                    "Enter your move (row and column): ").split())
                if board[x][y] == EMPTY:
                    board[x][y] = PLAYER_X
                    break
                else:
                    print("Cell is already occupied! Try again.")
            except (ValueError, IndexError):
                print("Invalid input! Please enter row and column "
                      "as two numbers (0, 1, or 2).")

        print_board(board)
        if is_game_over(board):
            break

        # Tour de l'ordinateur O
        print("Computer's turn:")
        move = find_best_move(board)
        if move != (-1, -1):
            board[move[0]][move[1]] = PLAYER_O
        print_board(board)

    # Résultat
    result = evaluate_board(board)
    if result == 1:
        print("Computer (O) wins!")
    elif result == -1:
        print("You (X) win!")
    else:
        print("It's a draw!")


if __name__ == "__main__":
    # ---- Lance d'abord la version terminal ----
    print("\nChoisissez le mode :")
    print("1 → Terminal (console)")
    print("2 → Interface graphique (GUI)")
    choix = input("Votre choix (1 ou 2) : ").strip()

    if choix == "2":
        root = tk.Tk()
        app  = TicTacToeGUI(root)
        root.mainloop()
    else:
        main()