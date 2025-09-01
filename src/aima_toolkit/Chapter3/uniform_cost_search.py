from Chapter3.SearchProblemPackage.search_problem import *
from Chapter3.SearchProblemPackage.expand import expand
from Chapter3.SearchProblemPackage.node import Node
from Chapter3.SearchProblemPackage.queue import Priority_Queue

def uniform_cost_search(problem : Search_Problem):
  node = Node(problem.initial_state)
  if problem.IS_GOAL(node.state):
    return node
  
  frontier = Priority_Queue(lambda node: node.path_cost)
  frontier.push(node)

  reached = {problem.initial_state: node}
  
  while len(frontier) > 0:
    node = frontier.pop()

    if node.path_cost > reached[node.state].path_cost:
      continue
    elif problem.IS_GOAL(node.state):
      return node

    for child in expand(problem=problem, node=node):
      if child.state not in reached.keys() or child.path_cost < reached[child.state].path_cost:
        reached[child.state] = child
        frontier.push(child)

  return SearchStatus.FAILURE