from src.aima_toolkit.Problems import PartiallyObservableVacuumWorld, SensorlessVacuumWorld
from src.aima_toolkit.SearchProblemPackage.SearchAlgorithms.NondeterministicSearch.Uninformed import nondeterministic_uniform_cost_search
from pprint import pprint
def test_solution():
  problem = PartiallyObservableVacuumWorld(initial_state=frozenset({1,3}))
  print("\n\n\n")
  pprint(nondeterministic_uniform_cost_search(problem))


def test_sensorless():
  problem = SensorlessVacuumWorld(initial_state=frozenset({1,2,3,4,5,6,7,8}))