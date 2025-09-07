from typing import Iterable, Callable
from abc import ABC, abstractmethod

from ... import SearchProblem

class PartiallyObservableProblem[S,A,P](ABC, SearchProblem):
  @abstractmethod
  def PERCEPT(self, state) -> None | P: # Returns None for sensorless, returns the state for observable, or it returns a percept describing the state
    raise NotImplementedError

  @abstractmethod
  def PREDICT(self, state : S, action : A) -> set[S]: # Equivalent to RESULTSp
    raise NotImplementedError

  @abstractmethod
  def ACTIONSp(self, state : S) -> set[A]:
    raise NotImplementedError

  @abstractmethod
  def ACTION_COSTp(self, state : S, action : A, new_state : S) -> float:
    raise NotImplementedError

  def POSSIBLE_PERCEPTS(self, belief_state : set[S]) -> set[P | None]:
    possible_percepts : set[P] = set()
    for o in (self.PERCEPT(state) for state in belief_state):
      possible_percepts.add(o)

    return possible_percepts

  def UPDATE(self, belief_state : set[S], percept : P) -> set[S]:
    return {state for state in belief_state if percept == self.PERCEPT(state)}

  def RESULTS(self, belief_state : set[S], action : A) -> Iterable[set[S]]:
    new_belief_state : set[S] = set().union(*(self.PREDICT(state=state,action=action) for state in belief_state))
    for percept in self.POSSIBLE_PERCEPTS(belief_state=new_belief_state):
      yield self.UPDATE(new_belief_state, percept)

  def ACTIONS(self, belief_state : set[S], allow_illegal_actions: bool = False) -> set[A]:
    actions = self.ACTIONSp( state=belief_state.pop( ) )
    for state in belief_state:
      if allow_illegal_actions:
        actions |= self.ACTIONS( state )
      else:
        actions &= self.ACTIONS( state )

    return actions

  def ACTION_COST(self, belief_state : set[S], action : A, new_belief_state : set[S]) -> float:
    costs = (
        self.ACTION_COSTp(state=state, action=action, new_state=new_state)
        for state in belief_state
        for new_state in self.PREDICT(state=state, action=action)
        if new_state in new_belief_state
    )

    return max(costs, default=float("inf"))

  def EVALUATION_SCORE(self, belief_state : set[S], action : A, new_belief_state : set[S], heuristic : Callable[[S], float]) -> float:
    evaluation_score = (
        self.ACTION_COSTp(state=state, action=action, new_state=new_state) + heuristic(state)
        for state in belief_state
        for new_state in self.PREDICT(state=state, action=action)
        if new_state in new_belief_state
    )

    return max(evaluation_score, default=float("inf"))