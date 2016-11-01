import cProfile, pstats, StringIO
import os

def run_profile(function):
  pr = cProfile.Profile() # cProfile.run('simulation()', sort = 'cumtime')
  pr.enable()
  results = function()
  pr.disable()
  return results, pr

def str_profile(pr, limit=25):
  output = StringIO.StringIO()
  ps = pstats.Stats(pr, stream=output)
  #print ps.__dict__.keys()
  directory = os.getcwd()
  for (f, l, fn), value in ps.stats.items():
    if directory in f:
      ps.stats[(f[f.index(directory)+len(directory):], l, fn)] = value
      del ps.stats[(f, l, fn)]
  ps.fcn_list = list(ps.stats.keys())
  ps.sort_stats('tottime') # .strip_dirs()

  ps.print_stats(limit) # ps.print_stats(.1) # ps.reverse_order()
  so = '\n' + '\n'.join(output.getvalue().split('\n')[::-1]).strip('\n')
  # print '\n' + output.getvalue().strip('\n') + '\n'
  output.close()
  return so

def write_profile(pr, filename):
  with open(filename, 'w') as fo:
    ps = pstats.Stats(pr, stream=fo).strip_dirs().sort_stats('tottime')
    ps.print_stats()
