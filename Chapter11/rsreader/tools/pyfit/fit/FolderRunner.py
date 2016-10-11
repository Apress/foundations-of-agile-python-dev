#! python
# FolderRunner execution stub.
# copyright 2005 John H. Roth Jr.
# released under the terms of the GNU General Public License, version 2 or later.
# this is a complete ground-up reimplementation of the original FileRunner.
import sys
from fit.RunnerImplementation import FileRunner

if __name__ == '__main__':
    obj = FileRunner()
    if not obj.parms(sys.argv):
        sys.exit(-1)
    result = obj.run()
    sys.exit(result)
