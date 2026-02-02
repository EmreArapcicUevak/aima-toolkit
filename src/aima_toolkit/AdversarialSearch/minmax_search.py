from .Game import Game
import math

def minmax_search[StateT,MoveT, PlayerT](game : Game[StateT, MoveT, PlayerT], state : StateT) -> tuple[dict[PlayerT, float], MoveT | None]:
  if game.IS_TERMINAL(state): return (game.UTILITY(state), None)

  current_player : PlayerT = game.TO_MOVE(state)
  best_score : dict[PlayerT, float] = {current_player: -math.inf}
  best_move : MoveT | None = None

  for action in game.ACTIONS(state):
    result_state = game.RESULTS(state, action)
    new_score, action2 = minmax_search(game, result_state)

    if new_score[current_player] > best_score[current_player]:
      best_score = new_score
      best_move = action

  return best_score, best_move
