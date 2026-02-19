from aima_toolkit.AdversarialSearch import minmax_search
from aima_toolkit.AdversarialSearch.PremadeGames import TicTacToe
import pytest
import math

@pytest.fixture
def ttt_game():
    # Set depth high enough to solve Tic-Tac-Toe (at least 9)
    return TicTacToe(depth_limit=10)


def test_minmax_takes_winning_move(ttt_game):
  """If X has an immediate winning move, minmax must choose it."""
  # X can win by playing at index 2 (top-right)
  board = ('X', 'X', ' ',
           'O', 'O', ' ',
           ' ', ' ', ' ')
  state = (board, 'X')

  values, move = minmax_search( ttt_game, state )

  assert move == 2
  assert values[ 'X' ] == 2

def test_minmax_blocks_opponent_win(ttt_game):
  """If O is about to win, X must move to block them."""
  # O has two in a row on the bottom; X must play at index 8
  board = ('X', ' ', ' ',
           ' ', 'X', ' ',
           'O', 'O', ' ')
  state = (board, 'X')

  values, move = minmax_search( ttt_game, state )

  assert move == 8

def test_minmax_perfect_play_draw(ttt_game):
  """Two perfect players should result in a draw utility of 0."""
  # Starting from a fresh board
  board = (' ',) * 9
  state = (board, 'X')

  # We use a lower singularity_ply or specific margin if your implementation requires
  ttt_game.margin = 0.1
  values, move = minmax_search( ttt_game, state, singularity_ply=1 )


  assert values[ 'X' ] == 1
  assert values[ 'O' ] == 1
  # On an empty board, center (4) or corners are common optimal moves
  assert move in [ 0, 2, 4, 6, 8 ]

def test_minmax_respects_depth_limit( ):
  """If depth limit is low, minmax should return EVAL scores instead of UTILITY."""
  # Set a very shallow depth limit
  shallow_game = TicTacToe( depth_limit=1 )
  board = ('X', ' ', ' ',
           ' ', ' ', ' ',
           ' ', ' ', ' ')
  state = (board, 'O')  # O's turn

  values, move = minmax_search( shallow_game, state )

  # Since it can't see the end of the game,
  # it should return the heuristic value from EVAL
  assert 0 < values[ 'X' ] < 2
  assert move is not None

def test_minmax_terminal_state(ttt_game):
  """If called on a terminal state, move should be None."""
  board = ('X', 'X', 'X',
           'O', 'O', ' ',
           ' ', ' ', ' ')
  state = (board, 'O')

  values, move = minmax_search( ttt_game, state )

  assert move is None
  assert values[ 'X' ] == 2
  assert values[ 'O' ] == 0