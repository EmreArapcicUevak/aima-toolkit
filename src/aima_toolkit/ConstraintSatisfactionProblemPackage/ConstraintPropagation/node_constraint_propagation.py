from ..constraint_satisfaction_problem import ConstraintSatisfactionProblem, Constraint
from ...SearchProblemPackage.queue import FIFOQueue


def node_constraint_propagation(csp: ConstraintSatisfactionProblem):
  constraints = FIFOQueue()

  for constraint in csp.constraints:
    if len(constraint.variables) == 1:
      constraints.push(constraint)

  while len(constraints) > 0:
    constraint = constraints.pop()
    variable = constraint.variables[0]
    variable_domain = csp.domains[variable]

    inconsistent_values = set()
    for value in variable_domain:
      if not constraint.satisfied({variable : value}):
        inconsistent_values.add(value)

    csp.domains[variable] = variable_domain.difference(inconsistent_values)
