#! python ???
# FitServer stub
# copyright 2005 John H. Roth Jr
# released under the GNU General Public License, version 2.0 or higher

import sys
from fitnesse.FitServerImplementation import FitServer

if __name__ == "__main__":
    obj = FitServer()
    result = obj.run(sys.argv)
    sys.exit(result)
