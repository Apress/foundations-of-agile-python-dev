# ScientificDouble is an example from core FIT
#LegalStuff cc02 jr04-05
# Original Java version Copyright 2002 Cunningham and Cunningham, Inc.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# changes Copyright 2004-2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

# Warning - Special values are not handled at all, let alone properly.

# This is now a subclass of ScientificFloat. The former conforms to
# good Python style guidelines and does not have any Javaisms. It
# can be used as its own type adapter. ScientificDouble adds all of
# the Javaisms back in for backwards compatability.

#import math
from fit.ScientificFloat import ScientificFloat

class ScientificDouble(ScientificFloat):
    def valueOf(s):
        return ScientificDouble(s)
    valueOf = staticmethod(valueOf)

    def parse(s):
        return ScientificDouble(s)
    parse = staticmethod(parse)

    def equals(self, obj):
        return self.__eq__(obj)

    def toString(self):
        return str(self.value)

    def doubleValue(self):
        return self.value

    def floatValue(self):
        return self.value

    def longValue(self):
        return int(self.value)

    def intValue(self):
        return int(self.value)
