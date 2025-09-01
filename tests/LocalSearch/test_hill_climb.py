from Problems.eight_queen_problem import EightQueenProblem
from Chapter3.SearchProblemPackage.node import Node
from Chapter4.LocalSearch.hill_climbing import hill_climbing_search

def test_hill_climbing():
    initial_state = EightQueenProblem.random_initial_state()
    problem = EightQueenProblem(initial_state)

    result : Node = hill_climbing_search(problem=problem, objective_function=lambda node: -problem.heuristic(node), sideway_moves_allowed=100)
    assert result is not None
    assert problem.IS_GOAL(result.state) or problem.heuristic(result) < problem.heuristic(Node(problem.initial_state))