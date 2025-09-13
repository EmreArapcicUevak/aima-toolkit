from collections.abc import Callable

from src.aima_toolkit.Problems.find_the_ip_phone import Switch, FindTheIPPhone, topology, learned_mac_address
from src.aima_toolkit.SearchProblemPackage.SearchAlgorithms.OnlineSearch.SearchAgents import OnlineDFSAgent
from src.aima_toolkit.SearchProblemPackage.SearchAlgorithms.OnlineSearch import OnlineSearchAction
from pprint import pprint


def check_result(problem, wanted_switch, action_value_heuristic : Callable[[Switch, str], float]= lambda s,a: 0.0):
  dfs_agent = OnlineDFSAgent( problem, action_value_heuristic )
  agent_search = dfs_agent.search( )

  action = next( agent_search )
  current_switch = problem.initial_state
  while action != OnlineSearchAction.STOP:
    current_switch = topology[ action ]
    action = agent_search.send( current_switch )

  assert action == OnlineSearchAction.STOP
  assert wanted_switch == current_switch

def test_SE1():
  check_result(FindTheIPPhone(topology["127.0.0.1"], "11-11-11-11-11-05"), topology["127.0.0.6"])
  check_result(FindTheIPPhone(topology["127.0.0.1"], "11-11-11-11-11-04"), topology["127.0.0.5"])
  check_result(FindTheIPPhone(topology["127.0.0.1"], "11-11-11-11-11-03"), topology["127.0.0.3"])
  check_result(FindTheIPPhone(topology["127.0.0.1"], "11-11-11-11-11-02"), topology["127.0.0.2"])
  check_result(FindTheIPPhone(topology["127.0.0.1"], "11-11-11-11-11-01"), topology["127.0.0.2"])
  check_result(FindTheIPPhone(topology["127.0.0.1"], "11-11-11-11-11-00"), topology["127.0.0.1"])

def test_SE2():
  check_result(FindTheIPPhone(topology["127.0.0.2"], "11-11-11-11-11-05"), topology["127.0.0.6"])
  check_result(FindTheIPPhone(topology["127.0.0.2"], "11-11-11-11-11-04"), topology["127.0.0.5"])
  check_result(FindTheIPPhone(topology["127.0.0.2"], "11-11-11-11-11-03"), topology["127.0.0.3"])
  check_result(FindTheIPPhone(topology["127.0.0.2"], "11-11-11-11-11-02"), topology["127.0.0.2"])
  check_result(FindTheIPPhone(topology["127.0.0.2"], "11-11-11-11-11-01"), topology["127.0.0.2"])
  check_result(FindTheIPPhone(topology["127.0.0.2"], "11-11-11-11-11-00"), topology["127.0.0.1"])

def test_SE3():
  check_result(FindTheIPPhone(topology["127.0.0.3"], "11-11-11-11-11-05"), topology["127.0.0.6"])
  check_result(FindTheIPPhone(topology["127.0.0.3"], "11-11-11-11-11-04"), topology["127.0.0.5"])
  check_result(FindTheIPPhone(topology["127.0.0.3"], "11-11-11-11-11-03"), topology["127.0.0.3"])
  check_result(FindTheIPPhone(topology["127.0.0.3"], "11-11-11-11-11-02"), topology["127.0.0.2"])
  check_result(FindTheIPPhone(topology["127.0.0.3"], "11-11-11-11-11-01"), topology["127.0.0.2"])
  check_result(FindTheIPPhone(topology["127.0.0.3"], "11-11-11-11-11-00"), topology["127.0.0.1"])

def test_SE4():
  check_result(FindTheIPPhone(topology["127.0.0.4"], "11-11-11-11-11-05"), topology["127.0.0.6"])
  check_result(FindTheIPPhone(topology["127.0.0.4"], "11-11-11-11-11-04"), topology["127.0.0.5"])
  check_result(FindTheIPPhone(topology["127.0.0.4"], "11-11-11-11-11-03"), topology["127.0.0.3"])
  check_result(FindTheIPPhone(topology["127.0.0.4"], "11-11-11-11-11-02"), topology["127.0.0.2"])
  check_result(FindTheIPPhone(topology["127.0.0.4"], "11-11-11-11-11-01"), topology["127.0.0.2"])
  check_result(FindTheIPPhone(topology["127.0.0.4"], "11-11-11-11-11-00"), topology["127.0.0.1"])

def test_SE5():
  check_result(FindTheIPPhone(topology["127.0.0.5"], "11-11-11-11-11-05"), topology["127.0.0.6"])
  check_result(FindTheIPPhone(topology["127.0.0.5"], "11-11-11-11-11-04"), topology["127.0.0.5"])
  check_result(FindTheIPPhone(topology["127.0.0.5"], "11-11-11-11-11-03"), topology["127.0.0.3"])
  check_result(FindTheIPPhone(topology["127.0.0.5"], "11-11-11-11-11-02"), topology["127.0.0.2"])
  check_result(FindTheIPPhone(topology["127.0.0.5"], "11-11-11-11-11-01"), topology["127.0.0.2"])
  check_result(FindTheIPPhone(topology["127.0.0.5"], "11-11-11-11-11-00"), topology["127.0.0.1"])

def test_SE6():
  check_result(FindTheIPPhone(topology["127.0.0.6"], "11-11-11-11-11-05"), topology["127.0.0.6"])
  check_result(FindTheIPPhone(topology["127.0.0.6"], "11-11-11-11-11-04"), topology["127.0.0.5"])
  check_result(FindTheIPPhone(topology["127.0.0.6"], "11-11-11-11-11-03"), topology["127.0.0.3"])
  check_result(FindTheIPPhone(topology["127.0.0.6"], "11-11-11-11-11-02"), topology["127.0.0.2"])
  check_result(FindTheIPPhone(topology["127.0.0.6"], "11-11-11-11-11-01"), topology["127.0.0.2"])
  check_result(FindTheIPPhone(topology["127.0.0.6"], "11-11-11-11-11-00"), topology["127.0.0.1"])

def test_SE1_with_heuristic():
  check_result(
    FindTheIPPhone(
      topology["127.0.0.1"],
      "11-11-11-11-11-05"
    ),
    topology["127.0.0.6"],
    FindTheIPPhone.get_action_value_heuristic("11-11-11-11-11-05")
  )

def test_non_existent_phone():
  problem = FindTheIPPhone(topology["127.0.0.1"], "11-11-11-11-11-0A")
  dfs_agent = OnlineDFSAgent( problem )
  agent_search = dfs_agent.search( )

  action = next( agent_search )
  current_switch = problem.initial_state
  while action != OnlineSearchAction.STOP:
    current_switch = topology[ action ]
    action = agent_search.send( current_switch )

  assert action == OnlineSearchAction.STOP
  assert problem.IS_GOAL( current_switch ) == False