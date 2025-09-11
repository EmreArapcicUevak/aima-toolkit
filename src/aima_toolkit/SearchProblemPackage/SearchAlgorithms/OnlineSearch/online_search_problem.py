from abc import ABC, abstractmethod
class OnlineSearchProblem[S,A](ABC):
  def __init__(self):
    self.result : dict[S,A] = {}
    self.s : S | None = None
    self.a : A | None = None

  @abstractmethod
  def ACTIONS(self, state : S) -> set[A]:
    pass

  @abstractmethod
  def ACTION_COST(self, state : S, action : A, new_state : S) -> float:
    pass

  @abstractmethod
  def IS_GOAL(self, state : S) -> bool:
    pass