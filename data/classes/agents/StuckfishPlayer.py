from data.classes.Board import Board
from data.classes.Square import Square
from data.classes.agents.ChessAgent import ChessAgent


class StuckfishPlayer(ChessAgent):
  def choose_action(self, board: Board) -> tuple[Square, Square]:
    possible_moves = self.determine_all_possible_moves(board)
    if len(possible_moves) < 1:
      return False
    return random.choice(possible_moves)


  def determine_all_possible_moves(self, board: Board) -> list[tuple[Square, Square]]:
    possible_moves: list[tuple[Square, Square]] = []
    for square in board.squares:
      if square.occupying_piece is not None and square.occupying_piece.color == self.color:
        for target in square.occupying_piece.get_valid_moves(board):
          possible_moves.append((square, target))
    return possible_moves