# Copyright (c) 2002 Cunningham & Cunningham, Inc.
# Released under the terms of the GNU General Public License version 2 or later.
# Converted to Python 2003/07/24 by John Roth

from fit.RowFixture import RowFixture
import MusicLibrary
from Music import Music
# !!! note that Browser must be invoked first: the other
#     modules depend on it to create the interconnections.

class Display(RowFixture):
    def getTargetClass(self):
        return Music

    def query(self):
        return MusicLibrary.displayContents()

    def parse(self, text, objType):
        __pychecker__ = "no-classattr"
        if objType == "Date":  # XXX not correct - check this out
            return Music.dateFormat.parse(text)
        return super.parse(text, objType)
