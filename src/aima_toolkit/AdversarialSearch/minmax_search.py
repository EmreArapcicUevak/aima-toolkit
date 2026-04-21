from logging import getHandlerNames

import numpy

from .Game import Game

import math
import numpy as np
from typing import Iterator

def minmax_search[StateT,MoveT, PlayerT](game : Game[StateT, MoveT, PlayerT], state : StateT , * , singularity_ply : int = 1, quiescence_search_limit : int = -1) -> tuple[dict[PlayerT, float], MoveT | None]:
  assert singularity_ply >= 1
  assert quiescence_search_limit >= 1 or quiescence_search_limit == -1

  return _search(game, state, depth=0, singularity_ply=singularity_ply,  bound=game.sum, quiescence_search_limit=quiescence_search_limit)

def _search[StateT,MoveT, PlayerT](game : Game[StateT, MoveT, PlayerT], state : StateT, * , depth : int, singularity_ply : int, bound : float, quiescence_search_limit : int) -> tuple[dict[PlayerT, float], MoveT | None]:
  if game.IS_CUTOFF(state, depth): return _quiescence_search(game, state, bound=bound, depth_limit = quiescence_search_limit), None

  actions, state_hash = game.ACTIONS(state), hash(state)
  current_player : PlayerT = game.TO_MOVE(state)

  tt_result = game.transposition_table.probe(key=state_hash, player=current_player, actions=actions)
  if tt_result is not None:
    return tt_result

  best_move, best_move_idx = next(actions, None), 0
  assert best_move is not None
  next_state = game.RESULTS(state, best_move)

  best_score, _  = _search(game, next_state, depth=depth+1, singularity_ply=singularity_ply, bound=bound, quiescence_search_limit=quiescence_search_limit)
  best_node_is_cutoff = False

  scores = np.array([best_score[current_player]])

  for move_idx, action in enumerate(actions):
    if best_score[current_player] >= bound: # Shallow pruning
      game.transposition_table.store( key=state_hash, depth=depth, score=best_score[ current_player ], flag=1, move=move_idx + 1 )
      return best_score, best_move

    result_state = game.RESULTS(state, action)
    new_score, _ = _search(game, result_state, depth=depth+1, singularity_ply=singularity_ply, bound=game.sum-best_score[current_player], quiescence_search_limit=quiescence_search_limit)

    scores = np.append(scores, new_score[current_player])
    if new_score[current_player] > best_score[current_player]:
      best_score = new_score
      best_move = action
      best_move_idx = move_idx + 1
      best_node_is_cutoff = game.IS_CUTOFF(state, depth=depth+1)

  singularity_state = game.RESULTS( state, best_move )

  scores_delta = best_score[current_player] - scores
  num_of_neighbors = (scores_delta <= game.margin).sum() - 1

  if best_node_is_cutoff == False or num_of_neighbors != 0: # No Singularity at the cutoff node
    game.transposition_table.store(key=state_hash, depth=depth, score=best_score[current_player], flag=0, move=best_move_idx)
    return best_score, best_move

  extended_score, _ = _ply_search(game, singularity_state, ply=singularity_ply) # get the new score and action
  game.transposition_table.store( key=state_hash, depth=depth, score=best_score[ current_player ], flag=2, move=best_move_idx)

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

def _quiescence_search[StateT,MoveT, PlayerT](game : Game[StateT, MoveT, PlayerT], state : StateT, bound : float, depth_limit : int) -> dict[PlayerT, float]:
  if game.IS_TERMINAL(state) or depth_limit == 0: return game.EVAL(state)

  actions, state_hash = game.QUIESCENCE_ACTIONS(state), hash(state)
  current_player : PlayerT = game.TO_MOVE(state)

  tt_result = game.transposition_table.probe(key=state_hash, player=current_player, actions=actions)
  if tt_result is not None:
    return tt_result[0]

  first_move = next(actions, None)
  if first_move is None:
    return game.EVAL(state)

  next_state = game.RESULTS(state, first_move)
  next_depth = depth_limit - 1 if depth_limit != -1 else depth_limit

  best_score = _quiescence_search(game, next_state, game.sum, next_depth)

  for action in actions:
    if best_score[current_player] >= bound: # Shallow pruning
      return best_score

    result_state = game.RESULTS(state, action)
    new_score  = _quiescence_search(game, result_state, game.sum - best_score[current_player], next_depth)

    if new_score[current_player] > best_score[current_player]:
      best_score = new_score

  return best_score

__all__ = ['minmax_search']
