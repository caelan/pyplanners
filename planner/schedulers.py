class Scheduler(object):
  def __init__(self, rg):
    self.rg = rg
  def __call__(self, start_vertex, connector):
    raise NotImplementedError('Scheduler must implement __call__(self, start_vertex, connector)')

class GeneratingScheduler(Scheduler):
  def __init__(self, rg, subplanners):
    super(self.__class__, self).__init__(rg)
    self.subplanners = subplanners
  def __call__ (self, start_vertex, connector):
    return [subplanner(start_vertex, connector, self.rg) for subplanner in self.subplanners
            if subplanner.applicable(start_vertex, connector, self.rg)]
