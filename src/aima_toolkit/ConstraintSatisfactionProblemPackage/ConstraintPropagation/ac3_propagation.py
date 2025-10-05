from ..constraint_satisfaction_problem import ConstraintSatisfactionProblem, Constraint
from ...SearchProblemPackage import PriorityQueue
from ...SearchProblemPackage.queue import FIFOQueue

def ac3(csp : ConstraintSatisfactionProblem):
  constraints = PriorityQueue[Constraint](lambda c: len(c.variables))

  for constraint_list in csp.var_to_constraints.values( ):
    for constraint in constraint_list:
      constraints.push(constraint)

  