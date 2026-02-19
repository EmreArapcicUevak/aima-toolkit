import pytest
from aima_toolkit.AdversarialSearch.PremadeGames import Chess
from aima_toolkit.AdversarialSearch import minmax_search


# --- Helpers ---
def create_board(piece_dict):
  """
  Creates a 64-length tuple board from a dictionary of {index: 'Piece'}.
  Indices: 0=a8, 7=h8, 56=a1, 63=h1.
  """
  board = [ ' ' ] * 64
  for idx, piece in piece_dict.items( ):
    board[ idx ] = piece
  return tuple( board )


def get_dest(move_str):
  return int( move_str.split( '-' )[ -1 ].split( '=' )[ 0 ] )


@pytest.fixture
def chess_game( ):
  # Depth 3 is usually enough to see mate-in-1 and 1-move blunders
  return Chess( tt_memory_mb=200, depth_limit=3, horizon_margin=0.2)


# --- Tests ---

def test_minmax_finds_mate_in_one(chess_game):
  """White has a forced Mate in 1. Minimax must find it."""
  # Setup:
  # Black King on e8 (4)
  # White King on e6 (20) - cuts off d7, e7, f7
  # White Queen on a7 (8)
  # Move: Queen a7 to a8 (8-0) is checkmate.
  board = create_board( {
    4: 'k',
    20: 'K',
    8: 'Q'
  } )

  # State: board, player (0=White), no castling, no en passant
  state = (board, 0, (False, False, False, False), None)

  values, move = minmax_search( chess_game, state )

  assert move in ('8-0', '8-1', '8-12'), f"Expected mate-in-1 move '8-0' or '8-1' or '8-12', but got {move}"
  assert values[ 0 ] == 2, "White's utility should reflect a win (2)"


def test_minmax_blocks_immediate_mate(chess_game):
  """Black threatens mate in 1. White must defend."""
  # Setup:
  # White King on h1 (63), blocked by pawns on g2(54), h2(55).
  # Black Rook on a2 (48). Next move a2-a1 (48-56) is back-rank mate.
  # White MUST move a pawn to create an escape square (luft).
  board = create_board( {
    63: 'K',
    54: 'P',
    55: 'P',
    48: 'r',
    4: 'k'  # Keep enemy king on board for validity
  } )

  state = (board, 0, (False, False, False, False), None)
  values, move = minmax_search( chess_game, state )

  # Valid defenses are moving the g2 or h2 pawn forward
  valid_defenses = [ '54-46', '55-47', '54-38', '55-39']
  assert move in valid_defenses, f"Minimax failed to prevent mate. Made move {move}"


def test_minmax_takes_free_material(chess_game):
  """White can capture a free Black Queen. Minimax should prioritize massive material gain."""
  # Setup:
  # White Rook on a1 (56).
  # Black Queen on a8 (0).
  # Kings tucked away safely.
  board = create_board( {
    56: 'R',
    0: 'q',
    63: 'K',
    7: 'k'
  } )

  state = (board, 0, (False, False, False, False), None)
  values, move = minmax_search( chess_game, state )

  # White should capture the Queen at index 0
  assert move == '56-0', f"Expected to take the free Queen with '56-0', got {move}"


def test_minmax_avoids_blundering_queen(chess_game):
  """White can capture a pawn, but it's defended. Minimax should avoid bad trades."""
  # Setup:
  # White Queen on d4 (27).
  # Black Pawn on d5 (19), defended by Black Rook on e5 (20).
  # If White plays '27-19', Black recaptures '20-19', losing the Queen for a Pawn.
  board = create_board( {
    27: 'Q',
    19: 'p',
    20: 'r',
    63: 'K',
    7: 'k'
  } )

  state = (board, 0, (False, False, False, False), None)
  values, move = minmax_search( chess_game, state )

  # White must NOT take the pawn at 19
  assert get_dest( move ) != 19, "Minimax blundered the Queen by taking a guarded pawn!"


def test_minmax_terminal_state(chess_game):
  """If the board is already in checkmate, search should return None for the move."""
  # Setup: Black is already checkmated.
  # Black King on e8 (4). White King on e6 (20). White Queen on e7 (12).
  board = create_board( {
    4: 'k',
    20: 'K',
    12: 'Q'
  } )

  # It is Black's turn (1), but they have no legal moves and are in check.
  state = (board, 1, (False, False, False, False), None)

  values, move = minmax_search( chess_game, state )

  assert move is None, f"Expected move to be None on terminal state, got {move}"
  assert values[ 1 ] == 0, "Black's utility should reflect a loss (0)"