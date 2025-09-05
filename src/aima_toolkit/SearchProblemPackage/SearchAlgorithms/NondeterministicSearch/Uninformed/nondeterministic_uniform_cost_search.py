from .... import SearchProblem, AndNode, OrNode, nondeterministic_expand
def nondeterministic_uniform_cost_search(problem : SearchProblem):
  initial_node = OrNode(problem.initial_state)
