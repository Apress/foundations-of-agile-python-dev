# Grid Fixture Under Test from FitLibrary Specification Tests
# Developed by Rick Mugridge
# Copyright 2005 Rick Mugridge, University of Auckland, NZ
# Released under the terms of the GNU General Public License, version 2.0 or later
# Python translation copyright 2005 John H. Roth Jr.

from fitLib.DoFixture import DoFixture
from fitLib.GridFixture import GridFixture
from fitLib.ImageFixture import ImageFixture, ImageNameGraphic, GraphicTypeAdapter
from fitLib.ListTree import ListTree, TreeTypeAdapter

try:
    False
except:
    False = 0
    True = 1

class GridFixtureUnderTest(DoFixture):
    _typeDict = {}

    _typeDict["empty.types"] = [None]    
    def empty(self):
        return GridFixture([], {"name": "String"})

    _typeDict["strings.types"] = [None]    
    def strings(self):
        return GridFixture([["a", "b"], ["c", "d"]], {"name": "String"})
    
    _typeDict["ints.types"] = [None]    
    def ints(self):
        return GridFixture([[1, 2], [3, 4]], {"name": "Int"})
    
    _typeDict["trees.types"] = [None]    
    def trees(self):
        return GridFixture([
                [ ListTree.parse("a"),
                  ListTree.parse("<ul><li>a</li></ul>") ],
                [ ListTree.parse("<ul><li>BB</li></ul>"),
                  ListTree.parse("<ul><li>a</li><li>BB</li></ul>")]],
                           {"name": TreeTypeAdapter})

    _typeDict["images.types"] = [None]
    def images(self):
        return GridFixture([[
            ImageNameGraphic("images/wall.jpg"),
            ImageNameGraphic("images/space.jpg"),
            ImageNameGraphic("images/box.jpg"),
            ImageNameGraphic("images/space.jpg"),
            ImageNameGraphic("images/wall.jpg"),
            ]], {"name": GraphicTypeAdapter,
                 "name.class": ImageNameGraphic})

    _typeDict["imagesForImageFixture"] = [None]
    def imagesForImageFixture(self):
        return ImageFixture([[
            ImageNameGraphic("images/wall.jpg"),
            ImageNameGraphic("images/space.jpg"),
            ImageNameGraphic("images/box.jpg"),
            ImageNameGraphic("images/space.jpg"),
            ImageNameGraphic("images/wall.jpg"),
            ]])
