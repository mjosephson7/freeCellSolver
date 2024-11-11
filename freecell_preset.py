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
        self.tableau = self.create_custom_tableau()  # Use a custom tableau configuration
        self.free_cells = [None for _ in range(4)]
        self.foundations = [[] for _ in range(4)]  # Four foundation piles
        self.card_widgets = {}
        self.selected_card = None
        self.selected_pile = None

        # Create UI components
        self.create_widgets()
        
    def create_custom_tableau(self):
        # Define the custom tableau configuration based on your screenshot
        print("Creating custom tableau...")
        return [
            ['5 of Diamonds', 'Q of Hearts', '7 of Spades', '7 of Clubs', '2 of Clubs', '5 of Hearts', '10 of Spades'],
            ['4 of Spades', 'A of Hearts', '4 of Hearts', '8 of Diamonds', '8 of Clubs', '8 of Spades', '10 of Hearts'],
            ['6 of Diamonds', '5 of Clubs', '10 of Clubs', '7 of Hearts', '6 of Clubs', '4 of Clubs', 'K of Diamonds'],
            ['9 of Diamonds', '2 of Hearts', 'Q of Spades', '3 of Hearts', 'Q of Diamonds', '7 of Diamonds', 'Q of Clubs'],
            ['A of Clubs', 'J of Spades', '8 of Hearts', '4 of Diamonds', 'J of Clubs', 'K of Hearts'],
            ['K of Clubs', 'A of Diamonds', '9 of Clubs', 'J of Diamonds', 'J of Hearts', 'K of Spades'],
            ['3 of Diamonds', '3 of Spades', 'A of Spades', '3 of Clubs', '9 of Spades', '2 of Spades'],
            ['5 of Spades', '6 of Spades', '9 of Hearts', '10 of Diamonds', '2 of Diamonds', '6 of Hearts']
        ]

    def create_widgets(self):
        print("Creating widgets...")
        # Create free cells
        self.free_cell_frames = []
        for i in range(4):
            frame = tk.Frame(self.root, width=100, height=50, borderwidth=1, relief="solid")
            frame.grid(row=0, column=i, padx=5, pady=5)
            self.free_cell_frames.append(frame)

        # Create foundation piles
        self.foundation_frames = []
        for i in range(4):
            frame = tk.Frame(self.root, width=100, height=200, borderwidth=1, relief="solid")
            frame.grid(row=0, column=i + 4, padx=5, pady=5)
            self.foundation_frames.append(frame)

        # Create tableau frames
        self.tableau_frames = [tk.Frame(self.root, width=100, height=400, borderwidth=1, relief="solid") for _ in range(8)]
        for i, frame in enumerate(self.tableau_frames):
            frame.grid(row=1, column=i, padx=5, pady=5, sticky="n")
            frame.grid_propagate(False)

        self.solve_button = tk.Button(self.root, text="Solve", command=self.solve_game)
        self.solve_button.grid(row=2, column=0, columnspan=8, pady=10)

        self.reset_button = tk.Button(self.root, text="Reset", command=self.reset_game)
        self.reset_button.grid(row=3, column=0, columnspan=8, pady=10)

        # Display the initial tableau
        self.display_tableau()

    def display_tableau(self):
        print("Displaying the tableau...")
        for i, col in enumerate(self.tableau):
            for card in col:
                label = tk.Label(self.tableau_frames[i], text=card)
                label.pack(anchor="w", padx=2, pady=2)
                label.bind("<Button-1>", lambda event, l=label, c=i: self.start_drag(event, l, c))
                self.card_widgets[label] = (i, card)

    def start_drag(self, event, label, col):
        self.selected_card = label
        self.selected_pile = col
        label.config(bg="yellow")
        print(f"Selected card: {label.cget('text')} from column {col}")
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
                    print(f"Dropping card in tableau column {i}")
                    self.place_card_in_tableau(i)
                    dropped = True
                    break

            if not dropped:
                for i, frame in enumerate(self.free_cell_frames):
                    if frame.winfo_rootx() < event.x_root < frame.winfo_rootx() + frame.winfo_width():
                        print(f"Dropping card in free cell {i}")
                        self.place_card_in_free_cell(None, i)
                        dropped = True
                        break

            if not dropped:
                for i, frame in enumerate(self.foundation_frames):
                    if frame.winfo_rootx() < event.x_root < frame.winfo_rootx() + frame.winfo_width():
                        print(f"Dropping card in foundation pile {i}")
                        self.place_card_in_foundation(i)
                        dropped = True
                        break

            if not dropped:
                print("Invalid drop location, returning card to original position")
                self.selected_card.place_forget()
                self.selected_card.pack()

            self.selected_card.config(bg="white")
            self.selected_card = None
            self.selected_pile = None

        self.root.unbind("<B1-Motion>")
        self.root.unbind("<ButtonRelease-1>")

    def place_card_in_tableau(self, col):
        if self.selected_card:
            old_col, card = self.card_widgets[self.selected_card]
            print(f"Moving card {card} from column {old_col} to column {col}")
            self.tableau[col].append(card)
            self.tableau[old_col].remove(card)
            self.selected_card.pack_forget()
            label = tk.Label(self.tableau_frames[col], text=card)
            label.pack(anchor="w", padx=2, pady=2)
            label.bind("<Button-1>", lambda event, l=label, c=col: self.start_drag(event, l, c))
            self.card_widgets[label] = (col, card)

    def place_card_in_free_cell(self, event, cell):
        if self.selected_card and self.free_cells[cell] is None:
            old_col, card = self.card_widgets[self.selected_card]
            print(f"Placing card {card} in free cell {cell}")
            self.free_cells[cell] = card
            self.tableau[old_col].remove(card)
            self.selected_card.pack_forget()
            label = tk.Label(self.free_cell_frames[cell], text=card)
            label.pack()
            label.bind("<Button-1>", lambda event, l=label, c=cell: self.select_free_cell_card(event, l, c))
            self.card_widgets[label] = (cell, card)
            self.selected_card = None

    def place_card_in_foundation(self, foundation_index):
        if self.selected_card:
            old_col, card = self.card_widgets[self.selected_card]
            suit = card.split(' of ')[1]
            foundation_suit = suits[foundation_index]
            if suit == foundation_suit and (not self.foundations[foundation_index] or
                values.index(self.foundations[foundation_index][-1].split(' of ')[0]) + 1 == values.index(card.split(' of ')[0])):
                print(f"Placing card {card} in foundation pile {foundation_index}")
                self.foundations[foundation_index].append(card)
                self.tableau[old_col].remove(card)
                self.selected_card.pack_forget()
                label = tk.Label(self.foundation_frames[foundation_index], text=card)
                label.pack(anchor="w", padx=2, pady=2)
                self.card_widgets.pop(self.selected_card, None)
                self.selected_card = None
            else:
                print("Invalid move to foundation")

    def solve_game(self):
        print("Solving the game...")
        solver = FreeCellSolver(self.tableau, self.free_cells, self.foundations)
        solution = solver.solve()

        if solution:
            steps = [f"Move card '{move[2]}' from {move[1]} to {move[3]}" for move in solution]
            messagebox.showinfo("Solution", "\n".join(steps))
            print("Solution found:")
            for step in steps:
                print(step)
        else:
            print("No solution found")
            messagebox.showinfo("Solution", "No solution found")

    def reset_game(self):
        print("Resetting the game...")
        self.tableau = self.create_custom_tableau()
        self.free_cells = [None for _ in range(4)]
        self.foundations = [[] for _ in range(4)]
        for frame in self.tableau_frames:
            for widget in frame.winfo_children():
                widget.destroy()
        for frame in self.free_cell_frames:
            for widget in frame.winfo_children():
                widget.destroy()
        for frame in self.foundation_frames:
            for widget in frame.winfo_children():
                widget.destroy()
        self.display_tableau()

if __name__ == "__main__":
    root = tk.Tk()
    app = FreeCellGUI(root)
    print("Starting FreeCell GUI...")
    root.mainloop()
