from aima_toolkit.AdversarialSearch.PremadeGames import Breakthrough
import pytest


# Helper to create state from a string for readability
def make_state(board_str: str, player: int):
  # Removes whitespace/newlines and converts to tuple
  board = tuple( board_str.replace( '\n', '' ).replace( '|', '' ) )
  return (board, player)

@pytest.fixture
def game():
    return Breakthrough(depth_limit=5)

class TestBreakthrough:
  def test_initial_moves_count(self, game):
    """At the start of the game, White should have exactly 15 moves on a 5x5 board."""
    # 5 pieces in the front row can move 3 ways each = 15
    # (Actually, in Breakthrough, front row is usually full)
    board_str = (
      "  b  "
      "     "
      "     "
      "wwwww"
      "wwwww"
    )
    state = make_state( board_str, 0 )
    actions = list( game.ACTIONS( state ) )
    assert len( actions ) == 13

  @pytest.mark.parametrize( "start_idx, expected_dests", [
    (10, [ 5, 6 ]),  # Left edge: can only move straight (5) or diag-right (6)
    (12, [ 6, 7, 8 ]),  # Center: can move all three directions
    (14, [ 8, 9 ]),  # Right edge: can only move straight (9) or diag-left (8)
  ] )
  def test_movement_boundaries(self, game, start_idx, expected_dests):
    """Ensure pieces don't wrap around the 1D array."""
    board_list = [ ' ' ] * 25
    board_list[ start_idx ] = 'w'
    board_list[ start_idx + (1 if start_idx != 24 else -1)] = 'b'
    state = (tuple( board_list ), 0)

    actions = game.ACTIONS( state )
    destinations = [ int(move.split(sep='-')[-1]) for move in actions ]

    assert sorted( destinations ) == sorted( expected_dests )

  def test_quiescence_only_captures(self, game):
    """QUIESCENCE_ACTIONS should ignore empty diagonal squares."""
    board_str = (
      "  b  "  # b at index 2
      " w   "  # w at index 6
      "     "
      "     "
      "     "
    )
    state = make_state( board_str, 0 )

    # Standard actions should include straight move (1) and diag move (3)
    # Quiescence should ONLY include the capture at (2)
    q_actions = list( game.QUIESCENCE_ACTIONS( state ) )
    destinations = [ int(move.split(sep='-')[-1]) for move in q_actions ]

    assert 2 in destinations
    assert 1 not in destinations
    assert 3 not in destinations
    assert len( q_actions ) == 1

  def test_straight_move_blocked_by_enemy(self, game):
    """In Breakthrough, you cannot capture by moving straight forward."""
    board_str = (
      "  b  "  # index 2
      "  w  "  # index 7
      "     "
      "     "
      "     "
    )
    state = make_state( board_str, 0 )
    actions = list( game.ACTIONS( state ) )
    destinations = [ int(move.split(sep='-')[-1]) for move in actions ]

    assert 2 not in destinations

  def test_win_by_reaching_end(self, game):
    """Check if reaching the final row triggers IS_TERMINAL."""
    board_str = (
      " w   "  # White reached row 0
      "     "
      "  b  "
      "     "
      "     "
    )
    state = make_state( board_str, 1 )  # Black's turn
    assert game.IS_TERMINAL( state ) is True

  def test_eval_symmetry(self, game):
    """EVAL should be zero-sum or relative to the player."""
    board_str = (
      "bbbbb"
      "     "
      "     "
      "     "
      "wwwww"
    )
    state = make_state( board_str, 0 )
    evals = game.EVAL( state )
    # On a mirrored starting board, the relative advantage should be 0
    assert evals[ 0 ] == 0

    def test_eval_material_advantage(self, game):
      """White with 3 pieces should have higher score than Black with 2 pieces (same rows)."""
      board_w3_b2 = (
        "     "
        "b b  "
        "     "  # Row 2
        "w w w"  # Row 3
        "     "
      )
      state = make_state( board_w3_b2, 0 )
      evals = game.EVAL( state )

      # evals[0] is White's perspective
      assert evals[ 0 ] > 0, "White should have positive score with material lead"

  def test_eval_positional_advantage(self, game):
    """Even material, but White is closer to row 0 than Black is to row 4."""
    board_w_closer = (
      "     "  # White is 1 step from winning (Row 0)
      "b w  "
      "     "
      "     "  # Black is 3 steps from winning (Row 4 is target, currently row 3)
      "     "
    )
    state = make_state( board_w_closer, 0 )
    evals = game.EVAL( state )

    assert evals[ 0 ] > 0, "White should have advantage due to proximity to goal"

  def test_quiescence_vs_standard_actions(self, game):
    """
    Verify that QUIESCENCE_ACTIONS filters out non-capturing moves
    while ACTIONS returns everything.
    """
    # Setup:
    # Black at index 7.
    # White at index 11 (Diagonal Left) -> Capture target.
    # Empty at index 12 (Straight) -> Quiet move target.
    # White at index 13 (Diagonal Right) -> Capture target.

    board_list = [ ' ' ] * 25
    board_list[ 7 ] = 'b'
    board_list[ 11 ] = 'w'
    board_list[ 12 ] = ' '
    board_list[ 13 ] = 'w'

    state = (tuple( board_list ), 1)  # Black's turn

    # 1. Standard ACTIONS should see ALL 3 possibilities
    actions = list( game.ACTIONS( state ) )
    all_dests = [ int(move.split(sep='-')[-1]) for move in actions ]

    assert 11 in all_dests  # Capture
    assert 12 in all_dests  # Quiet move (Straight)
    assert 13 in all_dests  # Capture
    assert len( all_dests ) == 3

    # 2. QUIESCENCE_ACTIONS should ONLY see the 2 captures
    q_actions = list( game.QUIESCENCE_ACTIONS( state ) )
    q_dests = [ int(move.split(sep='-')[-1]) for move in q_actions ]

    assert 11 in q_dests
    assert 13 in q_dests
    assert 12 not in q_dests  # <--- This is the proof! The quiet move is filtered out.
    assert len( q_dests ) == 2

  # --- Transition Model Tests ---

  def test_results_updates_correctly(self, game):
    """Ensure RESULTS moves the piece and clears the old spot."""
    # Setup: White at 22 (bottom row), attempting to move forward to 17
    board_list = [ ' ' ] * 25
    board_list[ 22 ] = 'w'
    board_list[ 0 ] = 'b'
    state = (tuple( board_list ), 0)  # 0 is White

    action = "22-17"
    new_state = game.RESULTS( state, action )
    new_board, next_player = new_state

    # Check board update
    assert new_board[ 22 ] == ' '
    assert new_board[ 17 ] == 'w'
    # Check player swap (0 -> 1)
    assert next_player == 1
