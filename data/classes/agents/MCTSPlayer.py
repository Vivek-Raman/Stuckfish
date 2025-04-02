# /* MCTSPlayer.py

import math
import random
from typing import Literal, Optional, Tuple, List

from data.classes.Square import Square
from data.classes.Board import Board
from data.classes.agents.ChessAgent import ChessAgent


class MCTSNode:
    def __init__(self, board: Board, parent: Optional['MCTSNode'] = None, move: Tuple[Square, Square] = None):
        self.board = board
        self.parent = parent
        self.move = move
        self.children: List[MCTSNode] = []
        self.wins = 0
        self.visits = 0
        self.untried_moves: List[Tuple[Square, Square]] = self._get_untried_moves()

    def _get_untried_moves(self) -> List[Tuple[Square, Square]]:
        moves = []
        for square in self.board.squares:
            if square.occupying_piece is not None and square.occupying_piece.color == self.board.turn:
                for target in square.occupying_piece.get_valid_moves(self.board):
                    moves.append((square, target))
        return moves

    def add_child(self, move: Tuple[Square, Square]) -> 'MCTSNode':
        # Create a new board with the same dimensions
        child_board = Board(self.board.display, self.board.width, self.board.height)
        # Copy the piece positions
        for i, square in enumerate(self.board.squares):
            if square.occupying_piece:
                child_board.squares[i].occupying_piece = square.occupying_piece
        child_board.turn = self.board.turn

        from_square, to_square = move
        child_board.handle_move(from_square, to_square)
        child = MCTSNode(child_board, parent=self, move=move)
        self.untried_moves.remove(move)
        self.children.append(child)
        return child

    def update(self, result: float):
        self.visits += 1
        self.wins += result

    def fully_expanded(self) -> bool:
        return len(self.untried_moves) == 0

    def best_child(self, c_param: float = 1.414) -> 'MCTSNode':
        choices = [(c.wins / c.visits) + c_param * math.sqrt((2 * math.log(self.visits) / c.visits))
                  for c in self.children]
        return self.children[choices.index(max(choices))]


class MCTSPlayer(ChessAgent):
    def __init__(self, color: Literal['white', 'black'], num_simulations: int = 1000):
        super().__init__(color)
        self.num_simulations = num_simulations

    def choose_action(self, board: Board) -> Tuple[Square, Square] | bool:
        root = MCTSNode(board)

        for _ in range(self.num_simulations):
            node = root
            # Create a new board for simulation
            state = Board(board.display, board.width, board.height)
            # Copy the piece positions
            for i, square in enumerate(board.squares):
                if square.occupying_piece:
                    state.squares[i].occupying_piece = square.occupying_piece
            state.turn = board.turn

            # Selection
            while node.fully_expanded() and node.children:
                node = node.best_child()
                if node.move:
                    from_square, to_square = node.move
                    state.handle_move(from_square, to_square)

            # Expansion
            if node.untried_moves:
                move = random.choice(node.untried_moves)
                from_square, to_square = move
                state.handle_move(from_square, to_square)
                node = node.add_child(move)

            # Simulation
            while not state.is_in_checkmate(state.turn):
                possible_moves = []
                for square in state.squares:
                    if square.occupying_piece is not None and square.occupying_piece.color == state.turn:
                        for target in square.occupying_piece.get_valid_moves(state):
                            possible_moves.append((square, target))
                if not possible_moves:
                    break
                move = random.choice(possible_moves)
                from_square, to_square = move
                state.handle_move(from_square, to_square)

            # Backpropagation
            result = 1.0 if state.is_in_checkmate('black' if self.color == 'white' else 'black') else 0.0
            while node is not None:
                node.update(result)
                node = node.parent

        # Choose the best move
        if not root.children:
            return False
        best_child = root.best_child(c_param=0.0)
        return best_child.move