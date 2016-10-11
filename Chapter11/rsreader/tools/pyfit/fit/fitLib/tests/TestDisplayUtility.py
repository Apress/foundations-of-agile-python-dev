# test module for Display Utility 
# copyright 2005, John H. Roth Jr.
# Released under the terms of the GNU General Public License, Version 2 or later.
# See license.txt for conditions and exclusion of all warrenties.

import sys
import unittest
from fit.Parse import Parse
from fitLib.DisplayUtility import DisplayUtility

try:
    False
except:
    True = 1
    False = 0

def em(msg):
    if msg[-1] != "\n":
        msg += "\n"
    sys.stderr.write(msg)

def makeDisplayUtilityTest():
    theSuite = unittest.makeSuite(Test_DisplayUtility, 'test')
#    theSuite.addTest(unittest.makeSuite(Test_FooBar, 'Test'))
    return theSuite

class FakeObject(object):
    def __init__(self, aDict):
        for key, value in aDict.items():
            setattr(self, key, value)

class ThrowsExceptionForStr(object):
    def __str__(self):
        raise Exception

class Test_DisplayUtility(unittest.TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())

    nameList = ["fie", "fi", "fo", "fum"]
    typeDict = {
        "fie": "Integer",
        "fi": "String",
        "fo": "Boolean",
        "fum": "Float"
        }

    def testInstantiation(self):
        objList = []
        obj = DisplayUtility(objList, self.nameList, self.typeDict)
        assert obj.objList == objList
        assert obj.nameList == self.nameList
        assert obj._typeDict == self.typeDict

    def testBuildHeaderRow(self):
        objList = []
        typeDict = {}
        obj = DisplayUtility(objList, self.nameList, typeDict)
        row = obj.buildHeaderRow(self.nameList)
        assert row.parts.size() == 4
        assert row.tag == "<tr>"
        assert row.parts.more.more.body == "fo"

    def testBuildTypeAdapterList(self):
        objList = []
        obj = DisplayUtility(objList, self.nameList, self.typeDict)
        headers = obj.buildHeaderRow(self.nameList).parts
        taList = obj.buildTypeAdapterList(self.nameList,
                                          self.typeDict, headers)
        assert taList[0].parse("1") == 1
        assert taList[2].toString(True) == "True"

    def testBuildListWithMissingTypeAdapter(self):
        nameList = ["fie", "fi", "fo", "fiddly"]
        objList = []
        obj = DisplayUtility(objList, nameList, self.typeDict)
        headers = obj.buildHeaderRow(nameList).parts
        taList = obj.buildTypeAdapterList(nameList,
                                          self.typeDict, headers)
        assert taList[3] is False

    dict1 = {"fie": 1, "fi": "fie on it!", "fo": False, "fum": 1.0}
    theObject = FakeObject(dict1)
    objList = [theObject]
    def testBuildRowFromObject(self):
        __pychecker__ = "maxrefs=10"
        obj = DisplayUtility(self.objList, self.nameList, self.typeDict)
        headers = obj.buildHeaderRow(self.nameList).parts
        taList = obj.buildTypeAdapterList(self.nameList,
                                          self.typeDict, headers)
        row = obj.buildRow(self.theObject, self.nameList, taList, headers)
        assert row.parts.size() == 4
        assert row.parts.tag == "<td>"
        assert row.parts.more.more.body == "False"

    theObject4 = FakeObject({"fie": 1, "fi": "fie on it!",
                            "fo": False})
    objList4 = [theObject4]
    def testBuildRowWithMissingAttribute(self):
        __pychecker__ = "maxrefs=10"
        obj = DisplayUtility(self.objList4, self.nameList, self.typeDict)
        headers = obj.buildHeaderRow(self.nameList).parts
        taList = obj.buildTypeAdapterList(self.nameList,
                                          self.typeDict, headers)
        row = obj.buildRow(self.theObject4, self.nameList, taList, headers)
        assert row.parts.size() == 4
        assert row.parts.more.more.more.body.find("[not found]") > -1
        assert row.parts.more.more.more.tag.find("fit_ignore") > -1

    shortTypeDict = {
        "fie": "Integer",
        "fi": "String",
        "fo": "Boolean",
        }

    dict3 = {"fie": 1, "fi": "fie on it!",
                            "fo": False, "fum": 2.0}
    theObject3 = FakeObject(dict3)
    objList3 = [theObject3]

    def testBuildRowWithMissingTypeAdapter(self):
        __pychecker__ = "maxrefs=10"
        obj = DisplayUtility(self.objList3, self.nameList,
                             self.shortTypeDict)
        headers = obj.buildHeaderRow(self.nameList).parts
        taList = obj.buildTypeAdapterList(self.nameList,
                                          self.typeDict, headers)
        row = obj.buildRow(self.theObject3, self.nameList, taList, headers)
        assert row.parts.size() == 4
        assert row.parts.more.more.more.body == "2.0"
        assert row.parts.more.more.more.tag == "<td>"

    theObject2 = FakeObject({"fie": 1, "fi": "fie on it!",
                    "fo": False, "fum": ThrowsExceptionForStr()})
    objList2 = [theObject2]
    
    def testBuildRowWithMissingTypeAdapterAndNoStr(self):
        __pychecker__ = "maxrefs=10"
        obj = DisplayUtility(self.objList2, self.nameList,
                             self.shortTypeDict)
        headers = obj.buildHeaderRow(self.nameList).parts
        taList = obj.buildTypeAdapterList(self.nameList,
                                          self.shortTypeDict, headers)
        row = obj.buildRow(self.theObject2, self.nameList, taList, headers)
        assert row.parts.size() == 4
        assert row.parts.more.more.more.body == "[cannot display]"
        assert headers.more.more.more.body.find("Metadata missing") > -1
        assert headers.more.more.more.tag.find("fit_fail") > -1
        assert row.parts.more.more.more.tag.find("fit_fail") > -1

    def testDoTableHeaderRow(self):
        obj = DisplayUtility(self.objList, self.nameList,
                             self.typeDict)
        aTable = Parse(tag="table")
        obj.doTable(aTable)
        assert aTable.parts.parts.body == "fie"

    objList5 = [theObject, theObject3]
    def testDoTableAndTwoObjects(self):        
        __pychecker__ = "maxrefs=10"
        obj = DisplayUtility(self.objList5, self.nameList,
                             self.typeDict)
        aTable = Parse(tag="table")
        obj.doTable(aTable)
        row1 = aTable.parts
        row2 = row1.more
        row3 = row2.more
        assert row3.more is None
        assert row1.parts.body == "fie"
        assert row3.parts.more.more.more.body == "2.0"

    dictList5 = [dict1, dict3]
    def testDoTableWithTwoDictionaries(self):
        __pychecker__ = "maxrefs=10"
        obj = DisplayUtility(self.dictList5, self.nameList,
                             self.typeDict)
        aTable = Parse(tag="table")
        obj.doTable(aTable)
        row1 = aTable.parts
        row2 = row1.more
        row3 = row2.more
        assert row3.more is None
        assert row1.parts.body == "fie"
        assert row3.parts.more.more.more.body == "2.0"

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main(defaultTest='makeDisplayUtilityTest')
