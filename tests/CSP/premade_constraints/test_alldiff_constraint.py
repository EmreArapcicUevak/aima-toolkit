from src.aima_toolkit.ConstraintSatisfactionProblemPackage import ConstraintSatisfactionProblem, Constraint
from src.aima_toolkit.ConstraintSatisfactionProblemPackage.PremadeConstraints import alldiff_constraint, \
  alldiff_constraint_propagation


def test_alldiff_constraint():
  integers_from_zero_to_five = set(range(6))
  test_csp = ConstraintSatisfactionProblem(variables=['X1', 'X2', 'X3', 'X4'], domains={'X1': integers_from_zero_to_five, 'X2': integers_from_zero_to_five, 'X3': integers_from_zero_to_five, 'X4': integers_from_zero_to_five})
  assert alldiff_constraint_propagation(test_csp, {'X1', 'X2', 'X3', 'X4'}) == True

  test_csp_2 = ConstraintSatisfactionProblem(variables=['X1', 'X2', 'X3', 'X4'], domains={'X1': {1}, 'X2': {1,2}, 'X3': {1,2,3,4}, 'X4': {2,4}})
  assert alldiff_constraint_propagation(test_csp_2, {'X1', 'X2', 'X3', 'X4'}) == True

  test_csp_3 = ConstraintSatisfactionProblem(variables=['X1', 'X2', 'X3', 'X4'], domains={'X1': {1}, 'X2': {1}, 'X3': {1,2,3,4}, 'X4': {2,4}})
  assert alldiff_constraint_propagation(test_csp_3, {'X1', 'X2', 'X3', 'X4'}) == False

  test_csp_4 = ConstraintSatisfactionProblem(variables=['X1', 'X2', 'X3', 'X4'], domains={'X1': {1}, 'X2': {}, 'X3': {1,2,3,4}, 'X4': {2,4}})
  assert alldiff_constraint_propagation(test_csp_4, {'X1', 'X2', 'X3', 'X4'}) == False
