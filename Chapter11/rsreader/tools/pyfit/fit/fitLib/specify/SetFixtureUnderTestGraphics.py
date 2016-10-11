# SetFixtureUnderTestGraphics from FitLibrary Acceptance Tests
# Developed by Rick Mugridge
# Copyright 2004 Rick Mugridge, University of Auckland, NZ
# Released under the terms of the GNU General Public License version 2 or later
# Translation to Python copyright 2005 John H. Roth Jr.

from fitLib.SetFixture import SetFixture
from fitLib.specify.ArrayFixtureUnderTestGraphics import GraphicElement as GE

class SetFixtureUnderTestGraphics(SetFixture):
    _typeDict = GE._typeDict
    def __init__(self):
        super(SetFixtureUnderTestGraphics, self).__init__(
            [GE(1, "a"),
             GE(1,"<ul><li>a</li></ul>"),
             GE(2,"<ul><li>a</li><li>BB</li></ul>")])
