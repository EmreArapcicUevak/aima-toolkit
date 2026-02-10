import pytest
from aima_toolkit.AdversarialSearch.PremadeGames import Breakthrough
from aima_toolkit.AdversarialSearch import minmax_search

@pytest.fixture
def game( ):
  # Helper to ensure we get a fresh game instance
  return Breakthrough(depth_limit=3)


# --- Helper for parsing the user's specific move format ---
def get_dest(move_str):
  """Parses 'start-end' string and returns end index as int."""
  return int( move_str.split( sep='-' )[ -1 ] )


def get_start(move_str):
  """Parses 'start-end' string and returns start index as int."""
  return int( move_str.split( sep='-' )[ 0 ] )

@pytest.fixture
def bt_game():
    # Depth 3 is sufficient for most tactical checks in 5x5 Breakthrough
    return Breakthrough(depth_limit=3)

def test_minmax_takes_winning_move(bt_game):
    """If White has an immediate winning move (reaching row 0), minmax must choose it."""
    # Setup:
    # White at index 6 (Row 1). One move to reach Row 0 (index 1).
    # All other squares empty for simplicity.
    board_list = [' '] * 25
    board_list[6] = 'w'
    board_list[4] = 'b'
    state = (tuple(board_list), 0) # White's turn

    # Call your search function
    values, move = minmax_search(bt_game, state)

    # We check if the chosen move lands on row 0.
    dest = get_dest(move)
    assert dest in (0,1,2)  # Must land in Winning Row (0-4)

    # Check if value reflects a win
    assert values[0] == 1
    assert values[1] == -1

def test_minmax_blocks_opponent_win(bt_game):
    """If Black is about to win, White must capture or block them."""
    # Setup:
    # Black at 16 (Row 3). Next move to 21 (Row 4) wins.
    # White at 22 (Row 4).
    # White MUST capture Black at 16 to survive.
    # Move: 22->16 (Diagonal Right Capture: 22 - 6 = 16)

    board_list = [' '] * 25
    board_list[16] = 'b' # The threat
    board_list[22] = 'w' # The defender
    state = (tuple(board_list), 0) # White's turn

    values, move = minmax_search(bt_game, state)

    # We expect the move to target index 16
    dest = get_dest(move)
    assert dest == 16

def test_minmax_respects_depth_limit():
    """If depth limit is low, minmax should return EVAL scores instead of terminal UTILITY."""
    # Use a very shallow depth
    shallow_game = Breakthrough(depth_limit=1)

    # A generic mid-game state (no immediate win)
    board_list = [' '] * 25
    board_list[12] = 'w'
    board_list[7] = 'b'
    state = (tuple(board_list), 0)

    values, move = minmax_search(shallow_game, state)

    # Since it's not a terminal state, values should be heuristic scores
    # Checking that we got a valid move and a score
    assert get_dest(move) in (6, 8)
    assert values[0] > 0

def test_minmax_terminal_state(bt_game):
    """If called on a terminal state, move should be None."""
    # Setup: White has already reached row 0
    board_list = [' '] * 25
    board_list[2] = 'w'
    state = (tuple(board_list), 1) # Black's turn, but game is over

    values, move = minmax_search(bt_game, state)

    assert move is None
    assert values[0] == 1
    assert values[1] == -1

def test_minmax_quiescence_scenario(bt_game):
    """
    Test a scenario where Quiescence Search changes the outcome compared to Depth 1.
    (Optional but recommended for your specific use case)
    """
    # Setup the "Poisoned Pawn" scenario
    # White can capture a piece, but will be immediately recaptured.
    # Depth 1 (No QS) -> Takes the piece.
    # Depth 1 + QS -> Sees the recapture and avoids it.

    board_list = [' '] * 25
    board_list[12] = 'w'
    board_list[8] = 'b'  # Bait
    board_list[4] = 'b'  # Trap (guards 8)
    board_list[11] = 'w' # Safe move option

    state = (tuple(board_list), 0)

    # Force shallow search to rely on QS
    bt_game.depth_limit = 1

    values, move = minmax_search(bt_game, state)

    dest = get_dest(move)

    # Ideally, minmax with QS enabled in the game class should AVOID the capture at 8
    # If this fails, your QS logic might not be triggering correctly.
    assert dest != 8