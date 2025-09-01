from Chapter3.SearchProblemPackage.search_problem import *
from Chapter3.SearchProblemPackage.queue import Priority_Queue
from Chapter3.SearchProblemPackage.node import Node
from Chapter3.SearchProblemPackage.expand import expand

def a_star_search(problem: Search_Problem, heuristic):
  root_node = Node(problem.initial_state)

  frontier = Priority_Queue(evaluation_func=lambda node: node.path_cost + heuristic(node))
  reached = {root_node.state: root_node}

  frontier.push(root_node)
  while len(frontier) > 0:
    node = frontier.pop()

    if problem.IS_GOAL(node.state):
      return node
    elif node.path_cost > reached[node.state].path_cost:
      continue

    for successor in expand(problem=problem, node=node):
      if successor.state not in reached or successor.path_cost < reached[successor.state].path_cost:
        reached[successor.state] = successor
        frontier.push(successor)

  return SearchStatus.FAILURE