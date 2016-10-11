#!/usr/local/bin/python

import os
from subprocess import Popen
import sys

def bin_dir():
    this_file = sys.modules[__name__].__file__
    return os.path.dirname(os.path.abspath(this_file))
   
def find_dev_root(d):
    setup_py = os.path.join(d, 'setup.py')
    if os.path.exists(setup_py):
       return d
    parent = os.path.dirname(d)
    if parent == d:
       return None
    return find_dev_root(parent)

dev_root = find_dev_root(bin_dir())
if dev_root is None:
     msg = "Could not find development environment root"
     print >> sys.stderr, msg
     sys.exit(1)
os.chdir(dev_root)

cmd = "%(python)s %(fitrunner)s +r %(requirements)s %(reports)s"
expansions = dict(python=sys.executable,
                  fitrunner='./tools/pyfit/fit/FolderRunner.py',
                  requirements='./acceptance/requirements',
                  reports='./acceptance/reports')
env = dict(PYTHONPATH='tools/pyfit/fit:acceptance/fixtures')
              
proc = Popen(cmd % expansions, shell=True, env=env)
proc.wait()


