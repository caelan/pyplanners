# http://www.fast-downward.org/TranslatorOutputFormat

def write_version(version=3):
  return 'begin_version\n%s\nend_version'%version

def write_action_costs(action_costs=False):
  return 'begin_metric\n%s\nend_metric'%int(action_costs)

###########################################################################

def write_variable(v):
  s = 'begin_variable\n' \
      '%s\n' \
      '%s\n' \
      '%s'%(v.name, v.axiom_layer, len(v.values))
  for val in v.values:
    s += '\n' + val.name
  s += 'end_variable'
  return s

def write_variables(variables):
  s = '%s'%len(variables)
  for var in variables:
    s += '\n' + write_variable(var)
  return s

###########################################################################

def write_mutex(mutex):
  s = 'begin_mutex_group\n' \
      '%s\n'%len(mutex)
  for var, val in mutex:
    s += '%s %s\n'%(var, val)
  s += 'end_mutex_group'
  return s

def write_mutexes(mutexes):
  s = '%s'%len(mutexes)
  for mutex in mutexes:
    s += '\n' + write_mutex(mutex)
  return s

###########################################################################

def write_initial(state):
  s = 'begin_state\n'
  for val in state:
    s += val + '\n'
  s += 'end_state'
  return s

def write_goal(goal):
  s = 'begin_goal\n' \
      '%s\n'%len(goal)
  for var, val in goal:
    s += '%s %s\n'%(var, val)
  s += 'end_goal'
  return s

###########################################################################

def write_effect(eff):
  s = '%s'%len(eff.con)
  for var, val in eff.con:
    s += ' %s %s'%(var, val)
  var_con = -1 # Indicates no value
  s += ' %s %s %s'%(eff.var, var_con, eff.val)
  return s

def write_action(action):
  s = 'begin_operator\n' \
      '%s\n' \
      '%s\n'%(action.name, len(action.pre))
  for var, val in action.pre:
    s += '%s %s\n'%(var, val)
  s += '%s\n'%len(action.eff)
  for var, val in action.eff:
    s += '%s %s\n'%(var, val)
  s += '%s\n' \
       'end_operator'%action.cost # Will be treated as 1 if action_costs=False
  return s

def write_actions(actions):
  s = '%s\n'%len(actions)
  for action in actions:
    s += '\n' + write_action(action)
  return s

###########################################################################

def write_axiom(axiom):
  s = 'begin_rule\n'
  s += '%s\n'%len(axiom.pre)
  for var, val in axiom.pre:
    s += '%s %s\n'%(var, val)
  var_con = -1 # Indicates no value
  s += ' %s %s %s\n'%(axiom.var, var_con, axiom.val)
  s += 'end_rule'
  return s

def write_axioms(axioms):
  s = '%s\n'%len(axioms)
  for axiom in axioms:
    s += '\n' + write_axiom(axiom)
  return s

###########################################################################

from misc.io import write, read

PATH = 'output.sas'

def write_file(problem):
  write(PATH, problem)



