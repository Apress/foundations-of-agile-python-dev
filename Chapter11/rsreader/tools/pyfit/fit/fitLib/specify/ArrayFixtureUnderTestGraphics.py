# ArrayFixtureUnderTestGraphics from FitLibrary Specification Tests
# Developed by Rick Mugridge
# Copyright 2004 Rick Mugridge
# Released under the terms of the GNU General Public License version 2 or later
# Translation to Python copyright 2005 John H. Roth Jr.

from fitLib.ArrayFixture import ArrayFixture
from fitLib.ListTree import ListTree, TreeTypeAdapter

class GraphicElement(object):
    _typeDict = {"i": "Integer",
                 "tree": TreeTypeAdapter}
    i = 0
    tree = None # ListTree

    def __init__(self, i, aTree):
        self.i = i
        self.tree = ListTree.parse(aTree)

class ArrayFixtureUnderTestGraphics(ArrayFixture):
    _typeDict = GraphicElement._typeDict
    def __init__(self):
        super(ArrayFixtureUnderTestGraphics, self).__init__([
            GraphicElement(1, "a"),
            GraphicElement(1, "<ul><li>a</li></ul>"),
            GraphicElement(2, "<ul><li>a</li><li>BB</li></ul>"),
            ])
