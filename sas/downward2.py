# http://www.fast-downward.org/TranslatorOutputFormat

def write_version(version=3):
  return 'begin_version\n%s\nend_version\n'%version

def write_action_costs(action_costs=False):
  return 'begin_metric\n%s\nend_metric\n'%int(action_costs)

###########################################################################

def write_variables(problem):
  s = '%s\n'%len(problem.var_order)
  for i, var in enumerate(problem.var_order):
    name = 'var%s'%i
    axiom_layer = -1
    s += 'begin_variable\n' \
      '%s\n' \
      '%s\n' \
      '%s\n'%(name, axiom_layer, len(problem.var_val_order[var]))
    for j, val in enumerate(problem.var_val_order[var]):
      name = 'Atom %s-%s()'%(i, j) # NOTE - not sure why it needs this but it does
      s += '%s\n'%name
    s += 'end_variable\n'
  return s

###########################################################################

def write_mutexes(problem):
  s = '%s\n'%len(problem.mutexes)
  for mutex in problem.mutexes:
    s += 'begin_mutex_group\n' \
        '%s\n'%len(mutex)
    for var, val in mutex:
      s += '%s %s\n'%(var, val)
    s += 'end_mutex_group'
  return s

###########################################################################

def write_initial(problem):
  #assert len(problem.initial.values) == len(problem.var_order)
  s = 'begin_state\n'
  for var in problem.var_order:
    #val = problem.get_val(var, problem.initial.values[var])
    val = problem.get_val(var, problem.initial.values.get(var, problem.default_val))
    s += '%s\n'%val
  s += 'end_state\n'
  return s

def write_goal(problem):
  s = 'begin_goal\n' \
      '%s\n'%len(problem.goal.conditions)
  for item in problem.goal.conditions.items():
    var, val = problem.get_var_val(*item)
    s += '%s %s\n'%(var, val)
  s += 'end_goal\n'
  return s

###########################################################################

def write_actions(problem):
  s = '%s\n'%len(problem.actions)
  for i, action in enumerate(problem.actions):
    s += 'begin_operator\n' \
         'a%s\n' \
         '%s\n'%(i, len(action.conditions))
    for item in action.conditions.items():
      var, val = problem.get_var_val(*item)
      s += '%s %s\n'%(var, val)
    s += '%s\n'%len(action.effects)
    for item in action.effects.items():
      var, val = problem.get_var_val(*item)
      s += '0 %s -1 %s\n'%(var, val)
    s += '%s\n' \
         'end_operator\n'%action.cost # Will be treated as 1 if action_costs=False
  return s

###########################################################################

def write_axioms(problem):
  s = '%s\n'%len(problem.axioms)
  for axiom in problem.axioms:
    s += 'begin_rule\n'
    s += '%s\n'%len(axiom.pre)
    for var, val in axiom.pre:
      s += '%s %s\n'%(var, val)
    var_con = -1 # Indicates no value
    s += ' %s %s %s\n'%(axiom.var, var_con, axiom.val)
    s += 'end_rule\n'
  return s

###########################################################################

from misc.io import write, read

import os
from os.path import expanduser
from time import time

#FD_ROOT = expanduser('~/Programs/LIS/planners/FD/')
#FD_PATH = os.path.join(FD_ROOT, 'builds/release32/bin/')
FD_PATH = os.environ.get('FD_PATH', '')

SAS_PATH = 'output.sas'
OUTPUT_PATH = 'sas_plan'

#SEARCH_OPTIONS = '--heuristic "hlm,hff=lm_ff_syn(lm_rhw(reasonable_orders=true,lm_cost_type=plusone),cost_type=plusone)" ' \
#                 '--search "lazy_wastar([hff,hlm],preferred=[hff,hlm],w=1,max_time=%s,bound=%s)"'
SEARCH_OPTIONS = '--heuristic "h=ff(transform=adapt_costs(cost_type=PLUSONE))" ' \
                 '--search "astar(h,max_time=%s,bound=%s)"'

SEARCH_COMMAND = FD_PATH + 'bin/downward %s < %s'%(SEARCH_OPTIONS, SAS_PATH) #+ ' --search-time-limit %s'%10 # TODO - limit

def write_sas(problem):
  s = write_version() + \
    write_action_costs() + \
    write_variables(problem) + \
    write_mutexes(problem) + \
    write_initial(problem) + \
    write_goal(problem) + \
    write_actions(problem) + \
    write_axioms(problem)
  write(SAS_PATH, s)

def fast_downward(debug=False, max_time=30, max_cost='infinity'):
  if os.path.exists(OUTPUT_PATH):
    os.remove(OUTPUT_PATH)
  command = SEARCH_COMMAND%(max_time, max_cost)
  t0 = time()
  p = os.popen(command)
  output = p.read()
  print(command, time() - t0)
  if debug:
    print(output)
  if not os.path.exists(OUTPUT_PATH):
    return None
  return read(OUTPUT_PATH)

def convert_solution(solution, problem):
  lines = solution.split('\n')[:-2] # Last line is newline, second to last is cost
  plan = []
  for line in lines:
    index = int(line.strip('( )')[1:])
    plan.append(problem.actions[index])
  return plan

def solve_sas(problem):
  write_sas(problem)
  plan = fast_downward()
  if plan is None:
    return None
  return convert_solution(plan, problem)
