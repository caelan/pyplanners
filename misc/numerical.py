from math import ceil, pi, cos, sin, atan2, sqrt, exp
from random import random, randint, gauss, uniform
from time import time, sleep
from bisect import bisect
from collections import defaultdict
#py_any, py_all = any, all
#from numpy import *
#np_any, np_all = any, all
#any, all = py_any, py_all
import numpy as np
import sys

PI = pi
INF = float('inf')
np.set_printoptions(suppress=True) # precision=5,

def within(v1, v2, eps=1e-6):
  return abs(v1 - v2) < eps

def clip(value, min_value=-INF, max_value=INF):
  return max(min(value, max_value), min_value)

def positive_angle(angle): # [0, 2*PI)
  return angle%(2*PI)

def symmetric_angle(angle): # [-PI, PI)
  return (angle + PI)%(2*PI) - PI

def sample_categorical(categories):
  names = categories.keys()
  cutoffs = np.cumsum([categories[name] for name in names])/sum(categories.values())
  return names[bisect(cutoffs, random())]

#def sample_categorical(categories):
#  names = categories.keys()
#  return np.random.multinomial(1, np.array(categories.values())/sum(categories.values()), size=1)

def sample_boltzmann(categories):
  return sample_categorical({k: exp(v) for k, v in categories.iteritems()})

def uniform_categorical(categories):
  return {c: 1./len(categories) for c in categories}

def merge_categorical(one, two, p=.5):
  merged = defaultdict(float)
  for c in one:
    merged[c] += p*one[c]
  for c in two:
    merged[c] = (1-p)*two[c]
  return merged

def joint_categorical(one, two):
  return {(x1, x2): p1*p2 for x1, p1 in one.iteritems() for x2, p2 in two.iteritems()}

def normalize_categorical(dist):
  return {c: p/sum(dist.values()) for c, p in dist.iteritems()}

def positive_hash(x):
  return hash(x)%((sys.maxsize+1)*2)