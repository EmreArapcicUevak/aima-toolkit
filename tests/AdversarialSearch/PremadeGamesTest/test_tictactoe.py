import pytest
from aima_toolkit.AdversarialSearch.PremadeGames import TicTacToe

@pytest.fixture
def game():
    return TicTacToe(depth_limit=3)


# --- Transition Model Tests ---
def test_results_updates_correctly(game):
  """Ensure RESULTS places the mark and swaps the player."""
  initial_board = (' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ')
  state = (initial_board, 'X')

  new_board, next_player = game.RESULTS( state, 4 )  # Place X in center

  assert new_board[ 4 ] == 'X'
  assert next_player == 'O'
  assert new_board.count( ' ' ) == 8


def test_actions_finds_all_empty_spaces(game):
  """Ensure ACTIONS returns only indices with ' '."""
  board = ('X', 'O', 'X', ' ', 'O', ' ', ' ', ' ', ' ')
  state = (board, 'X')
  assert list( game.ACTIONS( state ) ) == [ 3, 5, 6, 7, 8 ]

# --- Terminal and Utility Tests ---

@pytest.mark.parametrize("board, expected_utility", [
    # X wins horizontally
    (('X', 'X', 'X', 'O', 'O', ' ', ' ', ' ', ' '), {'X': 2, 'O': 0}),
    # O wins vertically
    (('X', 'O', ' ', 'X', 'O', ' ', ' ', 'O', 'X'), {'X': 0, 'O': 2}),
    # Draw
    (('X', 'O', 'X', 'X', 'O', 'O', 'O', 'X', 'X'), {'X': 1, 'O': 1}),
])
def test_terminal_utility(game, board, expected_utility):
    state = (board, 'X')
    assert game.IS_TERMINAL(state) is True
    assert game.UTILITY(state) == expected_utility


# --- Evaluation and Heuristic Tests ---

def test_eval_consistency_with_utility(game):
  """EVAL must return UTILITY values if the state is terminal."""
  win_board = ('X', 'X', 'X', 'O', ' ', 'O', ' ', ' ', ' ')
  state = (win_board, 'O')

  assert game.EVAL( state ) == game.UTILITY( state )


def test_eval_heuristic_direction(game):
  """Check if EVAL score favors X when X has a better position."""
  # X has center, O has a corner.
  board = ('O', ' ', ' ', ' ', 'X', ' ', ' ', ' ', ' ')
  state = (board, 'O')

  scores = game.EVAL( state )
  # X should have a positive score, O negative
  assert scores[ 'X' ] > 1
  assert scores[ 'O' ] < 1


# --- Cutoff Logic ---

def test_is_cutoff(game):
  """Verify cutoff logic for depth and terminal states."""
  empty_state = ((' ',) * 9, 'X')

  # Not terminal, depth 0 -> False
  assert game.IS_CUTOFF( empty_state, 0 ) is False
  # Not terminal, depth at limit -> True
  assert game.IS_CUTOFF( empty_state, 3 ) is True

  # Terminal state -> True regardless of depth
  win_state = (('X', 'X', 'X', ' ', ' ', ' ', ' ', ' ', ' '), 'O')
  assert game.IS_CUTOFF( win_state, 1 ) is True
  assert game.IS_CUTOFF( win_state, 10 ) is True
