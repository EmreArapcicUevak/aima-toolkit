from Chapter3.SearchProblemPackage.search_problem import *
from Chapter3.SearchProblemPackage.queue import FIFO_Queue
from Chapter3.SearchProblemPackage.node import Node
from Chapter3.SearchProblemPackage.expand import expand


def breadth_first_search(problem: Search_Problem):
    node = Node(problem.initial_state)
    if problem.IS_GOAL(node.state):
        return node

    frontier = FIFO_Queue()
    frontier.push(node)

    reached = [problem.initial_state]

    while len(frontier) > 0:
        node = frontier.pop()

        for child in expand(problem=problem, node=node):
            if problem.IS_GOAL(child.state):
                return child
            elif child.state not in reached:
                reached.append(child.state)
                frontier.push(child)

    return SearchStatus.FAILURE
