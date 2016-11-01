
class MultiSortKey(object): # TODO - bizarre error where if you do key_fns = [] it takes an argument anyways...
  def __init__(self):
    self.key_fns = []
  def true_key_fn(self, f):
    self.key_fns.append(lambda x: not f(x))
  def false_key_fn(self, f):
    self.key_fns.append(f)
  def max_key_fn(self, f):
    self.key_fns.append(lambda x: -f(x))
  def min_key_fn(self, f):
    self.key_fns.append(f)
  def __call__(self, x):
    return tuple(key_fn(x) for key_fn in self.key_fns)

class DeterminisiticCache(object):
  def __init__(self, fn=None):
    if fn is not None: self.fn = fn
    self.reset()
  def key(self, *args, **kwargs):
    return (tuple(args), frozenset(kwargs.items()))
  def fn(self, *args, **kwargs):
    raise NotImplementedError()
  def contains(self, *args, **kwargs):
    return self.key(*args, **kwargs) in self.cache
  def __call__(self, *args, **kwargs):
    #self.total_calls += 1
    #t0 = time()
    key = self.key(*args, **kwargs)
    if key not in self.cache:
      self.cache[key] = self.fn(*args, **kwargs)
    #self.total_time += time() - t0
    return self.cache[key]
  def reset(self):
    self.cache = {}
    self.total_calls = 0
    self.total_time = 0
  def statistics(self):
    time_per_call = self.total_time/self.total_calls if self.total_calls > 0 else None
    return '{self}\n' \
           'Total Calls: {self.total_calls}\n' \
           'Total Time: {self.total_time}\n' \
           'Time/Call: {}\n'.format(time_per_call, self = self)
  def __str__(self):
    return self.__class__.__name__
  __repr__ = __str__

class DeterministicFn(object):
  def __init__(self, fn=None):
    if fn is not None: self.fn = fn
    self.reset()
  def __call__(self, *args, **kwargs):
    #self.total_calls += 1
    #t1 = time()
    value = self.fn(*args, **kwargs)
    #self.total_time += time() - t1
    return value
  def reset(self):
    self.total_calls = 0
    self.total_time = 0
  def statistics(self):
    time_per_call = self.total_time/self.total_calls if self.total_calls > 0 else None
    return '{self}\n' \
           'Total Calls: {self.total_calls}\n' \
           'Total Time: {self.total_time}\n' \
           'Time/Call: {}\n'.format(time_per_call, self = self)
  def __str__(self):
    return self.__class__.__name__ + '(' + self.fn.__name__ + ')'
  __repr__ = __str__
