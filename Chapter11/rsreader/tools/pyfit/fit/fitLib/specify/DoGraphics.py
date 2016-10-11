# DoGraphics part of FitLibrary specification tests
#LegalStuff rm05 jr05
# Original version Contains code developed by Rick Mugridge.
# University of Auckland, NZ. Copyright 2005 Rick Mugridge.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# changes Copyright 2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

from fitLib.DoFixture import DoFixture
from fitLib.ImageFixture import GraphicTypeAdapter
from fitLib.DotGraphic import DotGraphic

class DoGraphics(DoFixture):
    _typeDict = {"graph.types": [{"graph": GraphicTypeAdapter,
                                  "graph.class": DotGraphic}]}
    def graph(self):
        # Miscapitalization of Anna and anna is in original, required
        # for test to work. Error is expected.
        return (DotGraphic("digraph G {\n"
                "lotr->luke;\n"
                "lotr->Anna;\n" 
                "shrek->luke;\n"
                "shrek->anna;\n"
                "shrek->madelin;\n"
                "}\n"))
