from abc import ABC, abstractmethod
from typing import Any, Callable
from collections import defaultdict
import copy

# Type aliases
Variable = str
VariableAssignment = dict[Variable, Any]
ConstraintFunction = Callable[[VariableAssignment], bool]

class Constraint:
    def __init__(self, variables: list[Variable], constraint_func: ConstraintFunction):
        self.variables = list(variables)
        self.constraint_func = constraint_func

    def satisfied(self, assignment: VariableAssignment) -> bool:
        """
        Return True if the current partial assignment does NOT violate the constraint.
        If all variables of this constraint are present, evaluate the function.
        If not all present, return True (not violated yet).
        """
        if all(v in assignment for v in self.variables):
            sub = {v: assignment[v] for v in self.variables}
            return bool(self.constraint_func(sub))
        # partial assignment -> cannot claim violation
        return True

class ConstraintSatisfactionProblem:
    def __init__(self, variables: list[Variable], domains: dict[Variable, list[Any]]):
        self.variables: list[Variable] = list(variables)
        # deep copy so callers can't accidentally mutate internal domains
        self.domains: dict[Variable, list[Any]] = copy.deepcopy(domains)
        self.constraints: dict[Variable, list[Constraint]] = defaultdict(list)

        # sanity checks
        for var in self.domains.keys():
            assert var in self.variables, f"Domain provided for unknown variable {var}"

        assert len(self.variables) == len(self.domains.keys()), (
            f"Number of variables {len(self.variables)} does not match number of domains {len(self.domains.keys())}"
        )

        # ensure every variable has an entry in constraints dict
        for v in self.variables:
            self.constraints.setdefault(v, [])

    def add_variable(self, variable: Variable, domain: list[Any]):
        assert variable not in self.variables, f"Variable {variable} is already present"
        self.variables.append(variable)
        # copy domain to avoid aliasing problems
        self.domains[variable] = list(domain)
        self.constraints.setdefault(variable, [])

    def add_constraint(self, constraint: Constraint):
        for var in constraint.variables:
            assert var in self.variables, f"Variable {var} is not a valid variable"
            self.constraints[var].append(constraint)

    def is_consistent(self, var: Variable, assignment: VariableAssignment) -> bool:
        """
        Check all constraints that mention `var`. For partial assignments,
        constraint.satisfied returns True unless the constraint is violated.
        """
        assert var in self.variables, f"Variable {var} is not a valid variable"
        assert all(value in self.domains[variable] for variable, value in assignment.items()), f"Variable {var} doesn't have a valid assignment"
        return all(c.satisfied(assignment) for c in self.constraints[var])

__all__ = ["Variable", "VariableAssignment", "ConstraintSatisfactionProblem", "Constraint", "ConstraintSatisfactionProblem"]