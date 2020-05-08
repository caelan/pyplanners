# TODO -
# Iteratively limit search space as new plans are found (either by cost or length)
# Termination conditions - iterations, time, or found the best plan (complete exploration of the space)
# Admissible heuristic can help further rule out states by pruning those far from the goal
# Slightly randomized search (or using weighted A*) will ensure not obtaining the same results
# Bugsey inspiration

def contracting_search(search, initial_parameters, iterate_parameters):
  raise NotImplementedError()
