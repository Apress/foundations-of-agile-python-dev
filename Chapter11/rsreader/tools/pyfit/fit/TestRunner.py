#! python
# TestRunner stub
# copyright 2005 John H. Roth Jr
# released under the GNU General Public License, version 2.0 or higher

import sys
from fitnesse.FitServerImplementation import TestRunner

if __name__ == "__main__":
    obj = TestRunner()
    result = obj.run(sys.argv)
    sys.exit(result)
