import copy

# Define card suits and values
suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

class FreeCellSolver:
    def __init__(self, tableau, free_cells, foundations):
        self.initial_tableau = copy.deepcopy(tableau)
        self.initial_free_cells = copy.deepcopy(free_cells)
        self.foundations = foundations
        self.moves = []
        self.visited_states = set()  # Set to keep track of visited states

    def solve(self):
        tableau = copy.deepcopy(self.initial_tableau)
        free_cells = copy.deepcopy(self.initial_free_cells)
        if self.dfs(tableau, free_cells, 0):
            return self.moves
        return None

    def dfs(self, tableau, free_cells, depth):
        if self.is_solved():
            print("Solution found!")
            return True

        if depth > 100:  # Limit depth to avoid infinite recursion
            print("Depth limit reached, returning to previous state.")
            return False

        state_hash = self.hash_state(tableau, free_cells, self.foundations)
        if state_hash in self.visited_states:
            print("State already visited, skipping...")
            return False

        self.visited_states.add(state_hash)

        for move in self.valid_moves(tableau, free_cells):
            tableau_copy = copy.deepcopy(tableau)
            free_cells_copy = copy.deepcopy(free_cells)
            self.make_move(move, tableau_copy, free_cells_copy)

            self.moves.append(move)
            print(f"Trying move: {move}")
            if self.dfs(tableau_copy, free_cells_copy, depth + 1):
                return True
            print(f"Backtracking from move: {move}")
            self.moves.pop()

        return False

    def is_solved(self):
        # The game is solved if all foundations contain 13 cards
        return all(len(foundation) == 13 for foundation in self.foundations)

    def hash_state(self, tableau, free_cells, foundations):
        # Create a unique hashable representation of the state
        tableau_tuple = tuple(tuple(col) for col in tableau)
        free_cells_tuple = tuple(free_cells)
        foundations_tuple = tuple(tuple(foundation) for foundation in foundations)
        return (tableau_tuple, free_cells_tuple, foundations_tuple)

    def valid_moves(self, tableau, free_cells):
        moves = []

        # Move from tableau to free cell
        for i, col in enumerate(tableau):
            if col and None in free_cells:
                free_cell_idx = free_cells.index(None)
                moves.append(('T->F', i, free_cell_idx, col[-1]))

        # Move from free cell to tableau
        for i, card in enumerate(free_cells):
            if card:
                for j, col in enumerate(tableau):
                    if self.can_place(card, col):
                        moves.append(('F->T', i, j, card))

        # Move between tableau columns
        for i, col in enumerate(tableau):
            if col:
                for j, target_col in enumerate(tableau):
                    if i != j and self.can_place(col[-1], target_col):
                        moves.append(('T->T', i, j, col[-1]))

        # Move from tableau to foundation
        for i, col in enumerate(tableau):
            if col and self.can_place_in_foundation(col[-1]):
                moves.append(('T->Fnd', i, col[-1]))

        # Move from free cell to foundation
        for i, card in enumerate(free_cells):
            if card and self.can_place_in_foundation(card):
                moves.append(('F->Fnd', i, card))

        return moves

    def can_place(self, card, column):
        if not column:
            return True  # Can place any card in an empty column
        top_card = column[-1]
        card_value, card_suit = card.split(' of ')
        top_value, top_suit = top_card.split(' of ')
        value_order = values.index(card_value)
        top_value_order = values.index(top_value)

        # Different color and descending order
        return (value_order + 1 == top_value_order) and ((card_suit in ['Hearts', 'Diamonds']) != (top_suit in ['Hearts', 'Diamonds']))

    def can_place_in_foundation(self, card):
        value, suit = card.split(' of ')
        index = suits.index(suit)
        if not self.foundations[index]:
            return value == 'A'
        last_value = self.foundations[index][-1].split(' of ')[0]
        return values.index(last_value) + 1 == values.index(value)

    def make_move(self, move, tableau, free_cells):
        move_type = move[0]

        if move_type == 'T->F':
            src, dest, card = move[1], move[2], move[3]
            free_cells[dest] = tableau[src].pop()
        elif move_type == 'F->T':
            src, dest, card = move[1], move[2], move[3]
            tableau[dest].append(free_cells[src])
            free_cells[src] = None
        elif move_type == 'T->T':
            src, dest, card = move[1], move[2], move[3]
            tableau[dest].append(tableau[src].pop())
        elif move_type == 'T->Fnd':
            src, card = move[1], move[2]
            suit = card.split(' of ')[1]
            self.foundations[suits.index(suit)].append(tableau[src].pop())
        elif move_type == 'F->Fnd':
            src, card = move[1], move[2]
            suit = card.split(' of ')[1]
            self.foundations[suits.index(suit)].append(free_cells[src])
            free_cells[src] = None
