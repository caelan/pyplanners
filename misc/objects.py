from collections import deque, namedtuple, defaultdict, Counter as CountDict, Mapping, Iterable, Iterator, Set
from heapq import heappush, heappop, heapify
import numpy as np
from string import join
import types

# Old style classes don't inherit from object => type(old) != old.__class__
# New style classes do inherit from object => type(new) == new.__class__
# http://stackoverflow.com/questions/54867/what-is-the-difference-between-old-style-and-new-style-classes-in-python
# https://docs.python.org/2/library/stdtypes.html#object.__dict__
# https://docs.python.org/2/library/collections.html#collections.defaultdict

Object = object

def get_class(obj):
  return obj.__class__

def class_name(obj):
  return get_class(obj).__name__

def str_object(obj):
  if type(obj) in (list, np.ndarray):
    return '[%s]' % ', '.join(str_object(item) for item in obj)
  if type(obj) == tuple:
    return '(%s)' % ', '.join(str_object(item) for item in obj)
  if type(obj) == dict:
    return '{%s}' % ', '.join(str_object(item) + ': ' +  str_object(obj[item]) \
        for item in sorted(obj.keys(), key=lambda k: str_object(k)))
  if type(obj) in (set, frozenset):
    return '{%s}' % ', '.join(sorted(str_object(item) for item in obj))
  if type(obj) in (float, np.float64):
    obj = round(obj, 3)
    if obj == 0: obj = 0 # NOTE - catches -0.0 bug
    return '%.3f'%obj
  if isinstance(obj, types.FunctionType):
    return obj.__name__
  return str(obj)

def str_line(*args):
  return join([str_object(item) for item in args])

def str_args(args):
  return '(%s)' % ', '.join([str_object(item) + '=' +  str_object(args[item]) \
      for item in sorted(args.keys(), key=lambda k: str_object(k))])

def namedtuple_with_defaults(typename, field_names, default_values=[]):
  T = namedtuple(typename, field_names)
  T.__new__.__defaults__ = (None,) * len(T._fields)
  if isinstance(default_values, Mapping):
    prototype = T(**default_values)
  else:
    prototype = T(*default_values)
  T.__new__.__defaults__ = tuple(prototype)
  return T

def enum(*sequential, **named):
  enums = dict(zip(sequential, range(len(sequential))), **named)
  enums['names'] = sorted(enums.keys(), key=lambda k: enums[k])
  return type('Enum', (), enums)

class HashObject(object): # TODO - related to namedtuple
  def __init__(self):
    self.__dict__['__hash_dict'] = {} # collections.OrderedDict([items])
  def get(self, name):
    return self.__dict__['__hash_dict'][name]
  def __getattr__(self, name):
    return self.get(name)
  def set(self, name, value):
    self.__dict__['__hash_dict'][name] = value
  def __setattr__(self, name, value):
    self.set(name, value)
  def __eq__(self, other):
    if type(self) != type(other): return False
    return self.__dict__['__hash_dict'] == other.__dict__['__hash_dict']
  def __ne__(self, other):
    return not self == other
  def __hash__(self):
    if '__hash' not in self.__dict__:
      self.__dict__['__hash'] = hash(frozenset(self.__dict__['__hash_dict'].items()))
    return self.__dict__['__hash']

class HashDict(HashObject, Mapping):
  def __init__(self, d={}):
    HashObject.__init__(self)
    self.__dict__['__hash_dict'] = d
  def __getitem__(self, key):
    return self.get(key)
  def __iter__(self):
    return (key for key in self.__dict__['__hash_dict'])
  def __len__(self):
    return len(self.__dict__['__hash_dict'])
  def __str__(self):
    return str(self.__dict__['__hash_dict'])
  __repr__ = __str__

class DictPrintObject(HashObject):
  def __str__(self):
    return class_name(self) + str_args(self.__dict__['__hash_dict'])
  __repr__ = __str__

class ValuesPrintObject(HashObject):
  def __str__(self):
    return class_name(self) + str_object(tuple(self.__dict__['__hash_dict'].values()))
  __repr__ = __str__

class SinglePrintObject(HashObject):
  def __str__(self):
    if len(self.__dict__['__hash_dict']) == 0:
      return class_name(self)
    return class_name(self) + str_object(self.__dict__['__hash_dict'].values()[0])
  __repr__ = __str__

class FrozenDict(Mapping):
  def __init__(self, *args, **kwargs):
    self._d = dict(*args, **kwargs)
    self._hash = None
  def __iter__(self):
    return iter(self._d)
  def __len__(self):
    return len(self._d)
  def __getitem__(self, key):
    return self._d[key]
  def __hash__(self):
    if self._hash is None:
      self._hash = 0
      for pair in self.iteritems(): self._hash ^= hash(pair)
    return self._hash

class Function(namedtuple('Function', ['fn', 'args'])):
  __slots__ = ()
  def __call__(self, *args):
    return self.fn(*(list(args) + [arg() if isinstance(arg, self.__class__) else arg for arg in self.args]))
  def __repr__(self):
    return self.fn.__name__ + str_object(self.args)

def Fn(fn, *args):
  return Function(fn, args)