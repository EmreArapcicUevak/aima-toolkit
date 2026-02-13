from logging import getHandlerNames

import numpy

from .Game import Game
import math
import numpy as np

def minmax_search[StateT,MoveT, PlayerT](game : Game[StateT, MoveT, PlayerT], state : StateT , * , margin : float = math.inf, singularity_ply : int = 1) -> tuple[dict[PlayerT, float], MoveT | None]:
  assert singularity_ply >= 1

  return _search(game, state, depth=0, margin=margin, singularity_ply=singularity_ply,  bound=game.sum)

def _search[StateT,MoveT, PlayerT](game : Game[StateT, MoveT, PlayerT], state : StateT, * , depth : int , margin : float, singularity_ply : int, bound : float) -> tuple[dict[PlayerT, float], MoveT | None]:
  if game.IS_CUTOFF(state, depth): return _quiescence_search(game, state), None

  current_player : PlayerT = game.TO_MOVE(state)

  actions = iter(game.ACTIONS(state))
  best_move = next(actions, None)

  assert best_move is not None
  next_state = game.RESULTS(state, best_move)

  best_score, _  = _search(game, next_state, depth=depth+1, margin=margin, singularity_ply=singularity_ply, bound=game.sum)
  best_node_is_cutoff = False

  scores = np.array([])

  for action in actions:
    if best_score[current_player] >= bound: # Shallow pruning
      return best_score, best_move

    result_state = game.RESULTS(state, action)
    new_score, _ = _search(game, result_state, depth=depth+1, singularity_ply=singularity_ply, margin=margin, bound=game.sum-best_score[current_player])

    scores = np.append(scores, new_score[current_player])
    if new_score[current_player] > best_score[current_player]:
      best_score = new_score
      best_move = action
      best_node_is_cutoff = game.IS_CUTOFF(state, depth=depth+1)

  singularity_state = game.RESULTS( state, best_move )

  scores_delta = best_score[current_player] - scores
  num_of_neighbors = (scores_delta <= margin).sum() - 1

  if best_node_is_cutoff == False or num_of_neighbors != 0: # No Singularity at the cutoff node
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

def _quiescence_search[StateT,MoveT, PlayerT](game : Game[StateT, MoveT, PlayerT], state : StateT) -> dict[PlayerT, float]:
  if game.IS_TERMINAL(state): return game.EVAL(state)

  current_player : PlayerT = game.TO_MOVE(state)
  best_score : dict[PlayerT, float] = {current_player: -math.inf}

  is_quiescence_state = True

  for action in game.QUIESCENCE_ACTIONS(state):
    is_quiescence_state = False
    result_state = game.RESULTS(state, action)
    new_score  = _quiescence_search(game, result_state)

    if new_score[current_player] > best_score[current_player]:
      best_score = new_score

  if is_quiescence_state:
    return game.EVAL(state)
  else:
    return best_score

__all__ = ['minmax_search']
