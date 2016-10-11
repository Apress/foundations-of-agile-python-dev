# Copyright (C) 2003,2004 by Robert C. Martin and Micah D. Martin. All rights reserved.
# Released under the terms of the GNU General Public License version 2 or later.
# Port to Python copyright 2004 John H. Roth Jr.

# This is a test fixture that is not generally useful.

from fit.ColumnFixture import ColumnFixture

class ColumnFixtureTestFixture(ColumnFixture):
    _typeDict = {
        "input": "Int",
        "output": "Int",
        }
    input = '1'
    def output(self):
        return self.input
    
