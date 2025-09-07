from typing import Iterable

from ... import SearchProblem

class PartiallyObservableProblem[S,A,P](SearchProblem[S,A]):
  def PERCEPT(self, state) -> None | P | set[P | None]:
    raise NotImplementedError()

  def PREDICT(self, state : S, action : A) -> set[S]:
    raise NotImplementedError()

  def POSSIBLE_PERCEPTS(self, belief_state : set[S]) -> set[P | None]:
    possible_percepts : set[P] = set()
    for o in (self.PERCEPT(state) for state in belief_state):
      if isinstance(o, set):
        possible_percepts |= o
      else:
        possible_percepts.add(o)

    return possible_percepts

  def UPDATE(self, belief_state : set[S], percept : P) -> set[S]:
    return {state for state in belief_state if percept == self.PERCEPT(state)}

  def RESULTS(self, belief_state : set[S], action : A) -> Iterable[set[S]]:
    new_belief_state : set[S] = set().union(*(self.PREDICT(state=state,action=action) for state in belief_state))
    for percept in self.POSSIBLE_PERCEPTS(belief_state=new_belief_state):
      yield self.UPDATE(new_belief_state, percept)
