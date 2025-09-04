from enum import Enum, auto
from typing import Callable, Union, TypeAlias, Iterable
from .node import Node

Heuristic: TypeAlias = Callable[[Node], Union[int, float]]

class SearchStatus(Enum):
    FAILURE = auto()
    CUTOFF = auto()
    SUCCESS = auto()

class SearchProblem[S, A]:
  def __init__(self, initial_state : S):
    self.initial_state = initial_state

  def ACTIONS(self, state : S) -> set[A] | Iterable[A]:
      """
      Return a set of actions, or iterable over the actions, that can be performed on this search problem.
      Args:
          state:

      Returns:

      """
    raise NotImplementedError("This method should be overridden by subclasses")
  
  def RESULTS(self, state : S, action : A) -> set[S] | Iterable[S]:
    """

    :param state:
    :param action:
    :return:
    """
    raise NotImplementedError("This method should be overridden by subclasses")
  
  def ACTION_COST(self, state : S, action : A, new_state : S) -> float:
    raise NotImplementedError("This method should be overridden by subclasses")
  
  def IS_GOAL(self, state : S) -> bool:
    raise NotImplementedError("This method should be overridden by subclasses")
