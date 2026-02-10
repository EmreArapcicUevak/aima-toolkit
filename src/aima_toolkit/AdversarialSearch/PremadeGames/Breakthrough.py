from typing import Iterable
import copy

from .. import Game
StateT = tuple[tuple[str, ...], int]
PlayerT = int
MoveT = str

class Breakthrough(Game):
  """
  Breakthrough: a tactical board game played on a 5x5 grid.

  The board is represented as a flat 25-element tuple in row-major order
  (indices 0-4 are the top row, indices 20-24 are the bottom row).

  A game state is defined by:
  - State: (board, player), where board is a tuple containing 'w', 'b', or ' ',
    and player is an integer (0 for White, 1 for Black).
  - Actions: A piece may move one square forward, either straight or diagonally.
    White moves upward (toward lower indices) and Black moves downward (toward
    higher indices).
  - Captures: Captures occur only on diagonal forward moves when the destination
    square contains an opponent piece.
  - Terminal Test: A player wins by reaching the opponent's home row
    (White reaches indices 0-4, Black reaches indices 20-24), or by eliminating
    all enemy pieces.

  Type Aliases
  ------------
  StateT : tuple[tuple[str, ...], int]
      (board, current_player)
  MoveT : str
      Move encoded as "start-end", where start and end are board indices.
  PlayerT : int
      0 for White, 1 for Black.
  """
  def __init__(self, depth_limit : int):
    super().__init__()
    self.depth_limit = depth_limit

  def TO_MOVE(self, state: StateT) -> PlayerT:
    return state[1]

  def ACTIONS(self, state: StateT) -> Iterable[ MoveT ]:
    if self.IS_TERMINAL(state):
      return []

    board, current_player = state


    player_symbol = 'b' if current_player == 1 else 'w'
    left_shift, middle_shift, right_shift = (4,5,6) if current_player == 1 else (-6, -5, -4)
    left_wall = (0, 5, 10, 15, 20)
    right_wall = (4, 9, 14, 19, 24)

    for position in range(25):
      if board[position] == player_symbol:
        if board[position + middle_shift] == ' ':
          yield f"{position}-{position + middle_shift}"

        if position not in left_wall and board[position + left_shift] != player_symbol:
          yield f"{position}-{position + left_shift}"

        if position not in right_wall and board[position + right_shift] != player_symbol:
          yield f"{position}-{position + right_shift}"

  def QUIESCENCE_ACTIONS(self, state: StateT) -> Iterable[ MoveT ]:
    if self.IS_TERMINAL( state ):
      return [ ]

    board, current_player = state

    player_symbol = 'b' if current_player == 1 else 'w'
    enemy_symbol = 'w' if current_player == 1 else 'b'

    left_shift, middle_shift, right_shift = (4, 5, 6) if current_player == 1 else (-6, -5, -4)
    left_wall = (0, 5, 10, 15, 20)
    right_wall = (4, 9, 14, 19, 24)

    for position in range( 25 ):
      if board[ position ] == player_symbol:
        if position not in left_wall and board[ position + left_shift ] == enemy_symbol:
          yield f"{position}-{position + left_shift}"

        if position not in right_wall and board[ position + right_shift ] == enemy_symbol:
          yield f"{position}-{position + right_shift}"

  def RESULTS(self, state: StateT, action: MoveT) -> StateT:
    board, current_player = state

    current_player_symbol = 'b' if current_player == 1 else 'w'
    next_player = (current_player + 1) % 2
    current_position, new_position = map(int, action.split(sep='-'))

    assert board[current_position] == current_player_symbol
    assert board[new_position] != current_player_symbol

    new_board = list(board)
    new_board[current_position] = ' '
    new_board[new_position] = current_player_symbol

    return tuple(new_board), next_player


  def IS_TERMINAL(self, state: StateT) -> bool:
    board, _ = state
    if 'w' not in board or 'b' not in board:
      return True
    elif 'w' in board[0:5] or 'b' in board[20:25]:
      return True
    else:
      return False

  def UTILITY(self, state: StateT) -> dict[ PlayerT, float ]:
    assert self.IS_TERMINAL(state)
    board, _ = state

    if 'w' not in board and 'b' not in board:
      return {0 : 0, 1 : 0}
    elif 'w' not in board or 'b' in board[20:25]:
      return {0 : -1, 1 : 1}
    else:
      return {0 : 1, 1 : -1}

  def EVAL(self, state: StateT) -> dict[ PlayerT, float ]:
    if self.IS_TERMINAL(state):
      return self.UTILITY(state)

    board, _ = state
    white_score, black_score = 0, 0

    for pos, piece in enumerate( board ):
      row = pos // 5

      if piece == 'w':
        white_score += 10  # material
        white_score += (4 - row) * 2  # advancement bonus
      elif piece == 'b':
        black_score += 10
        black_score += row * 2

    normalized_score = (white_score - black_score) / 170
    return {0 : normalized_score, 1 : -normalized_score}

  def IS_CUTOFF(self, state: StateT, depth: int) -> bool:
    assert depth >= 0
    return self.IS_TERMINAL( state ) or depth >= self.depth_limit