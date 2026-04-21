from __future__ import annotations
from typing import Iterator
from collections import Counter
import math

from .. import Game

# Player: 0 = White, 1 = Black
PlayerT = int

# Move encoding:
#   "from-to" normal
#   "from-to=Q" promotion
#   "from-to=R" promotion
#   "from-to=B" promotion
#   "from-to=N" promotion
MoveT = str

# State:
# board: tuple[str, ...] length 64
# player: 0/1
# castling: (WK, WQ, BK, BQ)
# enpassant: int | None (square index that can be captured onto)
StateT = tuple[tuple[str, ...], PlayerT, tuple[bool, bool, bool, bool], int | None]

cdef bint _is_white(str piece):
    return piece.isupper()

cdef bint _is_black(str piece):
    return piece.islower()

cdef bint _enemy(int player, str piece):
    if piece == ' ':
        return False
    return (player == 0 and _is_black(piece)) or (player == 1 and _is_white(piece))

cdef bint _friendly(int player, str piece):
    if piece == ' ':
        return False
    return (player == 0 and _is_white(piece)) or (player == 1 and _is_black(piece))

cdef bint _in_bounds(int r, int c):
    return 0 <= r < 8 and 0 <= c < 8

cdef int _rc_to_i(int r, int c):
    return r * 8 + c

cdef (int, int) _i_to_rc(int i):
    return i // 8, i % 8

cdef str _king_piece(int player):
    return 'K' if player == 0 else 'k'

cdef str _pawn_piece(int player):
    return 'P' if player == 0 else 'p'

cdef int _back_rank(int player):
    return 7 if player == 0 else 0

cdef int _promotion_rank(int player):
    return 0 if player == 0 else 7

# ----------------------------
# MOVE GENERATION CORE
# ----------------------------

# NOTE: _pseudo_legal_moves, _pawn_moves, _knight_moves, _slide_moves,
# _bishop_moves, _rook_moves, _queen_moves, _king_moves must remain as
# 'def' methods on the class because they use 'yield'.
# All self._ calls inside them are replaced with module-level cdef calls.

def _pseudo_legal_moves(state):
    board, player, castling, ep = state

    cdef int i
    cdef str piece

    for i in range(64):
        piece = board[i]
        if not _friendly(player, piece):
            continue

        if piece == 'P' or piece == 'p':
            yield from _pawn_moves(state, i)
        elif piece == 'N' or piece == 'n':
            yield from _knight_moves(state, i)
        elif piece == 'B' or piece == 'b':
            yield from _bishop_moves(state, i)
        elif piece == 'R' or piece == 'r':
            yield from _rook_moves(state, i)
        elif piece == 'Q' or piece == 'q':
            yield from _queen_moves(state, i)
        elif piece == 'K' or piece == 'k':
            yield from _king_moves(state, i)

def _pawn_moves(state, int i):
    board, player, castling, ep = state

    cdef int r, c, nr, nc, to, to2, nnr
    cdef int direction, start_row, promo_row
    cdef str piece, promo_piece, p

    r, c = _i_to_rc(i)
    direction = -1 if player == 0 else 1
    start_row = 6 if player == 0 else 1
    promo_row = _promotion_rank(player)

    # forward 1
    nr = r + direction
    if _in_bounds(nr, c):
        to = _rc_to_i(nr, c)
        if board[to] == ' ':
            if nr == promo_row:
                for p in "QRBN":
                    promo_piece = p if player == 0 else p.lower()
                    yield f"{i}-{to}={promo_piece}"
            else:
                yield f"{i}-{to}"

            if r == start_row:
                nnr = r + 2 * direction
                to2 = _rc_to_i(nnr, c)
                if board[to2] == ' ':
                    yield f"{i}-{to2}"

    # captures
    cdef int dc
    for dc in (-1, 1):
        nc = c + dc
        nr = r + direction
        if not _in_bounds(nr, nc):
            continue
        to = _rc_to_i(nr, nc)

        if _enemy(player, board[to]):
            if nr == promo_row:
                for p in "QRBN":
                    promo_piece = p if player == 0 else p.lower()
                    yield f"{i}-{to}={promo_piece}"
            else:
                yield f"{i}-{to}"

        if ep is not None and to == ep:
            yield f"{i}-{to}"

def _knight_moves(state, int i):
    board, player, castling, ep = state

    cdef int r, c, nr, nc, to
    cdef int dr, dc

    r, c = _i_to_rc(i)

    cdef int[8][2] jumps = [
        [-2, -1], [-2, 1],
        [-1, -2], [-1, 2],
        [1, -2],  [1, 2],
        [2, -1],  [2, 1],
    ]

    for dr, dc in jumps:
        nr = r + dr
        nc = c + dc
        if not _in_bounds(nr, nc):
            continue
        to = _rc_to_i(nr, nc)
        if not _friendly(player, board[to]):
            yield f"{i}-{to}"

def _slide_moves(state, int i, directions):
    board, player, castling, ep = state

    cdef int r, c, nr, nc, to
    cdef int dr, dc

    r, c = _i_to_rc(i)

    for dr, dc in directions:
        nr = r + dr
        nc = c + dc
        while _in_bounds(nr, nc):
            to = _rc_to_i(nr, nc)

            if _friendly(player, board[to]):
                break

            yield f"{i}-{to}"

            if _enemy(player, board[to]):
                break

            nr += dr
            nc += dc

def _bishop_moves(state, int i):
    return _slide_moves(state, i, [(-1,-1), (-1,1), (1,-1), (1,1)])

def _rook_moves(state, int i):
    return _slide_moves(state, i, [(-1,0), (1,0), (0,-1), (0,1)])

def _queen_moves(state, int i):
    return _slide_moves(state, i, [
        (-1,-1), (-1,1), (1,-1), (1,1),
        (-1,0), (1,0), (0,-1), (0,1)
    ])

def _king_moves(state, int i):
    board, player, castling, ep = state

    cdef int r, c, nr, nc, to
    cdef int dr, dc
    cdef bint wk, wq, bk, bq

    r, c = _i_to_rc(i)

    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr = r + dr
            nc = c + dc
            if not _in_bounds(nr, nc):
                continue
            to = _rc_to_i(nr, nc)
            if not _friendly(player, board[to]):
                yield f"{i}-{to}"

    wk, wq, bk, bq = castling

    if player == 0:
        if i == 60 and not _square_attacked(board, i, 1):
            if wk and board[61] == ' ' and board[62] == ' ' and board[63] == 'R' \
                    and not _square_attacked(board, 61, 1) and not _square_attacked(board, 62, 1):
                yield "60-62"
            if wq and board[59] == ' ' and board[58] == ' ' and board[57] == ' ' and board[56] == 'R' \
                    and not _square_attacked(board, 59, 1) and not _square_attacked(board, 58, 1):
                yield "60-58"
    else:
        if i == 4 and not _square_attacked(board, i, 0):
            if bk and board[5] == ' ' and board[6] == ' ' and board[7] == 'r' \
                    and not _square_attacked(board, 5, 0) and not _square_attacked(board, 6, 0):
                yield "4-6"
            if bq and board[3] == ' ' and board[2] == ' ' and board[1] == ' ' and board[0] == 'r' \
                    and not _square_attacked(board, 3, 0) and not _square_attacked(board, 2, 0):
                yield "4-2"

# ----------------------------
# APPLY MOVE
# ----------------------------

def _parse_move(str move) -> tuple[int, int, str | None]:
    cdef str base, promo, frm_s, to_s
    if '=' in move:
        base, promo = move.split('=')
        frm_s, to_s = base.split('-')
        return int(frm_s), int(to_s), promo
    frm_s, to_s = move.split('-')
    return int(frm_s), int(to_s), None

# NOTE: RESULTS must remain a 'def' method as it is part of the public
# Game interface, but all helpers inside are now cdef calls.

# ----------------------------
# CHECK DETECTION
# ----------------------------

cdef int _find_king(board, int player):
    cdef int i
    cdef str k
    k = 'K' if player == 0 else 'k'
    for i in range(64):
        if board[i] == k:
            return i
    raise ValueError("King not found (illegal state).")

cdef bint _in_check(state, int player):
    board = state[0]
    cdef int king_pos
    king_pos = _find_king(board, player)
    return _square_attacked(board, king_pos, (player + 1) % 2)

cdef bint _square_attacked(tuple board, int sq, int attacker):
    cdef int r, c, nr, nc
    cdef int dr, dc
    cdef str p, knight, bishop, rook, queen, king

    r, c = _i_to_rc(sq)

    # Pawn attacks
    if attacker == 0:
        for dc in (-1, 1):
            nr = r + 1
            nc = c + dc
            if _in_bounds(nr, nc):
                if board[_rc_to_i(nr, nc)] == 'P':
                    return True
    else:
        for dc in (-1, 1):
            nr = r - 1
            nc = c + dc
            if _in_bounds(nr, nc):
                if board[_rc_to_i(nr, nc)] == 'p':
                    return True

    # Knight attacks
    knight = 'N' if attacker == 0 else 'n'
    cdef int[8][2] jumps = [
        [-2, -1], [-2, 1],
        [-1, -2], [-1, 2],
        [1, -2],  [1, 2],
        [2, -1],  [2, 1],
    ]
    for dr, dc in jumps:
        nr = r + dr
        nc = c + dc
        if _in_bounds(nr, nc):
            if board[_rc_to_i(nr, nc)] == knight:
                return True

    # King attacks
    king = 'K' if attacker == 0 else 'k'
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr = r + dr
            nc = c + dc
            if _in_bounds(nr, nc):
                if board[_rc_to_i(nr, nc)] == king:
                    return True

    # Sliding pieces
    bishop = 'B' if attacker == 0 else 'b'
    rook   = 'R' if attacker == 0 else 'r'
    queen  = 'Q' if attacker == 0 else 'q'

    # Diagonals
    for dr, dc in ((-1,-1), (-1,1), (1,-1), (1,1)):
        nr = r + dr
        nc = c + dc
        while _in_bounds(nr, nc):
            p = board[_rc_to_i(nr, nc)]
            if p != ' ':
                if p == bishop or p == queen:
                    return True
                break
            nr += dr
            nc += dc

    # Straights
    for dr, dc in ((-1,0), (1,0), (0,-1), (0,1)):
        nr = r + dr
        nc = c + dc
        while _in_bounds(nr, nc):
            p = board[_rc_to_i(nr, nc)]
            if p != ' ':
                if p == rook or p == queen:
                    return True
                break
            nr += dr
            nc += dc

    return False

class Chess(Game):
    """
    Full Chess implementation on a 8x8 board.

    Board representation:
      - Flat tuple length 64 in row-major order.
      - Index 0 is a8, index 7 is h8
      - Index 56 is a1, index 63 is h1

    Pieces:
      White: 'P','N','B','R','Q','K'
      Black: 'p','n','b','r','q','k'
      Empty: ' '

    State:
      (board, player, castling_rights, enpassant_square)

    Castling rights:
      (white_kingside, white_queenside, black_kingside, black_queenside)

    En passant square:
      index of square that pawn can capture onto, or None.

    Utility:
      Win = 2, Loss = 0, Draw = 1.
    """

    def __init__(self, depth_limit: int, tt_memory_mb: int, horizon_margin : float = 0.2, scale : float = 10.0):
        super().__init__(sum=2, transposition_table_size_mb=tt_memory_mb, margin=horizon_margin)
        self.depth_limit = depth_limit
        # Insufficient material cases
        self.insufficient = (
            ({ 'K': 1 }, { 'k': 1 }),  # K vs K
            ({ 'K': 1, 'B': 1 }, { 'k': 1 }),  # K+B vs K
            ({ 'K': 1, 'N': 1 }, { 'k': 1 }),  # K+N vs K
            ({ 'K': 1 }, { 'k': 1, 'b': 1 }),  # K vs K+B
            ({ 'K': 1 }, { 'k': 1, 'n': 1 }),  # K vs K+N
        )

        self.is_in_early_draw = False
        self.scale = scale

    def TO_MOVE(self, state: StateT) -> PlayerT:
        return state[1]

    # ----------------------------
    # INITIAL STATE
    # ----------------------------
    @staticmethod
    def INITIAL_STATE() -> StateT:
        board = [
            'r','n','b','q','k','b','n','r',
            'p','p','p','p','p','p','p','p',
            ' ',' ',' ',' ',' ',' ',' ',' ',
            ' ',' ',' ',' ',' ',' ',' ',' ',
            ' ',' ',' ',' ',' ',' ',' ',' ',
            ' ',' ',' ',' ',' ',' ',' ',' ',
            'P','P','P','P','P','P','P','P',
            'R','N','B','Q','K','B','N','R'
        ]
        castling = (True, True, True, True)
        return tuple( board ), 0, castling, None

    # ----------------------------
    # MOVE GENERATION CORE
    # ----------------------------

    def ACTIONS(self, state: StateT) -> Iterator[MoveT]:
        board, player, castling, ep = state

        # Generate pseudo-legal moves, then filter legality.
        for mv in _pseudo_legal_moves(state):
            new_state = self.RESULTS(state, mv)
            if not _in_check(new_state, player):
                yield mv

    def QUIESCENCE_ACTIONS(self, state: StateT) -> Iterator[MoveT]:
        """
        For quiescence: return only "noisy" moves (captures + promotions).
        """
        board, player, castling, ep = state

        if self.IS_TERMINAL(state):
            return iter(())

        for mv in _pseudo_legal_moves(state):
            new_state = self.RESULTS( state, mv )
            if _in_check( new_state, player ):
                continue

            frm, to, promo = _parse_move(mv)

            # capture?
            if board[to] != ' ':
                yield mv

            # en passant capture?
            if ep is not None and to == ep:
                piece = board[frm]
                if piece == _pawn_piece(player):
                    yield mv

            # promotion?
            if promo is not None:
                yield mv

    # ----------------------------
    # PSEUDO LEGAL MOVES (ignore check)
    # ----------------------------

    def RESULTS(self, state, action):
        board, player, castling, ep = state

        cdef int frm, to
        cdef str piece, promo
        cdef int capture_r, capture_i
        cdef int fr, fc, tr, tc, mid_r
        cdef bint wk, wq, bk, bq

        frm, to, promo = _parse_move(action)

        piece = board[frm]
        wk, wq, bk, bq = castling
        new_castling = [wk, wq, bk, bq]
        new_ep = None
        new_board = list(board)

        # En passant capture
        if (piece == 'P' or piece == 'p') and ep is not None and to == ep and board[to] == ' ':
            tr, tc = _i_to_rc(to)
            capture_r = tr + (1 if player == 0 else -1)
            capture_i = _rc_to_i(capture_r, tc)
            new_board[capture_i] = ' '

        new_board[frm] = ' '
        new_board[to] = piece

        if promo is not None:
            new_board[to] = promo

        if piece == 'P' or piece == 'p':
            fr, fc = _i_to_rc(frm)
            tr, tc = _i_to_rc(to)
            if abs(tr - fr) == 2:
                mid_r = (fr + tr) // 2
                new_ep = _rc_to_i(mid_r, fc)

        if piece == 'K' or piece == 'k':
            if player == 0:
                new_castling[0] = False
                new_castling[1] = False
            else:
                new_castling[2] = False
                new_castling[3] = False

            if frm == 60 and to == 62:
                new_board[63] = ' ';
                new_board[61] = 'R'
            elif frm == 60 and to == 58:
                new_board[56] = ' ';
                new_board[59] = 'R'
            elif frm == 4 and to == 6:
                new_board[7] = ' ';
                new_board[5] = 'r'
            elif frm == 4 and to == 2:
                new_board[0] = ' ';
                new_board[3] = 'r'

        if frm == 63 or to == 63: new_castling[0] = False
        if frm == 56 or to == 56: new_castling[1] = False
        if frm == 7 or to == 7:  new_castling[2] = False
        if frm == 0 or to == 0:  new_castling[3] = False

        return tuple(new_board), (player + 1) % 2, tuple(new_castling), new_ep

    # ----------------------------
    # TERMINAL / UTILITY
    # ----------------------------

    def IS_TERMINAL(self, state: StateT) -> bool:
        board, player, castling, ep = state

        # Material count (ignore empty squares)
        counts = Counter( p for p in board if p != ' ' )

        # Extract piece-sets for each side
        white = { p: counts[ p ] for p in counts if p.isupper( ) }
        black = { p: counts[ p ] for p in counts if p.islower( ) }

        if (white, black) in self.insufficient:
            self.is_in_early_draw = True
            return True

        self.is_in_early_draw = False

        # If player has no legal moves
        for _ in self.ACTIONS(state):
            return False

        # No moves: either checkmate or stalemate
        return True

    def UTILITY(self, state: StateT) -> dict[PlayerT, float]:
        board, player, castling, ep = state

        if not self.IS_TERMINAL(state):
            raise ValueError("UTILITY called on non-terminal state")
        elif self.is_in_early_draw:
            return {0 : 1, 1 : 1} # The game is in a state where checking is impossible

        # player is the side to move (and has no moves if terminal)
        in_check = _in_check(state, player)

        if in_check:
            # checkmate: current player loses
            winner = (player + 1) % 2
            return {winner: 2, player: 0}
        else:
            # stalemate draw
            return {0: 1, 1: 1}

    # ----------------------------
    # EVALUATION
    # ----------------------------

    def EVAL(self, state: StateT) -> dict[PlayerT, float]:
        if self.IS_TERMINAL(state):
            return self.UTILITY(state)

        board, player, castling, ep = state

        piece_values = {
            'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0,
            'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0
        }

        white = 0.0
        black = 0.0

        for i, p in enumerate(board):
            if p == ' ':
                continue

            val = piece_values[p]

            # small positional bonus: pawns advanced, center control
            r, c = _i_to_rc(i)

            if p == 'P':
                val += (6 - r) * 0.05
            elif p == 'p':
                val += (r - 1) * 0.05

            if c in (3, 4) and r in (3, 4):
                val += 0.1

            if p.isupper():
                white += val
            else:
                black += val

        # Normalize into your [0,2] style:
        # baseline 1, advantage shifts toward 2.
        diff = white - black
        normalized = math.tanh(diff / self.scale)
        return {0: 1 + normalized, 1: 1 - normalized}

    # ----------------------------
    # CUTOFF
    # ----------------------------

    def IS_CUTOFF(self, state: StateT, depth: int) -> bool:
        assert depth >= 0
        return depth >= self.depth_limit or self.IS_TERMINAL(state)