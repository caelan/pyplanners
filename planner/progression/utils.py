from random import random, randint, choice

def pop_random(queue):
  queue.rotate(randint(0, len(queue)-1))
  return queue.popleft()

def sample_target(sample, goal_sample=None, goal_probability=.1):
  if goal_sample is not None and random() < goal_probability:
    return goal_sample()
  return sample()

def pop_min(queue, distance):
  minimum, indices = None, []
  for i, v in enumerate(queue):
    score = distance(v)
    if minimum is None or score < minimum:
      minimum, indices = score, [i]
    elif score == minimum:
      indices.append(i)
  queue.rotate(choice(indices))
  return queue.popleft()

def pop_rrt(distance, sample, goal_sample=None, goal_probability=.1):
  return lambda queue: pop_min(queue,
    lambda sv: distance(sv.state, sample_target(sample, goal_sample=goal_sample, goal_probability=goal_probability)))
