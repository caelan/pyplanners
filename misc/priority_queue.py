from heapq import heappush, heappop, heapify
#from Queue import PriorityQueue
from collections import namedtuple, deque
from itertools import count

# TODO - multi-priority queues

class HeapElement(object):
  def __init__(self, key, value):
    self.key = key
    self.value = value
  def __lt__(self, other):
    return self.key < other.key
  def __iter__(self):
    return iter([self.key, self.value])
  def __repr__(self):
    return '{}({}, {})'.format(self.__class__.__name__, self.key, self.value)

##################################################

class Queue(object): # FIFO
  def __init__(self, array=[]):
    self.queue = deque(array)
  def peek(self):
    return self.queue[0]
  def push(self, _, element):
    self.queue.append(element)
  def pop(self):
    return self.queue.popleft()
  def empty(self):
    return len(self) == 0
  def __len__(self):
    return len(self.queue)
  def __repr__(self):
    return '{}{}'.format(self.__class__.__name__, list(self.queue))

class Stack(Queue): # LIFO
  @property
  def stack(self):
    return self.queue
  def push(self, _, element):
    self.stack.appendleft(element)

##################################################

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
    self.queue = list(map(lambda x: self.new_node(*x), array))
    heapify(self.queue)
  def peek(self):
    return self.queue[0].element
  def push(self, priority, element):
    heappush(self.queue, self.new_node(priority, element))
  def pop(self):
    return heappop(self.queue).element
  def empty(self):
    return len(self) == 0
  def __len__(self):
    return len(self.queue)
  def __repr__(self):
    #order = self.queue
    order = sorted(self.queue)
    return '{}{}'.format(self.__class__.__name__, order)

class FIFOPriorityQueue(PriorityQueue):
  sign = 1
class FILOPriorityQueue(PriorityQueue):
  sign = -1

##################################################

class ClassicPriorityQueue(StableQueue):
  def __init__(self, array=[]):
    super(ClassicPriorityQueue, self).__init__()
    self.queue = []
    self.priorities = {}
    self.processed = set()
    for x in array:
      self.decrease_key(*x)
  def decrease_key(self, priority, element):
    if (element not in self.priorities) or (priority < self.priorities[element]):
      self.priorities[element] = priority
      heappush(self.queue, self.new_node(priority, element))
  def clean(self):
    # gets rid of redundant queue nodes
    while (len(self.queue) != 0) and (self.queue[0] in self.processed):
      heappop(self.queue)
  def pop(self):
    self.clean()
    element = heappop(self.queue).element
    self.processed.add(element)
    return element
  def empty(self):
    self.clean()
    return len(self.queue) == 0

class FIFOClassicPriorityQueue(ClassicPriorityQueue):
  sign = 1
class FILOClassicPriorityQueue(ClassicPriorityQueue):
  sign = -1
