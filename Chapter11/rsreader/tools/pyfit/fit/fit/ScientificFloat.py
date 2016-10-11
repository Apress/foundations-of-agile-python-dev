# ScientificFloat from Python FIT
#legalStuff cc02 jr04-05
# Original Java version Copyright 2002 Cunningham and Cunningham, Inc.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# changes Copyright 2004-2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

# This is now the base class for Scientific Double.
# The rewrite was to remove all of the Javaisms so that
# it can be used as an example of an application value
# object which can be used directly through the type
# adapter mechanism.

# ScientificDouble is a subclass, and adds all of the
# Javaisms back in for backwards compatability. It cannot
# be used directly through the type adapter mechanism.

# Warning - Special values are not handled at all, let alone properly.

#import math

class ScientificFloat(object):
    value = 0.0
    upperBound = 0.0
    lowerBound = 0.0
    charBounds = "5"

    def __init__(self, value, bounds = "5"):
        self.value = float(value)
        self.charBounds = bounds
        self._computeBounds(value)
        self.precision = self.upperBound - self.lowerBound

    def _computeBounds(self, value):        
        value = value.strip()
        locE = value.lower().find('e')
        locDot = value.find('.')
        if locE >= 0:
            bound = value[:locE] + self.charBounds + value[locE:]
        elif locDot >= 0:
            bound = value + self.charBounds
        else:
            bound = value + "." + self.charBounds
        aBound = float(bound)
        if aBound > self.value:
            self.upperBound = aBound
            self.lowerBound = self.value - abs(aBound - self.value)
        else:
            self.lowerBound = aBound
            self.upperBound = self.value + abs(aBound - self.value)

    def __cmp__(self, obj):
        if isinstance(obj, ScientificFloat):
            other = obj.value
        else:
            other = obj
        if self.lowerBound >= other:
            result = 1
        elif self.upperBound <= other:
            result = -1
        else:
            result = 0
        return result

    def __eq__(self, other):
        return self.__cmp__(other) == 0

    def __ne__(self, other):
        return self.__cmp__(other) != 0

    # !!! the following two methods are not intended to
    #     support general arithmetic operations. They are
    #     here to support unittest and the float type
    #     adapter. Note that they return floats, not
    #     instances of ScientificFloat.
    def __sub__(self, other):
        if isinstance(other, ScientificFloat):
            return self.value - other.value
        else:
            return self.value - other

    def __rsub__(self, other):
        # !!! the first clause shouldn't ever be true unless someone
        #     deliberately calls __rsub__.
        if isinstance(other, ScientificFloat): #pragma: no cover
            return other.value - self.value
        else:
            return other - self.value

##    def compareTo(self, obj):

    # TODO -  __str__ should truncate the number
    # of digits displayed to match the input string.
    # some kind of magic with string formatting should do it.
    
    def __str__(self):
        return str(self.value)
