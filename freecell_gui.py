import tkinter as tk
from tkinter import messagebox
import copy
from freecell_solver import FreeCellSolver  # Import the solver from another file

# Define card suits and values
suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

# Helper function to create a deck sorted by suit
def create_deck_by_suit():
    return {suit: [f"{value} of {suit}" for value in values] for suit in suits}

# GUI Class for FreeCell
class FreeCellGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FreeCell Solver")
        self.deck_by_suit = create_deck_by_suit()
        self.tableau = [[] for _ in range(8)]
        self.free_cells = [None for _ in range(4)]
        self.foundations = [[] for _ in range(4)]
        self.card_widgets = {}
        self.selected_card = None
        self.selected_pile = None

        # Create UI components
        self.create_widgets()

    def create_widgets(self):
        # Create free cells
        self.free_cell_frames = []
        for i in range(4):
            frame = tk.Frame(self.root, width=100, height=50, borderwidth=1, relief="solid")
            frame.grid(row=0, column=i, padx=5, pady=5)
            self.free_cell_frames.append(frame)
            frame.bind("<Button-1>", lambda event, cell=i: self.place_card_in_free_cell(event, cell))

        # Create suit piles
        self.suit_frames = {}
        for i, suit in enumerate(suits):
            frame = tk.Frame(self.root, width=100, height=200, borderwidth=1, relief="solid")
            frame.grid(row=0, column=i + 4, padx=5, pady=5)
            self.suit_frames[suit] = frame
            self.display_suit_pile(frame, suit)

        # Create tableau frames
        self.tableau_frames = [tk.Frame(self.root, width=100, height=400, borderwidth=1, relief="solid") for _ in range(8)]
        for i, frame in enumerate(self.tableau_frames):
            frame.grid(row=1, column=i, padx=5, pady=5, sticky="n")
            frame.grid_propagate(False)  # Prevent the frame from shrinking
            frame.columnconfigure(0, weight=1)  # Keep columns consistent

        self.solve_button = tk.Button(self.root, text="Solve", command=self.solve_game)
        self.solve_button.grid(row=2, column=0, columnspan=8, pady=10)

        self.reset_button = tk.Button(self.root, text="Reset", command=self.reset_game)
        self.reset_button.grid(row=3, column=0, columnspan=8, pady=10)

    def display_suit_pile(self, frame, suit):
        # Display all cards in the suit pile
        for card in self.deck_by_suit[suit]:
            label = tk.Label(frame, text=card)
            label.pack(anchor="w", padx=2, pady=2)
            label.bind("<Button-1>", lambda event, l=label, s=suit: self.start_drag(event, l, s))
            self.card_widgets[label] = (suit, card)

    def start_drag(self, event, label, suit):
        self.selected_card = label
        self.selected_pile = suit
        label.config(bg="yellow")
        self.root.bind("<B1-Motion>", self.drag_card)
        self.root.bind("<ButtonRelease-1>", self.drop_card)

    def drag_card(self, event):
        if self.selected_card:
            self.selected_card.place(x=event.x_root - self.root.winfo_rootx(), y=event.y_root - self.root.winfo_rooty())

    def drop_card(self, event):
        if self.selected_card:
            dropped = False
            for i, frame in enumerate(self.tableau_frames):
                if frame.winfo_rootx() < event.x_root < frame.winfo_rootx() + frame.winfo_width():
                    self.place_card_in_tableau(i)
                    dropped = True
                    break

            if not dropped:
                for i, frame in enumerate(self.free_cell_frames):
                    if frame.winfo_rootx() < event.x_root < frame.winfo_rootx() + frame.winfo_width():
                        self.place_card_in_free_cell(None, i)
                        dropped = True
                        break

            if not dropped:
                self.selected_card.place_forget()
                self.selected_card.pack()

            self.selected_card.config(bg="white")
            self.selected_card = None
            self.selected_pile = None

        self.root.unbind("<B1-Motion>")
        self.root.unbind("<ButtonRelease-1>")

    def place_card_in_tableau(self, col):
        if self.selected_card:
            suit, card = self.card_widgets[self.selected_card]
            self.tableau[col].append(card)
            self.selected_card.pack_forget()
            label = tk.Label(self.tableau_frames[col], text=card)
            label.pack(anchor="w", padx=2, pady=2)
            label.bind("<Button-1>", lambda event, l=label, c=col: self.select_tableau_card(event, l, c))
            self.card_widgets[label] = (col, card)

    def place_card_in_free_cell(self, event, cell):
        if self.selected_card and self.free_cells[cell] is None:
            suit, card = self.card_widgets[self.selected_card]
            self.free_cells[cell] = card
            self.selected_card.pack_forget()
            label = tk.Label(self.free_cell_frames[cell], text=card)
            label.pack()
            label.bind("<Button-1>", lambda event, l=label, c=cell: self.select_free_cell_card(event, l, c))
            self.card_widgets[label] = (cell, card)
            self.selected_card = None

    def solve_game(self):
        solver = FreeCellSolver(self.tableau, self.free_cells, self.foundations)
        solution = solver.solve()

        if solution:
            steps = [f"{move[0]} from {move[1]} to {move[2]}" for move in solution]
            messagebox.showinfo("Solution", "\n".join(steps))
        else:
            messagebox.showinfo("Solution", "No solution found")

    def reset_game(self):
        self.deck_by_suit = create_deck_by_suit()
        self.tableau = [[] for _ in range(8)]
        self.free_cells = [None for _ in range(4)]
        for frame in self.tableau_frames:
            for widget in frame.winfo_children():
                widget.destroy()
        for frame in self.free_cell_frames:
            for widget in frame.winfo_children():
                widget.destroy()
        for suit, frame in self.suit_frames.items():
            for widget in frame.winfo_children():
                widget.destroy()
            self.display_suit_pile(frame, suit)
        self.card_widgets.clear()
        self.selected_card = None
        self.selected_pile = None

if __name__ == "__main__":
    root = tk.Tk()
    app = FreeCellGUI(root)
    root.mainloop()
