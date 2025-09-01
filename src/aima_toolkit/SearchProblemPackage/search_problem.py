from enum import Enum, auto
from typing import Callable, Union, TypeAlias
from Chapter3.SearchProblemPackage.node import  Node

Heuristic: TypeAlias = Callable[[Node], Union[int, float]]

class SearchStatus(Enum):
    FAILURE = auto()
    CUTOFF = auto()
    SUCCESS = auto()

class Search_Problem():
  def __init__(self, initial_state):
    self.initial_state = initial_state

  def  ACTIONS(self, states):
    raise NotImplementedError("This method should be overridden by subclasses")
  
  def RESULTS(self, state, action):
    raise NotImplementedError("This method should be overridden by subclasses")
  
  def ACTION_COST(self, state, action, new_state):
    raise NotImplementedError("This method should be overridden by subclasses")
  
  def IS_GOAL(self, state):
    raise NotImplementedError("This method should be overridden by subclasses")
