from heapq import heappush, heappop, heapify
#from Queue import PriorityQueue
from collections import namedtuple, defaultdict, deque
from itertools import count

# TODO - multi-priority queues

class Stack(object):
  def __init__(self, array=[]):
    self.stack = deque(array)
  def peek(self):
    return self.stack[0]
  def push(self, _, element):
    self.stack.appendleft(element)
  def pop(self):
    return self.stack.popleft()
  def empty(self):
    return len(self.stack) == 0

class Queue(object):
  def __init__(self, array=[]):
    self.queue = deque(array)
  def peek(self):
    return self.queue[0]
  def push(self, _, element):
    self.queue.append(element)
  def pop(self):
    return self.queue.popleft()
  def empty(self):
    return len(self.queue) == 0

class StableQueue(object):
  sign = 0
  Node = namedtuple('Node', ['priority', 'index', 'element'])
  def __init__(self):
    self.counter = count(0)
  def new_node(self, priority, element):
    return self.Node(priority, self.sign*next(self.counter), element)

class PriorityQueue(StableQueue):
  def __init__(self, array=[]):
    super(PriorityQueue, self).__init__()
    self.queue = map(lambda x: self.new_node(*x), array)
    heapify(self.queue)
  def peek(self):
    return self.queue[0].element
  def push(self, priority, element):
    heappush(self.queue, self.new_node(priority, element))
  def pop(self):
    return heappop(self.queue).element
  def empty(self):
    return len(self.queue) == 0

class FIFOPriorityQueue(PriorityQueue): sign = 1
class FILOPriorityQueue(PriorityQueue): sign = -1

class ClassicPriorityQueue(StableQueue):
  def __init__(self, array=[]):
    super(ClassicPriorityQueue, self).__init__()
    self.queue = []
    self.priorities = {}
    self.processed = set()
    for x in array: self.decrease_key(*x)
  def decrease_key(self, priority, element):
    if element not in self.priorities or priority < self.priorities[element]:
      self.priorities[element] = priority
      heappush(self.queue, self.new_node(priority, element)) # TODO - retain old priority?
  def clean(self):
    while len(self.queue) > 0 and self.queue[0] in self.processed: # NOTE - gets rid of redundant queue nodes
      heappop(self.queue)
  def pop(self):
    self.clean()
    element = heappop(self.queue).element
    self.processed.add(element)
    return element
  def empty(self):
    self.clean()
    return len(self.queue) == 0

class FIFOClassicPriorityQueue(ClassicPriorityQueue): sign = 1
class FILOClassicPriorityQueue(ClassicPriorityQueue): sign = -1
