# Fit acceptance test module - not for general use!
# copyright 2004 John H. Roth Jr.
# May be used under the terms of the GNU general license, v2 or later.

import time

try:
    False
except:
    True = 1
    False = 0

class Date:
    aTime = None
    def __init__(self, string):
        try:
            self.aTime = time.strptime(string, "%b %d, %Y")
        except:
            self.aTime = time.strptime(string, "%B %d, %Y")
            

    def __eq__(self, other):
        if self.aTime[0:3] == other.aTime[0:3]:
            return True
        else:
            return False

    def __str__(self):
        return time.strftime(self.aTime, "%B %d, %Y")