# Summary from Core FIT
#legalStuff cc02 sm02 jr05
# Original Java version Copyright 2002 Cunningham and Cunningham, Inc.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Original translation to Python Copyright 2002 Simon Michael
# changes Copyright 2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

from fit.Counts import Counts
from fit.Parse import Parse
from fit.Fixture import Fixture

class Summary(Fixture):
    countsKey = "counts"

    def doTable(self, table):
        self.summary[self.countsKey] = self.counts
        table.parts.more = self.rows(self.summary.keys())

    def rows(self, keys):
        keys.sort()
        if len(keys) > 0:
            key = keys[0]
            result = self.tr(self.td(key,
                             self.td(str(self.summary[key]),
                             None)),
                             self.rows(keys[1:]))
            if key == self.countsKey:
                self.mark(result)
            return result
        else:
            return None

    def tr(self, parts, more):
        return Parse(tag="tr", parts=parts, more=more)

    def td(self, body, more):
        cell = Parse(tag="td", body=body, more=more)
        cell.info()
        return cell

    # Annotate counts cell without tabulation.
    def mark(self, row):
        counts = self.counts
        cell = row.parts.more
        if counts.isError():
            cell.wrong()
        else:
            cell.right()
