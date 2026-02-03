import numpy

from .Game import Game
import math
import numpy as np

def minmax_search[StateT,MoveT, PlayerT](game : Game[StateT, MoveT, PlayerT], state : StateT , * , margin : float = math.inf, singularity_ply : int = 1) -> tuple[dict[PlayerT, float], MoveT | None]:
  assert singularity_ply >= 1

  return _search(game, state, depth=0, margin=margin, singularity_ply=singularity_ply)

def _search[StateT,MoveT, PlayerT](game : Game[StateT, MoveT, PlayerT], state : StateT, * , depth : int , margin : float, singularity_ply : int) -> tuple[dict[PlayerT, float], MoveT | None]:
  if game.IS_CUTOFF(state, depth): return (game.EVAL(state), None)

  current_player : PlayerT = game.TO_MOVE(state)
  best_score : dict[PlayerT, float] = {current_player: -math.inf}
  best_move : MoveT | None = None
  scores = np.empty()

  for action in game.ACTIONS(state):
    result_state = game.RESULTS(state, action)
    new_score, _ = _search(game, result_state, depth=depth+1, singularity_ply=singularity_ply)

    scores = np.append(scores, new_score[current_player])
    if new_score[current_player] > best_score[current_player]:
      best_score = new_score
      best_move = action

  singularity_state = game.RESULTS( state, best_move )

  scores_delta = best_score[current_player] - scores
  num_of_neighbors = (scores_delta <= margin).sum() - 1

  if num_of_neighbors != 0: # No Singularity
    return best_score, best_move

  extended_score, _ = _ply_search(game, singularity_state, ply=singularity_ply) # get the new score and action

  return extended_score, best_move

def _ply_search[StateT,MoveT, PlayerT](game : Game[StateT, MoveT, PlayerT], state : StateT, * , ply : int) -> tuple[dict[PlayerT, float], MoveT | None]:
  assert ply >= 0
  if game.IS_TERMINAL(state) or ply == 0: return game.EVAL(state), None

  current_player : PlayerT = game.TO_MOVE(state)
  best_score : dict[PlayerT, float] = {current_player: -math.inf}
  best_move : MoveT | None = None

  for action in game.ACTIONS(state):
    result_state = game.RESULTS(state, action)
    new_score, _ = _ply_search(game, result_state, ply=ply - 1)

    if new_score[current_player] > best_score[current_player]:
      best_score = new_score
      best_move = action

  return best_score, best_move


__all__ = ['minmax_search']
