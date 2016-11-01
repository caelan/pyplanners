from random import shuffle, choice
from itertools import cycle, islice, permutations, chain, product, count
from collections import Iterable
from numerical import INF
import operator

def irange(start, stop=None, step=1): #np.arange
  if stop is None:
    stop = start
    start = 0
  while start < stop:
    yield start
    start += step

def erange(start, stop=None, step=1):
  if stop is None:
    stop = start
    start = 0
  while start < stop:
    yield start
    start += step
  yield stop

def some(function, iterable):
  return any(function(item) for item in iterable)

def every(function, iterable):
  return all(function(item) for item in iterable)

def first(function, iterable):
  for item in iterable:
    if function(item):
      return item
  return None

def argmax(function, sequence):
  values = list(sequence)
  scores = [function(x) for x in values]
  return values[scores.index(max(scores))]

def argmin(function, sequence):
  values = list(sequence)
  scores = [function(x) for x in values]
  return values[scores.index(min(scores))]

def pop_max(function, array):
  scores = [function(x) for x in array]
  return array.pop(scores.index(max(scores)))

def pop_min(function, array):
  scores = [function(x) for x in array]
  return array.pop(scores.index(min(scores)))

def safe_function(function, sequence, default):
  if len(sequence) == 0: return default
  return function(sequence)

def safe_choice(sequence, default=None):
  return safe_function(choice, sequence, default)

def safe_max(sequence, default=-INF):
  return safe_function(max, sequence, default)

def safe_min(sequence, default=INF):
  return safe_function(min, sequence, default)

def safe_maxmin(iterable_of_iterables):
  return safe_max([safe_min(iterables) for iterables in iterable_of_iterables])

def safe_minmax(iterable_of_iterables):
  return safe_min([safe_max(iterables) for iterables in iterable_of_iterables])

def safe_index(sequence, value, default=-1):
  if value not in sequence: return default
  return sequence.index(value)

def pairs(lst):
  return zip(lst[:-1], lst[1:])

def randomize(sequence):
  shuffle(sequence)
  return sequence

def random_sequence(sequence):
  indices = range(len(sequence))
  shuffle(indices)
  for i in indices:
    yield sequence[i]

def reverse(iterable):
  return reversed(list(iterable))

def flatten(iterable_of_iterables):
  return (item for iterables in iterable_of_iterables for item in iterables)

def squash(nested_iterables):
  result = []
  for item in nested_iterables:
    if isinstance(item, Iterable):
      result += squash(item)
    else:
      result.append(item)
  return result

def round_robin(*iterables):
  pending = len(iterables)
  nexts = cycle(iter(it).next for it in iterables)
  while pending:
    try:
      for next in nexts:
        yield next()
    except StopIteration:
      pending -= 1
      nexts = cycle(islice(nexts, pending))

def merge_unique(iterables, sort=False):
  merged = list(set(reduce(operator.add, iterables)))
  if sort: return sorted(merged)
  return merged

def merge_dicts(*args):
  result = {}
  for d in args:
    result.update(d)
  return result
  # return dict(reduce(operator.add, [d.items() for d in args]))

def in_add(x, s):
  if x not in s:
    s.add(x)
    return False
  return True
