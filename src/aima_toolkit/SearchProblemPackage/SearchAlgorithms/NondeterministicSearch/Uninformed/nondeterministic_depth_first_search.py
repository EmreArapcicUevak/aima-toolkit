from .... import SearchProblem, SearchStatus, AndNode, OrNode
def nondeterministic_depth_first_search[S,A](problem : SearchProblem[S,A]):
  return _or_search(problem, problem.initial_state, [])

def _or_search[S,A](problem : SearchProblem[S,A], state : S, path : list):
  if problem.IS_GOAL(state):
    return []
  elif state in path:
    return SearchStatus.FAILURE

  for action in problem.ACTIONS(state):
    plan = _and_search(
      problem,
      set(
        problem.RESULTS(
          state, action
        )
      ),
      [state] + path
    )

    if plan != SearchStatus.FAILURE:
      return [action] + plan

  return SearchStatus.FAILURE
def _and_search[S,A](problem : SearchProblem[S,A], states : set[S], path : list[S]):
  plan : dict[S,A] = dict()
  for state in states:
    plan_i = _or_search(problem, state, path + [state])
    if plan_i == SearchStatus.FAILURE:
      return SearchStatus.FAILURE
    else:
      plan[state] = plan_i

  return plan
