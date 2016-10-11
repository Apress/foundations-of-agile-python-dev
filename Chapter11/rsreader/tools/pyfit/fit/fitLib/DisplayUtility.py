# test module for Display Utility addition to FitLibrary
# Fit Library was developed by Rick Mugridge, University of Auckland, NZ
# copyright 2005, John H. Roth Jr.
# Released under the terms of the GNU General Public License, Version 2 or later.
# See license.txt for conditions and exclusion of all warrenties.

try:
    False
except:
    False = 0
    True = 1

import sys
import types
from fit.Fixture import Fixture

from fit.Parse import Parse
from fit import TypeAdapter

def em(msg):
    if msg[-1] != "\n":
        msg += "\n"
    sys.stderr.write(msg)

class DisplayUtility(Fixture):
    def __init__(self, objList, nameList, typeDict):
        self.objList = objList
        self.nameList = nameList
        self._typeDict = typeDict
        super(DisplayUtility, self).__init__()
##        em("\nin displayUtility.init")

    def doTable(self, table):
##        em("--- in doTable")
        cmdRow = table.parts
        cmdRow.more = self.buildHeaderRow(self.nameList)
        self.doRows(cmdRow.more)

    def doRows(self, hdrRow):
##        em("--- in doRows")
        headers = hdrRow.parts
        taList = self.buildTypeAdapterList(self.nameList,
                                  self._typeDict, headers)
        lastRow = hdrRow
        for obj in self.objList:
##            em("--- an object")
            lastRow.more = self.buildRow(obj, self.nameList,
                                         taList, headers)
            lastRow = lastRow.more
        
    def buildHeaderRow(self, nameList):
        head = Parse(tag="xx")
        current = head
        for name in nameList:
            current.more = Parse(tag="td", body=name)
            current = current.more
        return Parse(tag="tr", parts=head.more)

    def buildTypeAdapterList(self, nameList, typeDict, headerCells):
        taList = []
        for name in nameList:
            typeName = typeDict.get(name)
            if typeName is None:
                typeName = typeDict.get(name + ".types")
                if typeName is not None:
                    typeName = typeName[0]
            if typeName is None:
                ta = False
            else:
                ta = TypeAdapter.adapterOnType(self, name, {name: typeName})
            taList.append(ta)
            headerCells = headerCells.more
        return taList

    def buildRow(self, anObject, nameList, taList, headers):
        head = Parse(tag="xx")
        current = head
        i = 0
        while i < len(nameList):
            name = nameList[i]
            ta = taList[i]
            current.more = Parse(tag="td", body=name)
            current = current.more
            field, found = self.extractAttr(anObject, name)
            if found is False:
                current.body = "[not found]"
                self.ignore(current)
                headers = headers.more
                i += 1
                continue
            converted = False
            if not isinstance(ta, types.BooleanType):
                try:
                    result = ta.toString(field)
                    converted = True
                except:
                    result = None
                    converted = False
            if converted is False:
                try:
                    result = str(field)
                    converted = True
                except:
                    result = "[cannot display]"
                    converted = False
                    if ta is False:
                        taList[i] = True
                        self.wrong(headers, "Metadata missing")
            current.body = result
            if converted is False:
                self.wrong(current)
            headers = headers.more
            i += 1
        return Parse(tag="tr", parts=head.more)

    def extractAttr(self, anObj, aName):
        if isinstance(anObj, types.DictType):
            if anObj.has_key(aName):
                return anObj[aName], True
            else:
                return None, False
        try:
            field = getattr(anObj, aName)
            found = True
        except:
            field = None
            found = False
        return field, found

