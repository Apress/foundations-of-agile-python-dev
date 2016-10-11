# ParamRowFixture from FitLibrary
#legalStuff rm04 jr05
# Original version Contains code developed by Rick Mugridge.
# University of Auckland, NZ. Copyright 2004 Rick Mugridge.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# changes Copyright 2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

# subclass that adapts a RowFixture to work with DoFixture.
# The routine that returns it must specify $row as the target type adapter,
# and must initialize it by inserting the _typeDict.

# import copy
from types import ListType, TupleType, GeneratorType, DictType
from fit.FitException import FitException
from fit.RowFixture import RowFixture

class ParamRowFixture(RowFixture):
##    actuals = []
##    targetClass = None
##
##    def __init__(self, aList, typeDict):
##        self.objects = self.setActualCollection(aList)
##        ParamRowFixture._typeDict = typeDict
##
##    def setActualCollection(self, coll):
##        if isinstance(coll, (ListType, TupleType)):
##            return list(copy.copy(coll))
##        elif isinstance(coll, GeneratorType):
##            aList = []
##            for item in coll:
##                self.actuals.append(item)
##            return aList
##        elif isinstance(coll, DictType):
##            aList = coll.items()
##            aList.sort()
##            return [y for x, y in aList]
##        else:
##            raise FitException, ("message",
##                                 "Unsupported collection type %s" %
##                                 collType)
##
##    def query(self):
##        return self.objects

    def getTargetClass(self):
        return ParamRowFixture
    