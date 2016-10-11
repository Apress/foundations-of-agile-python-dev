# FixtureWithHiddenConstructor from FitLibrary Acceptance Tests
# Developed by Rick Mugridge on Dec 23, 2004.
# Copyright 2004 by Rick Mugridge, University of Auckland, NZ
# Released under the terms of the GNU General Public License version 2 or later.
# Python translation copyright 2005, John H. Roth Jr.

# Note - this is untranslatable - Python does not have
# any equivalent of a private constructor, at least without
# doing some deep magic with either metaclasses or the
# __new__ magic method.


from fit.Fixture import Fixture
from fit.FitException import FitException

class FixtureWithHiddenConstructor(Fixture):
    def __init__(self):
        raise FitException("NoConstructor")
