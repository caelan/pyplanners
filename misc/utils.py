from inspect import currentframe, getargvalues, getargspec, getfile
from caches import *
from numerical import *
from functions import *
from io import *
from generators import *
from objects import *
import importlib
import abc

#https://docs.python.org/2/glossary.html#term-generator

SEPARATOR = '\n'+85*'-'+'\n'

# NOTE - frame = inspect.currentframe()
def arg_info(frame, ignore=['self']):
  #frame_info = inspect.getframeinfo(frame)
  arg_info = getargvalues(frame)
  return {arg: arg_info.locals[arg] for arg in arg_info.args if arg not in ignore}

def function_name(stack): # NOTE - stack = inspect.stack()
  return stack[0][3]

def get_path(frame):
  return os.path.abspath(getfile(frame))
  # os.path.realpath(__file__)

def get_directory(abs_path):
  return os.path.dirname(abs_path)

def global_fn(name):
  # sys.modules[__name__]
  return globals()[name] # locals()

# TODO - method to reload all functions
def refresh(module_name):
  module = importlib.import_module(module_name) # module = __import__(module_name, fromlist=[''])
  reload(module)
  return module
