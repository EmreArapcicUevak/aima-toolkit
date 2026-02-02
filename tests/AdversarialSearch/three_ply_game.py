from typing import Iterable

from aima_toolkit.AdversarialSearch import Game, minmax_search

class three_ply_game(Game):

  def __init__(self):
    super().__init__()
    self.transitions = {
      'A' : {
        'left' : 'B1',
        'right' : 'B2',
      },
      'B1' : {
        'left' : 'C1',
        'right' : 'C2',
      },
      'B2' : {
        'left' : 'C3',
        'right' : 'C4',
      },
      'C1' : {
        'left' : 'D1',
        'right' : 'D2',
      },
      'C2' : {
        'left' : 'D3',
        'right' : 'D4',
      },
      'C3' : {
        'left' : 'D5',
        'right' : 'D6',
      },
      'C4' : {
        'left' : 'D7',
        'right' : 'D8',
      }
    }

    self.utilities = {
      'D1' : {'A' : 1, 'B' : 2, 'C' : 6},
      'D2' : {'A' : 4, 'B' : 2, 'C' : 3},
      'D3' : {'A' : 6, 'B' : 1, 'C' : 2},
      'D4' : {'A' : 7, 'B' : 4, 'C' : 1},
      'D5' : {'A' : 5, 'B' : 1, 'C' : 1},
      'D6' : {'A' : 0, 'B' : 5, 'C' : 2},
      'D7' : {'A' : 7, 'B' : 7, 'C' : 1},
      'D8' : {'A' : 5, 'B' : 4, 'C' : 5},
    }
  def TO_MOVE(self, state: str) -> str:
    return state[0]

  def ACTIONS(self, state: str) -> Iterable[str]:
    yield 'left'
    yield 'right'

  def RESULTS(self, state: str, action: str) -> str:
    return self.transitions[state][action]


  def IS_TERMINAL(self, state: str) -> bool:
    return state in self.utilities.keys()

  def UTILITY(self, state: str) -> dict[str, float]:
    return self.utilities[state].copy()


def test_three_ply_game_minmax_search():
  game = three_ply_game()
  expected_utility = {'A' : 1, 'B' : 2, 'C' : 6}
  cur_state = 'A'

  while not game.IS_TERMINAL(cur_state):
    utility, action = minmax_search(game, cur_state)
    assert action == 'left'
    assert utility == expected_utility
    cur_state = game.RESULTS(cur_state, action)