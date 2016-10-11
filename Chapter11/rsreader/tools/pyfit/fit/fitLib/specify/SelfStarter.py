# SelfStarter from FitLibrary
# Developed by Rick Mugridge Dec 28, 2004
# Copyright 2004 by Rick Mugridge, University of Auckland, NZ
# Released under the terms of the GNU General Public License version 2 or later.
# Python translation copyright 2005, John H. Roth Jr.

from fitLib.specify.SelfStartingActionFixture import SelfStartingActionFixture

class SelfStarter(SelfStartingActionFixture):
    s = ""

    _typeDict = {"enterString": "String",
                 "s": "String",
                 }

    def enterString(self, s):
        self.s = s

    def s(self):
        return self.s
