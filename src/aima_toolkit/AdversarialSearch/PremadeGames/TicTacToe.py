from typing import Iterator

from .. import Game

class TicTacToe(Game):
  """
  Tic-Tac-Toe game implementation for adversarial search.

  The game state is represented as a tuple of the form::

      (board, player)

  where:

  - ``player`` is a string representing the player to move,
    either ``'X'`` or ``'O'``.

  - ``board`` is a 1D tuple of length 9 representing the game board,
    indexed left-to-right, top-to-bottom. Each cell contains:

      - ``'X'`` for player X
      - ``'O'`` for player O
      - ``' '`` (space) for an empty square

    Example::

        (
            ('X', 'O', ' ',
             ' ', 'X', ' ',
             'O', ' ', ' '),
            'O'
        )

  Game semantics:

  - ``TO_MOVE(state)`` returns the player whose turn it is.
  - ``ACTIONS(state)`` returns the indices (0–8) of empty squares.
  - ``RESULTS(state, action)`` returns the new state after placing
    the current player's mark at the given index.
  - ``IS_TERMINAL(state)`` returns True if the game is over
    (win or draw).
  - ``UTILITY(state)`` returns a payoff dictionary with values:

      - ``+1`` for a win
      - ``-1`` for a loss
      - ``0`` for a draw

    The utility is from the perspective of each player.

  - ``EVAL(state)`` provides a heuristic evaluation for non-terminal
    states when search is cut off.
  - ``IS_CUTOFF(state, depth)`` stops the search when a terminal
    state is reached or when the depth limit is exceeded.

  Parameters
  ----------
  depth_limit : int
      Maximum search depth used for cutoff-based search algorithms
      such as minimax or alpha–beta pruning.
  """
  def __init__(self, depth_limit : int):
    super().__init__(sum=2)
    self.depth_limit = depth_limit

  def TO_MOVE(self, state: tuple[tuple,str]) -> str:
    return state[1]

  def ACTIONS(self, state: tuple[tuple,str]) -> Iterator[ int ]:
    board, _ = state
    return (i for i in range(9) if board[i] == ' ')

  def RESULTS(self, state: tuple[tuple,str], action: int) -> tuple[tuple,str]:
    board, current_player = state
    assert board[action] == ' '

    new_board = list(board)
    new_board[action] = current_player

    next_player = 'O' if current_player == 'X' else 'X'
    return tuple(new_board), next_player

  def IS_TERMINAL(self, state: tuple[tuple,str]) -> bool:
    board, _ = state
    for i in (0,1,2):
      if board[i] != ' ' and board[i] == board[i+3] == board[i+6]: return True # Check rows

    for i in (0,3,6):
      if board[i] != ' ' and board[i] == board[i+1] == board[i+2]: return True # Check columns

    if board[4] != ' ' and (board[0] == board[4] == board[8] or board[2] == board[4] == board[6]): return True # Check Diagonals

    return ' ' not in board # Draw

  def UTILITY(self, state: tuple[tuple,str]) -> dict[ str, float ]:
    assert self.IS_TERMINAL(state)
    board, _ = state

    for i in (0,1,2):
      if board[i] != ' ' and board[i] == board[i+3] == board[i+6]: # Check rows
        return {'X' : 2, 'O' : 0}  if board[i] == 'X' else {'X' : 0, 'O' : 2}

    for i in (0,3,6):
      if board[i] != ' ' and board[i] == board[i+1] == board[i+2]: # Check columns
        return {'X' : 2, 'O' : 0}  if board[i] == 'X' else {'X' : 0, 'O' : 2}

    if board[4] != ' ' and (board[0] == board[4] == board[8] or board[2] == board[4] == board[6]): # Check Diagonals
      return { 'X': 2, 'O': 0 } if board[ 4 ] == 'X' else { 'X': 0, 'O': 2 }

    return { 'X' : 1, 'O' : 1 } # Draw

  def EVAL(self, state: tuple[tuple,str]) -> dict[ str, float ]:
    if self.IS_TERMINAL(state):
      return self.UTILITY(state)

    board, _ = state
    lines = (
      (board[0], board[1], board[2]),
      (board[3], board[4], board[5]),
      (board[6], board[7], board[8]),
      (board[0], board[3], board[6]),
      (board[1], board[4], board[7]),
      (board[2], board[5], board[8]),
      (board[0], board[4], board[8]),
      (board[2], board[4], board[6]),
    )

    final_score = 0
    for line in lines:
      x = line.count('X')
      o = line.count('O')

      if x > 0 and o > 0:
        continue
      elif x > 0:
        final_score += x
      elif o > 0:
        final_score -= o

    final_score = final_score / 16

    return {'X' : 1+final_score, 'O' : 1-final_score}

  def IS_CUTOFF(self, state: tuple[tuple,str], depth: int) -> bool:
    assert depth >= 0
    return self.IS_TERMINAL( state ) or depth >= self.depth_limit