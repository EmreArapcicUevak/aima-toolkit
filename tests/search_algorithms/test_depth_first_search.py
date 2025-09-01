from tests.problems.tree_search_problem import *
from Chapter3.depth_first_search import depth_first_search
from Chapter3.SearchProblemPackage.search_problem import SearchStatus

def test_A_to_G():
    problem = Tree_Search_Problem(initial_state='A', goal_state='G')
    result_node = depth_first_search(problem)

    assert result_node != SearchStatus.FAILURE
    assert result_node.get_path() == ['A', 'C', 'G']

def test_A_to_H():
    problem = Tree_Search_Problem(initial_state='A', goal_state='H')
    result_node = depth_first_search(problem)

    assert result_node == SearchStatus.FAILURE

def test_A_to_A():
    problem = Tree_Search_Problem(initial_state='A', goal_state='A')
    result_node = depth_first_search(problem)

    assert result_node != SearchStatus.FAILURE
    assert result_node.get_path() == ['A']

def test_A_to_B():
    problem = Tree_Search_Problem(initial_state='A', goal_state='B')
    result_node = depth_first_search(problem)

    assert result_node != SearchStatus.FAILURE
    assert result_node.get_path() == ['A', 'B']

def test_A_to_C():
    problem = Tree_Search_Problem(initial_state='A', goal_state='C')
    result_node = depth_first_search(problem)

    assert result_node != SearchStatus.FAILURE
    assert result_node.get_path() == ['A', 'C']

def test_A_to_D():
    problem = Tree_Search_Problem(initial_state='A', goal_state='D')
    result_node = depth_first_search(problem)

    assert result_node != SearchStatus.FAILURE
    assert result_node.get_path() == ['A', 'B', 'D']

def test_A_to_E():
    problem = Tree_Search_Problem(initial_state='A', goal_state='E')
    result_node = depth_first_search(problem)

    assert result_node != SearchStatus.FAILURE
    assert result_node.get_path() == ['A', 'B', 'E']