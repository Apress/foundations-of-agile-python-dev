# Copyright (c) 2002 Cunningham & Cunningham, Inc.
# Released under the terms of the GNU General Public License version 2 or later.
# Conversion to Python copyright (c) 2004 John H. Roth Jr.

from fit.PrimitiveFixture import PrimitiveFixture
import fit.TypeAdapter
TypeAdapter = fit.TypeAdapter
from fat.Money import Money
from fit.ScientificDouble import ScientificDouble
from fat.Date import Date

class Equals(PrimitiveFixture):

    heads = None
    type = None
    x = None
    y = None
    result = None

    def doRows(self, rows):
        self.heads = rows.parts
        PrimitiveFixture.doRows(self, rows.more)

    def doCell(self, cell, col):
        try:
            head = self.heads.at(col).text()[:1]
            if head == "t":
                self.type = self.getTypeAdapter(cell.text().title())
            elif head == "x":
                self.x = self.type.parse(cell.text())
            elif head == "y":
                self.y = self.type.parse(cell.text())
            elif head == "=":
                self.check(cell, self.type.equals(self.x, self.y))
            elif head == "?":
                cell.addToBody(self.gray("x: %s y: %s" % (self.x, self.y)))
            else:
                raise Exception, "don't do " + head
        except Exception, e:
            self.exception(cell, e)

    def getTypeAdapter(self, typeName):
        metadata = {}
        if typeName.endswith("s"):
            shortName = typeName[:-1]
        else:
            shortName = typeName
        adapter = self.typeAdapterMap.get(shortName)
        if adapter is None:
            adapter = shortName.title()
        metadata = {typeName: adapter}

        if type(adapter) not in (type(""), type(u"")):
            metadata = {typeName: "Generic",
                        "%s.ValueClass" % typeName: adapter}

        if typeName.endswith("s"):
            metadata["%s.scalarType" % typeName] = metadata[typeName]
            metadata[typeName] = "List"

        return TypeAdapter.on(self, typeName, metadata)

    typeAdapterMap = {"Integer": "Int",
                      "Real": "Float",
                      "Money": Money,
                      "Scientific": ScientificDouble,
                      "Date": Date,
                      }
##    # XXX don't quite know what to do with this - it's an override for something...
##    def parse(self, s, type): # legitimate override of parse method...
##        if (type == "Money"):   return Money(s) # XXX where is this one???
##        if (type == "Boolean"): return self.parseCustomBoolean(s)
##        return Fixture.parse(self, s, type)

##    def parseCustomBoolean(self, s):
##        return None

    # special check for "=" column - TypeAdapters aren't set up for this!
    def check(self, cell, value):
        text = cell.text()
        adapter = TypeAdapter.on(self, "dummy", {"dummy": "Boolean"})
        expected = adapter.parse(text)
        if expected != value:
            self.wrong(cell, str(value))
        else:
            self.right(cell)

    def _print(self, value): # XXX probably not used any more...
        return self.type.toString(value)


