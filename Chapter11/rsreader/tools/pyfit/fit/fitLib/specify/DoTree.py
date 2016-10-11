# DoTree from FitLibrary Specification Tests
#legalStuff rm04 jr05
# Original version Contains code developed by Rick Mugridge.
# University of Auckland, NZ. Copyright 2004 Rick Mugridge.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# changes Copyright 2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

from fitLib.DoFixture import DoFixture
from fitLib.ListTree import ListTree, Tree, TreeTypeAdapter

class DoTree(DoFixture):
    _typeDict = {}

    _typeDict["tree.types"] = [TreeTypeAdapter, "String"]
    def tree(self, aString = None):
        if aString is None:
            aTree = ListTree("")
            aTree.addChild(ListTree("a"))
            aTree.addChild(ListTree("BB"))
            return aTree
        else:
            return ListTree.parse(aString)        

    _typeDict["teeTree.types"] = [TreeTypeAdapter, TreeTypeAdapter]
    def teeTree(self, t):
        return t

    _typeDict["it.types"] = [TreeTypeAdapter]
    def it(self):
        return TeeTree(self.tree())

class TeeTree(ListTree): # implements Tree, TreeInterface {
    _typeDict = {"tree": TreeTypeAdapter}    
    tree = None # tree

    def __init__(self, tree):
        self.tree = ListTree("B", tree.getChildren())

    _typeDict["title.RenameTo"] = "getTitle"
    _typeDict["getTitle.types"] = ["String"]
    def getTitle(self):
        return self.tree.getTitle()

#    _typeDict["text.RenameTo"] = "getText"
    _typeDict["getText.types"] = ["String"]
    def getText(self):
        return self.tree.getText()

    _typeDict["children.RenameTo"] = "getChildren"
    _typeDict["getChildren.types"] = [TreeTypeAdapter] # ???
    def getChildren(self):
       return self.tree.getChildren()

    _typeDict["text.types"] = ["String"]
    def text(self):
        return self.tree.textToString()

    _typeDict["parseTree.types"] = [TreeTypeAdapter, "String"]
    def parseTree(self, tree):
        return TeeTree(tree)

    _typeDict["toString.types"] = ["String"]
    def toString(self):
        __pychecker__ = "no-override"
        return self.tree.toString()

    _typeDict["toTree.types"] = [TreeTypeAdapter]
    def toTree(self):
        return self.tree

