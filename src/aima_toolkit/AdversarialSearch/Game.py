from abc import abstractmethod, ABC
from typing import Iterable
class Game[StateT, MoveT, PlayerT](ABC):
  def __init__(self, initial_state : StateT) -> None:
    self.initial_state = initial_state

  @abstractmethod
  def TO_MOVE(self, state : StateT) -> PlayerT:
    raise NotImplementedError( "This method should be overridden by subclasses" )

  @abstractmethod
  def ACTIONS(self, state : StateT) -> Iterable[MoveT]:
    raise NotImplementedError( "This method should be overridden by subclasses" )

  @abstractmethod
  def RESULTS(self, state : StateT, action : MoveT) -> Iterable[StateT]:
    raise NotImplementedError( "This method should be overridden by subclasses" )

  @abstractmethod
  def IS_TERMINAL(self, state : StateT) -> bool:
    raise NotImplementedError( "This method should be overridden by subclasses" )

  @abstractmethod
  def UTILITY(self, state : StateT, player : PlayerT) -> float:
    raise NotImplementedError( "This method should be overridden by subclasses" )

  def EVAL(self, state : StateT, player : PlayerT) -> float:
    return self.UTILITY(state, player)

  def IS_CUTOFF(self, state : StateT, depth : int) -> bool:
    assert depth >= 0
    return self.IS_TERMINAL(state)