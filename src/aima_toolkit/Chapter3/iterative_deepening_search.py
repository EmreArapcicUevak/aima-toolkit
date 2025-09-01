from itertools import count
from Chapter3.SearchProblemPackage.search_problem import *
from Chapter3.depth_limited_search import depth_limited_search

def iterative_deepening_search(problem : Search_Problem):
  for depth in count(start=0):
    result = depth_limited_search(problem, depth)
    if result != SearchStatus.CUTOFF:
      return result