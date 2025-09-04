from typing import Self

class Node[S,A]:
  def __init__(self, state : S, parent : Self | None = None, path_cost : float | int = 0, action : A | None = None):
    self.state = state
    self.parent = parent
    self.path_cost = path_cost
    self.depth = 0 if parent is None else parent.depth + 1
    self.action = action

  def __str__(self) -> str:
    return self.__repr__()

  def __eq__(self, value: object) -> bool:
    return self.state == value.state if isinstance(value, Node) else False

  def __repr__(self) -> str:
    return f"Node({self.state}, cost={self.path_cost})"

  def get_path(self) -> list[S]:
    path = []
    current = self
    while current:
      path.append(current.state)
      current = current.parent

    return path[::-1]
  
  def get_actions(self) -> list[A]:
    actions = []
    current = self
    while current:
      if current.action is not None:
        actions.append(current.action)
      current = current.parent

    return actions[::-1]