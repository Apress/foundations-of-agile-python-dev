
# Copyright (c) 2003 Cunningham & Cunningham, Inc.
# Read license.txt in this directory.

from fit.ColumnFixture import *
import random

class BinaryChop(ColumnFixture):
    _typeDict = {"key": "Int",
                 "array": "List",
                 "array.scalarType": "Int",
                 "mon": "Int",
                 "tue": "Int",
                 "wed": "Int",
                 "thr": "Int",
                 "fri": "Int"}

    key = 0
    array = [0] 

##"""
##// what are these two functions?????
##    public void execute() {
##        int empty[] = {};
##        if (array==null) array=empty;
##    }
##
##    public int result() {
##        return chopFriday(key, array) ;
##    }
##"""

    def mon(self):
        return self.chopMonday(self.key, self.array)
    def tue(self):
        return self.chopTuesday(self.key, self.array)
    def wed(self):
        return self.chopWednesday(self.key, self.array)
    def thr(self):
        return self.chopThursday(self.key, self.array)
    def fri(self):
        return self.chopFriday(self.key, self.array)    

# Search Methods

    def chopMonday(self, key, array):
        # !!! the iMin etc isn't because I like hungarian notation. It's
        #     because min and max are builtin functions, and it's not
        #     good practice to name variables the same as builtins.
        iMin = 0
        iMax = len(array) - 1
        while iMin <= iMax:
            probe = (iMin + iMax) // 2 # !!! Requires 2.2 to force integer divide
            if key == array[probe]:
                return probe
            elif key > array[probe]:
                iMin = probe + 1
            else:
                iMax = probe - 1
        return -1

    def chopTuesday(self, key, array):
        iMin = 0
        iMax = len(array) - 1
        while (iMin <= iMax):
            probe = (iMin + iMax) // 2
            # !!! original  used a switch/case construct. Python
            #     doesn't have one of those things, and I didn't want to
            #     use the dictionary or array lookup method.
            case = cmp(key, array[probe])
            if case == 0:
                return probe
            elif case > 0:
                iMin = probe + 1
            else:
                iMax = probe - 1
        return -1

    def chopWednesday(self, key, array):
        if len(array) == 0: return -1
        probe = len(array) // 2
        if key == array[probe]: return probe
        if key < array[probe]: return self.chopWednesday(key, array[:probe])
        result = self.chopWednesday(key, array[probe+1:])
        if result < 0: return result
        return result + probe + 1

    def chopThursday(self, key, array):
        iMin = 0
        iMax = len(array) - 1
        while iMin <= iMax:
            probe = random.randint(iMin, iMax)
            if key == array[probe]:
                return probe
            if key > array[probe]:
                iMin = probe + 1
            else:
                iMax = probe - 1
        return -1

    def chopFriday(self, key, array):
        for i in xrange(len(array)):
            if key == array[i]: return i
        return -1

