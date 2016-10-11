# MockCollection from FitLibrary Specification Tests
# Developed by Rick Mugridge
# Copyright 2004 Rick Mugridge, University of Auckland, NZ
# Released under the terms of the GNU General Public License version 2 or later.
# Translation to Python copyright 2005 John H. Roth Jr.

class MockCollection(object):
    def __init__(self, plus, ampersand):
        self.plus = plus
        self.ampersand = ampersand

    def getProp(self):
        return self.plus

    prop = property(getProp)    

