from Chapter3.SearchProblemPackage.search_problem import *
from Chapter3.SearchProblemPackage.queue import Stack
from Chapter3.SearchProblemPackage.node import Node
from Chapter3.SearchProblemPackage.expand import expand

def depth_limited_search(problem : Search_Problem, limit : int):
  frontier = Stack()
  frontier.push(Node(problem.initial_state))

  result = SearchStatus.FAILURE
  while len(frontier) > 0:
    node = frontier.pop()

    if problem.IS_GOAL(node.state):
      return node

    if node.depth < limit:
      for child in expand(problem=problem, node=node):
        frontier.push(child)
    else:
      result = SearchStatus.CUTOFF

  return result