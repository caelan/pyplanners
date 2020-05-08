#!/usr/bin/env python

from __future__ import print_function

from misc.utils import *
from misc.profiling import *
from planner.main import default_plan, default_scheduler_generator
import discrete.problems as problems
import sys
import getopt
import datetime

def solve(problem_name, print_profile=False):
  dt = datetime.datetime.now()
  directory = './simulations/discrete/planning/{}/{}/{}/'.format(problem_name, dt.strftime('%Y-%m-%d'), dt.strftime('%H-%M-%S'))
  start, goal, Scheduler = getattr(problems, problem_name)()
  generator = default_scheduler_generator(goal, Scheduler)

  print(SEPARATOR + '\nSolving planning problem ' + problem_name)

  def execute():
    output = default_plan(start, goal, generator)
    make_dir(directory)
    print('Created directory:', directory)
    return output

  (plan_data, search_data), profile_output = profile(execute, filename=directory+'profile')
  print('Wrote', directory+'profile')
  print(SEPARATOR)

  if plan_data is None:
    data = str_line('Could not find plan\n')
  else:
    data = str(plan_data)
  data += '\n' + str(search_data)
  print(data)
  write(directory + 'planner_statistics', data)
  print('Wrote', directory+'planner_statistics')

  if print_profile:
    print(SEPARATOR)
    print(profile_output)
  print(SEPARATOR)

###########################################################################

HELP_MESSAGE = 'python %s -p <problem>'%(__file__)

def main(argv):
  try:
    opts, args = getopt.getopt(argv, 'hp:q', ['help', 'problem=', 'profile'])
  except getopt.GetoptError:
    print(HELP_MESSAGE)
    return

  problem_name = None
  print_profile = False
  for opt, arg in opts:
    if opt in ('-h', '--help'):
       print(HELP_MESSAGE)
       return
    elif opt in ('-p', '--problem'):
       problem_name = arg
    elif opt in ('-q', '--profile'):
      print_profile = True

  if problem_name is None:
    print(HELP_MESSAGE)
    return
  if not hasattr(problems, problem_name):
    print(problem_name, 'is not a valid problem')
    return
  solve(problem_name, print_profile=print_profile)

if __name__ == '__main__':
  main(sys.argv[1:])
