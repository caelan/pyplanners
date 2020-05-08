from state_expanders import *

# TODO
# - store previous search states to avoid recomputing same structure (see IDA*)

def increment(parameters):
  return {p: v + 1 for p, v in parameters.items()}

def iterative_deepening(search, initial_parameters, iterate_parameters):
  parameters = initial_parameters
  while True:
    plan, search_data = search(**parameters)
    if plan is not None:
      return plan, search_data
    parameters = iterate_parameters(parameters)
  return None, None

