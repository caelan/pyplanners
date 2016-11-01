import pickle
import json
import subprocess
import datetime
import os
import hashlib # hashlib.sha224("Nobody inspects the spammish repetition").hexdigest()
import platform
import socket

def computer_name():
  #return platform.node() # = platform.platform() = socket.gethostname() ~= os.environ['COMPUTERNAME']
  return platform.uname()[0]
  #return platform.machine()

# http://www.cyberciti.biz/faq/howto-get-current-date-time-in-python/
def filename_datetime():
  return datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

def make_dir(directory):
  if not os.path.exists(directory):
    os.makedirs(directory)

# NOTE - f = __file__
def real_path(f):
  return os.path.realpath(f)

def rel_path(f):
  return os.path.relpath(f)

def abs_path(f):
  return os.path.abspath(f)

def parent_dir(f, n=1):
  if n == 0: return abs_path(f)
  return os.path.dirname(parent_dir(f, n-1))
  # os.path.join(os.path.dirname(__file__), os.path.pardir)

def run_script(*args):
  # TODO - none of these wait if you redirect STDOUT. Maybe something to do with the mathematica/mac...
  #result = os.system('./make_movie.m ' + directory + ' ' + extension)
  #p = subprocess.Popen(['./make_movie.m', directory, extension], stdout=subprocess.PIPE, sterr=subprocess.PIPE)
  #print p.communicate()
  err = subprocess.call(args) # script = './make_movie.m',
  if err != 0:
    return False
  return True

def record_screen(filename, delay=10):
 return run_script('osascript', 'misc/record_screen.scpt', filename, str(delay))

def launch_quicktime():
 return run_script('osascript', 'misc/launch_quicktime.scpt')

def read(filename):
  with open(filename, 'r') as f:
    return f.read()

def write(filename, string):
  with open(filename, 'w') as f:
    f.write(string)

def print_and_write(string, f):
  print string
  f.write(string + '\n')

def write_pickle(filename, data): # NOTE - cannot pickle lambda or nested functions
  with open(filename,'wb') as f:
    pickle.dump(data, f)

def read_pickle(filename):
  with open(filename, 'rb') as f:
    return pickle.load(f)

def write_json(filename, data): # 'filename.json'
  with open(filename, 'w') as f:
    f.write(json.dumps(data))

def read_json(filename):
  with open(filename, 'r') as f:
    return json.loads(f.read())

def pause(message='Paused'):
  raw_input(message)