# ClearStartInActionFixture from FitLibrary
# Developed by Rick Mugridge
# Copyright 2004 by Rick Mugridge, University of Auckland, NZ
# Released under the terms of the GNU General Public License version 2 or later.
# Python translation copyright 2005, John H. Roth Jr.

# Clear the actor class variable in ActionFixture so that it
# doesn't confuse things in subsequent tests.
# (This corresponds to a static variable in Java)


from fit.ActionFixture import ActionFixture
from fit.Fixture import Fixture

class ClearStartInActionFixture(Fixture):
    def __init__(self):
        ActionFixture.actor = None
        Fixture.__init__(self) # precaution
