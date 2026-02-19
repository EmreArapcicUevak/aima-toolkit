from __future__ import annotations
from typing import Iterator

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

    def __init__(self, depth_limit: int):
        super().__init__(sum=2)
        self.depth_limit = depth_limit

    # ----------------------------
    # BASIC HELPERS
    # ----------------------------

    def TO_MOVE(self, state: StateT) -> PlayerT:
        return state[1]

    def _is_white(self, piece: str) -> bool:
        return piece.isupper()

    def _is_black(self, piece: str) -> bool:
        return piece.islower()

    def _enemy(self, player: PlayerT, piece: str) -> bool:
        if piece == ' ':
            return False
        return (player == 0 and self._is_black(piece)) or (player == 1 and self._is_white(piece))

    def _friendly(self, player: PlayerT, piece: str) -> bool:
        if piece == ' ':
            return False
        return (player == 0 and self._is_white(piece)) or (player == 1 and self._is_black(piece))

    def _in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < 8 and 0 <= c < 8

    def _rc_to_i(self, r: int, c: int) -> int:
        return r * 8 + c

    def _i_to_rc(self, i: int) -> tuple[int, int]:
        return i // 8, i % 8

    def _king_piece(self, player: PlayerT) -> str:
        return 'K' if player == 0 else 'k'

    def _pawn_piece(self, player: PlayerT) -> str:
        return 'P' if player == 0 else 'p'

    def _back_rank(self, player: PlayerT) -> int:
        return 7 if player == 0 else 0

    def _promotion_rank(self, player: PlayerT) -> int:
        return 0 if player == 0 else 7

    # ----------------------------
    # INITIAL STATE
    # ----------------------------

    def INITIAL_STATE(self) -> StateT:
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

        # If terminal, no moves.
        if self.IS_TERMINAL(state):
            return iter(())

        # Generate pseudo-legal moves, then filter legality.
        for mv in self._pseudo_legal_moves(state):
            new_state = self.RESULTS(state, mv)
            if not self._in_check(new_state, player):
                yield mv

    def QUIESCENCE_ACTIONS(self, state: StateT) -> Iterator[MoveT]:
        """
        For quiescence: return only "noisy" moves (captures + promotions).
        """
        board, player, castling, ep = state

        if self.IS_TERMINAL(state):
            return iter(())

        for mv in self._pseudo_legal_moves(state):
            new_state = self.RESULTS( state, mv )
            if self._in_check( new_state, player ):
                continue

            frm, to, promo = self._parse_move(mv)

            # capture?
            if board[to] != ' ':
                yield mv

            # en passant capture?
            if ep is not None and to == ep:
                piece = board[frm]
                if piece == self._pawn_piece(player):
                    yield mv

            # promotion?
            if promo is not None:
                yield mv

    # ----------------------------
    # PSEUDO LEGAL MOVES (ignore check)
    # ----------------------------

    def _pseudo_legal_moves(self, state: StateT) -> Iterator[MoveT]:
        board, player, castling, ep = state

        for i in range(64):
            piece = board[i]
            if not self._friendly(player, piece):
                continue

            if piece in ('P', 'p'):
                yield from self._pawn_moves(state, i)
            elif piece in ('N', 'n'):
                yield from self._knight_moves(state, i)
            elif piece in ('B', 'b'):
                yield from self._bishop_moves(state, i)
            elif piece in ('R', 'r'):
                yield from self._rook_moves(state, i)
            elif piece in ('Q', 'q'):
                yield from self._queen_moves(state, i)
            elif piece in ('K', 'k'):
                yield from self._king_moves(state, i)

    def _pawn_moves(self, state: StateT, i: int) -> Iterator[MoveT]:
        board, player, castling, ep = state
        r, c = self._i_to_rc(i)

        direction = -1 if player == 0 else 1
        start_row = 6 if player == 0 else 1
        promo_row = self._promotion_rank(player)

        # forward 1
        nr = r + direction
        if self._in_bounds(nr, c):
            to = self._rc_to_i(nr, c)
            if board[to] == ' ':
                # promotion?
                if nr == promo_row:
                    for p in "QRBN":
                        promo_piece = p if player == 0 else p.lower()
                        yield f"{i}-{to}={promo_piece}"
                else:
                    yield f"{i}-{to}"

                # forward 2
                if r == start_row:
                    nnr = r + 2 * direction
                    to2 = self._rc_to_i(nnr, c)
                    if board[to2] == ' ':
                        yield f"{i}-{to2}"

        # captures
        for dc in (-1, 1):
            nc = c + dc
            nr = r + direction
            if not self._in_bounds(nr, nc):
                continue
            to = self._rc_to_i(nr, nc)

            # normal capture
            if self._enemy(player, board[to]):
                if nr == promo_row:
                    for p in "QRBN":
                        promo_piece = p if player == 0 else p.lower()
                        yield f"{i}-{to}={promo_piece}"
                else:
                    yield f"{i}-{to}"

            # en passant capture
            if ep is not None and to == ep:
                yield f"{i}-{to}"

    def _knight_moves(self, state: StateT, i: int) -> Iterator[MoveT]:
        board, player, castling, ep = state
        r, c = self._i_to_rc(i)

        jumps = [
            (-2, -1), (-2, 1),
            (-1, -2), (-1, 2),
            (1, -2),  (1, 2),
            (2, -1),  (2, 1),
        ]

        for dr, dc in jumps:
            nr, nc = r + dr, c + dc
            if not self._in_bounds(nr, nc):
                continue
            to = self._rc_to_i(nr, nc)
            if not self._friendly(player, board[to]):
                yield f"{i}-{to}"

    def _slide_moves(self, state: StateT, i: int, directions: list[tuple[int, int]]) -> Iterator[MoveT]:
        board, player, castling, ep = state
        r, c = self._i_to_rc(i)

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            while self._in_bounds(nr, nc):
                to = self._rc_to_i(nr, nc)

                if self._friendly(player, board[to]):
                    break

                yield f"{i}-{to}"

                if self._enemy(player, board[to]):
                    break

                nr += dr
                nc += dc

    def _bishop_moves(self, state: StateT, i: int) -> Iterator[MoveT]:
        return self._slide_moves(state, i, [(-1,-1), (-1,1), (1,-1), (1,1)])

    def _rook_moves(self, state: StateT, i: int) -> Iterator[MoveT]:
        return self._slide_moves(state, i, [(-1,0), (1,0), (0,-1), (0,1)])

    def _queen_moves(self, state: StateT, i: int) -> Iterator[MoveT]:
        return self._slide_moves(state, i, [
            (-1,-1), (-1,1), (1,-1), (1,1),
            (-1,0), (1,0), (0,-1), (0,1)
        ])

    def _king_moves(self, state: StateT, i: int) -> Iterator[MoveT]:
        board, player, castling, ep = state
        r, c = self._i_to_rc(i)

        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0: continue
                nr, nc = r + dr, c + dc
                if not self._in_bounds(nr, nc): continue
                to = self._rc_to_i(nr, nc)
                if not self._friendly(player, board[to]):
                    yield f"{i}-{to}"

        # Castling (pseudo legal; legality check will filter check squares)
        wk, wq, bk, bq = castling

        if player == 0:
            # White king starts at e1 = index 60
            if i == 60:
                # Kingside: e1 -> g1 (60 -> 62)
                if wk and board[61] == ' ' and board[62] == ' ':
                    yield "60-62"
                # Queenside: e1 -> c1 (60 -> 58)
                if wq and board[59] == ' ' and board[58] == ' ' and board[57] == ' ':
                    yield "60-58"
        else:
            # Black king starts at e8 = index 4
            if i == 4:
                # Kingside: e8 -> g8 (4 -> 6)
                if bk and board[5] == ' ' and board[6] == ' ':
                    yield "4-6"
                # Queenside: e8 -> c8 (4 -> 2)
                if bq and board[3] == ' ' and board[2] == ' ' and board[1] == ' ':
                    yield "4-2"

    # ----------------------------
    # APPLY MOVE
    # ----------------------------

    def _parse_move(self, move: MoveT) -> tuple[int, int, str | None]:
        # "12-28" or "52-60=Q"
        if '=' in move:
            base, promo = move.split('=')
            frm_s, to_s = base.split('-')
            return int(frm_s), int(to_s), promo
        frm_s, to_s = move.split('-')
        return int(frm_s), int(to_s), None

    def RESULTS(self, state: StateT, action: MoveT) -> StateT:
        board, player, castling, ep = state
        frm, to, promo = self._parse_move(action)

        piece = board[frm]
        assert self._friendly(player, piece)
        assert not self._friendly(player, board[to])

        wk, wq, bk, bq = castling
        new_castling = [wk, wq, bk, bq]
        new_ep = None

        new_board = list(board)

        # Handle en passant capture
        if piece in ('P', 'p') and ep is not None and to == ep and board[to] == ' ':
            # Captured pawn is behind the ep square
            tr, tc = self._i_to_rc(to)
            capture_r = tr + (1 if player == 0 else -1)
            capture_i = self._rc_to_i(capture_r, tc)
            new_board[capture_i] = ' '

        # Move the piece
        new_board[frm] = ' '
        new_board[to] = piece

        # Promotion
        if promo is not None:
            new_board[to] = promo

        # If pawn moved 2 squares, set en passant
        if piece in ('P', 'p'):
            fr, fc = self._i_to_rc(frm)
            tr, tc = self._i_to_rc(to)
            if abs(tr - fr) == 2:
                mid_r = (fr + tr) // 2
                new_ep = self._rc_to_i(mid_r, fc)

        # Castling move (king moved 2 squares)
        if piece in ('K', 'k'):
            if player == 0:
                # remove white castling rights
                new_castling[0] = False
                new_castling[1] = False
            else:
                new_castling[2] = False
                new_castling[3] = False

            # white king side: 60->62 rook 63->61
            if frm == 60 and to == 62:
                new_board[63] = ' '
                new_board[61] = 'R'
            # white queen side: 60->58 rook 56->59
            elif frm == 60 and to == 58:
                new_board[56] = ' '
                new_board[59] = 'R'

            # black king side: 4->6 rook 7->5
            elif frm == 4 and to == 6:
                new_board[7] = ' '
                new_board[5] = 'r'
            # black queen side: 4->2 rook 0->3
            elif frm == 4 and to == 2:
                new_board[0] = ' '
                new_board[3] = 'r'

        # If rook moved, remove castling rights
        if frm == 63 or to == 63:
            new_castling[0] = False
        if frm == 56 or to == 56:
            new_castling[1] = False
        if frm == 7 or to == 7:
            new_castling[2] = False
        if frm == 0 or to == 0:
            new_castling[3] = False

        # If king captured rook squares, also remove rights
        # (capturing rook indirectly handled by "to == rook square")

        next_player = (player + 1) % 2
        return tuple(new_board), next_player, tuple(new_castling), new_ep

    # ----------------------------
    # CHECK DETECTION
    # ----------------------------

    def _find_king(self, board: tuple[str, ...], player: PlayerT) -> int:
        k = self._king_piece(player)
        for i in range(64):
            if board[i] == k:
                return i
        raise ValueError("King not found (illegal state).")

    def _in_check(self, state: StateT, player: PlayerT) -> bool:
        board, _, castling, ep = state
        king_pos = self._find_king(board, player)
        return self._square_attacked(board, king_pos, attacker=(player + 1) % 2)

    def _square_attacked(self, board: tuple[str, ...], sq: int, attacker: PlayerT) -> bool:
        r, c = self._i_to_rc(sq)

        # Pawn attacks
        if attacker == 0:
            # white pawns attack up-left/up-right (r+1)
            for dc in (-1, 1):
                nr, nc = r + 1, c + dc
                if self._in_bounds(nr, nc):
                    if board[self._rc_to_i(nr, nc)] == 'P':
                        return True
        else:
            # black pawns attack down-left/down-right (r-1)
            for dc in (-1, 1):
                nr, nc = r - 1, c + dc
                if self._in_bounds(nr, nc):
                    if board[self._rc_to_i(nr, nc)] == 'p':
                        return True

        # Knight attacks
        knight = 'N' if attacker == 0 else 'n'
        jumps = [
            (-2, -1), (-2, 1),
            (-1, -2), (-1, 2),
            (1, -2),  (1, 2),
            (2, -1),  (2, 1),
        ]
        for dr, dc in jumps:
            nr, nc = r + dr, c + dc
            if self._in_bounds(nr, nc):
                if board[self._rc_to_i(nr, nc)] == knight:
                    return True

        # King attacks (adjacent)
        king = 'K' if attacker == 0 else 'k'
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if self._in_bounds(nr, nc):
                    if board[self._rc_to_i(nr, nc)] == king:
                        return True

        # Sliding pieces: bishop/rook/queen
        bishop = 'B' if attacker == 0 else 'b'
        rook = 'R' if attacker == 0 else 'r'
        queen = 'Q' if attacker == 0 else 'q'

        # Diagonals
        for dr, dc in [(-1,-1), (-1,1), (1,-1), (1,1)]:
            nr, nc = r + dr, c + dc
            while self._in_bounds(nr, nc):
                p = board[self._rc_to_i(nr, nc)]
                if p != ' ':
                    if p == bishop or p == queen:
                        return True
                    break
                nr += dr
                nc += dc

        # Straights
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nr, nc = r + dr, c + dc
            while self._in_bounds(nr, nc):
                p = board[self._rc_to_i(nr, nc)]
                if p != ' ':
                    if p == rook or p == queen:
                        return True
                    break
                nr += dr
                nc += dc

        return False

    # ----------------------------
    # TERMINAL / UTILITY
    # ----------------------------

    def IS_TERMINAL(self, state: StateT) -> bool:
        board, player, castling, ep = state

        # If player has no legal moves
        has_move = False
        for _ in self.ACTIONS(state):
            has_move = True
            break

        if has_move:
            return False

        # No moves: either checkmate or stalemate
        return True

    def UTILITY(self, state: StateT) -> dict[PlayerT, float]:
        board, player, castling, ep = state

        # player is the side to move (and has no moves if terminal)
        in_check = self._in_check(state, player)

        if not self.IS_TERMINAL(state):
            raise ValueError("UTILITY called on non-terminal state")

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
            r, c = self._i_to_rc(i)

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
        normalized = max(-1.0, min(1.0, diff / 20.0))

        return {0: 1 + normalized, 1: 1 - normalized}

    # ----------------------------
    # CUTOFF
    # ----------------------------

    def IS_CUTOFF(self, state: StateT, depth: int) -> bool:
        assert depth >= 0
        return self.IS_TERMINAL(state) or depth >= self.depth_limit