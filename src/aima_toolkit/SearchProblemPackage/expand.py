from .node import *
from .searchproblem import SearchProblem

def expand(problem : SearchProblem, node : Node):
  state = node.state

  for action in problem.ACTIONS(state):
    new_state = list(problem.RESULTS(state=state, action=action))
    assert len(new_state) == 1, "classical expand used on non deterministic problem"

    new_state = new_state[0]
    cost = node.path_cost + problem.ACTION_COST(state = state, action = action, new_state = new_state)

    yield Node(new_state, parent=node, path_cost= cost, action=action)

def local_expand(problem: SearchProblem, node : Node):
    """
    Takes a node and expands it locally, not saving the path and only showing nodes that are local
    :param problem:
    :param node:
    :return:
    """
    state = node.state

    for action in problem.ACTIONS(state):
      new_state = list( problem.RESULTS( state=state, action=action ) )
      assert len( new_state ) == 1, "classical local expand used on non deterministic problem"
      new_state = new_state[ 0 ]

      yield Node(new_state)

def nondeterministic_expand(problem: SearchProblem, node : Node):
  state = node.state
  for action in problem.ACTIONS(state):
    new_belief_state = problem.RESULTS(state=state, action=action)
    or_nodes : list[Node] = []

    for new_state in new_belief_state:
      cost = node.path_cost + problem.ACTION_COST( state=state, action=action, new_state=new_state)
      or_nodes.append( OrNode(new_state, action=action, path_cost=cost, parent=node) )

    yield  AndNode(tuple(or_nodes))

__all__ = ['expand', 'local_expand', 'nondeterministic_expand']