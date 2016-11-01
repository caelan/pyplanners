from misc.utils import *
from states import Substate
from effects import ValueEffect

# https://docs.python.org/2/library/functions.html#staticmethod

class Subplanner(object):
  def applicable(self, start_vertex, goal_connector, rg):
    raise NotImplementedError('Subplanner must implement applicable(self, start_vertex, goal_connector, rg)')
  def generator(self, start_vertex, goal_connector, rg):
    raise NotImplementedError('Subplanner must implement generator(self, start_vertex, goal_connector, rg)')
  def __contains__(self, start_vertex, goal_connector, rg):
    return self.applicable(start_vertex, goal_connector, rg)
  def __call__(self, start_vertex, goal_connector, rg):
    return SubplannerGenerator(start_vertex, goal_connector, rg, self.generator)

class SubplannerGenerator(GeneratorWrapper):
  def __init__(self, start_vertex, goal_connector, rg, generator):
    self.start_vertex = start_vertex
    self.goal_connector = goal_connector
    self.generator = generator(start_vertex, goal_connector, rg)
    self.exhausted = False
    self.generations = 0
    self.queued = False
    self.locked = False
    #self() # To immediately call the generator
  def __call__(self):
    if self.locked: return
    self.locked = True
    try:
      next(self.generator)
      self.generations += 1
    except StopIteration:
      self.exhausted = True
    self.locked = False
  def __str__(self):
    return str(self.__class__.__name__) + '(' + str(self.goal_connector) + ')'
  __repr__ = __str__

"""
class Subplanner(object):
  @staticmethod
  def __contains__(start_vertex, goal_connector, rg):
    raise NotImplementedError('GeneratorSubplanner must implement __contains__(self)')
  @classmethod
  def __call__(cls, *args):
    return SafeGeneratorWrapper(cls.generator(*args))
  @staticmethod
  def generator(start_vertex, goal_connector, rg):
    raise NotImplementedError('GeneratorSubplanner must implement generator(self)')
"""
