from src.aima_toolkit.Problems import PartiallyObservableVacuumWorld, SensorlessVacuumWorld, VacuumWorld
from src.aima_toolkit.SearchProblemPackage import SearchStatus
from src.aima_toolkit.SearchProblemPackage.SearchAlgorithms.NondeterministicSearch.Uninformed import nondeterministic_uniform_cost_search
from src.aima_toolkit.SearchProblemPackage.SearchAlgorithms.NondeterministicSearch.Informed import and_or_star_search
from src.aima_toolkit.SearchProblemPackage.SearchAlgorithms.UninformedSearch import uniform_cost_search
from pprint import pprint

def heuristic(state : frozenset[int]) -> float:
  return max(VacuumWorld.clean_square_heuristic(s) for s in state)

def test_solution():
  problem = PartiallyObservableVacuumWorld(initial_state=frozenset({1,3}))

  print("\n\n\n")
  status1, result1 = and_or_star_search(problem, heuristic=heuristic)
  status2, result2 = nondeterministic_uniform_cost_search(problem)
  assert status1 == status2 == SearchStatus.SUCCESS
  assert result1 == result2 == {frozenset({1, 3}): {'action': 'Suck',
                      'outcomes': {frozenset({5, 7}): {'action': 'Right',
                                                       'outcomes': {frozenset({6}): {'action': 'Suck',
                                                                                     'outcomes': {frozenset({8}): {}}},
                                                                    frozenset({8}): {}}}}}}

def test_sensorless():
  problem = SensorlessVacuumWorld(initial_state=frozenset({1,2,3,4,5,6,7,8}))
  assert uniform_cost_search(problem).get_actions() in [["Right", "Suck", "Left", "Suck"], ["Left", "Suck", "Right", "Suck"]]
