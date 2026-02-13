from abc import abstractmethod, ABC
from collections.abc import Iterable
from typing import Generic, TypeVar
import math

class Game[StateT, MoveT, PlayerT](ABC):
  """
    Abstract base class for turn-based adversarial games.

    This class defines the interface required by adversarial search
    algorithms such as minimax, alpha-beta pruning, and expectiminimax.

    A game is defined by:
      - a set of states
      - a set of legal actions
      - a transition model
      - a terminal test
      - a utility function

    Type Parameters
    ----------------
    StateT
        Type representing a game state.
    MoveT
        Type representing an action or move.
    PlayerT
        Type representing a player identifier.
  """

  def __init__(self, *, sum : float = math.inf) -> None:
    self.sum = sum

  @abstractmethod
  def TO_MOVE(self, state : StateT) -> PlayerT:
    """
    Return the player whose turn it is in the given state.

    Parameters
    ----------
    state : StateT
        Current game state.

    Returns
    -------
    PlayerT
        The player to move.
    """
    raise NotImplementedError( "This method should be overridden by subclasses" )

  @abstractmethod
  def ACTIONS(self, state : StateT) -> Iterable[MoveT]:
    """
    Return all legal actions available in the given state.

    Parameters
    ----------
    state : StateT
        Current game state.

    Returns
    -------
    Iterable[MoveT]
        An iterable of legal moves.
    """
    raise NotImplementedError( "This method should be overridden by subclasses" )

  def QUIESCENCE_ACTIONS(self, state : StateT) -> Iterable[MoveT]:
    """
    Return all legal actions available in the given state that should be
    considered during quiescence search.

    Quiescence actions are typically a subset of all legal actions, such as
    captures, checks, or other "tactical" moves that prevent evaluating
    unstable positions too early.

    Parameters
    ----------
    state : StateT
        Current game state.

    Returns
    -------
    Iterable[MoveT]
        An iterable of legal quiescence moves.
    """
    return []


  @abstractmethod
  def RESULTS(self, state : StateT, action : MoveT) -> StateT:
    """
    Return the state that results from applying an action
    in the given state.

    Parameters
    ----------
    state : StateT
        Current game state.
    action : MoveT
        Action to apply.

    Returns
    -------
    StateT
        The resulting game state.
    """
    raise NotImplementedError( "This method should be overridden by subclasses" )

  @abstractmethod
  def IS_TERMINAL(self, state : StateT) -> bool:
    """
    Determine whether the given state is terminal.

    A terminal state is one in which the game has ended
    (win, loss, draw, etc.).

    Parameters
    ----------
    state : StateT
        Game state to test.

    Returns
    -------
    bool
        True if the state is terminal, False otherwise.
    """
    raise NotImplementedError( "This method should be overridden by subclasses" )

  @abstractmethod
  def UTILITY(self, state : StateT) -> dict[PlayerT, float]:
    """
    Return the utility value of a terminal state
    from the perspective of the given player.

    Higher values indicate better outcomes for the player.

    Parameters
    ----------
    state : StateT
        Terminal game state.
    player : PlayerT
        Player for whom the utility is evaluated.

    Returns
    -------
    float
        Utility value of the state.
    """
    raise NotImplementedError( "This method should be overridden by subclasses" )

  def EVAL(self, state : StateT) -> dict[PlayerT, float]:
    """
    Evaluate a non-terminal state.

    By default, this calls :meth:`utility`, but subclasses may
    override this method to provide heuristic evaluations
    for cutoff search.

    Parameters
    ----------
    state : StateT
        Game state to evaluate.
    player : PlayerT
        Player for whom the evaluation is performed.

    Returns
    -------
    float
        Evaluation score.
    """
    return self.UTILITY(state)

  def IS_CUTOFF(self, state : StateT, depth : int) -> bool:
    """
    Determine whether search should be cut off at the given state.

    This method is used in depth-limited or heuristic search
    (e.g., alpha-beta with cutoff and evaluation).

    By default, the search is cut off only at terminal states.

    Parameters
    ----------
    state : StateT
        Current game state.
    depth : int
        Remaining search depth (must be non-negative).

    Returns
    -------
    bool
        True if search should be cut off, False otherwise.

    Raises
    ------
    ValueError
        If ``depth`` is negative.
    """
    assert depth >= 0
    return self.IS_TERMINAL(state)