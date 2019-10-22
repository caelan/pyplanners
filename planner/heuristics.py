from .helpful_actions import *

def h_0(rg): return 0
def h_naive(rg): return sum(1 for condition in rg.goal if rg.start.substate not in condition)
def h_blind(rg): return min(operator.cost for operator in applicable_operators(rg))

###########################################################################

def cost(rg, op=max, unit=False):
  rg.costs(op, unit=unit)
  return rg.goal.cost

def h_add(rg): return cost(rg, op=sum)
def h_max(rg): return cost(rg, op=max)
def h_add_unit(rg): return cost(rg, op=sum, unit=True)
def h_max_unit(rg): return cost(rg, op=max, unit=True)

###########################################################################

def ff(rg, op=max, unit=False):
  rg.costs(op=op, unit=unit)
  rg.linearize_plan()
  return sum(edge.value.cost if not unit else 1 for edge in flatten(rg.relaxed_plan_edges))

def h_ff_max(rg): return ff(rg, op=max)
def h_ff_add(rg): return ff(rg, op=sum)
