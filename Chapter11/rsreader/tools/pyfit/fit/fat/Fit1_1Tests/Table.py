# Copyright (c) 2002 Cunningham & Cunningham, Inc.
# Released under the terms of the GNU General Public License version 2 or later.
# Conversion to Python copyright (c) 2004 John H. Roth Jr.

# This embeds a table within a table so that the errors in the second table
# don't show, and so that the color fixture can check the results in the
# embedded table.

from fit.Fixture import Fixture
from fit.Parse import Parse
import copy

class Table(Fixture):
    #public static Parse table;

    def doRows(self, rows):
        #this.table = new Parse ("table", null, copy(rows), null);
        #// evaluate the rest of the table like a runner
        #(new Fixture()).doTables(this.table);
        table = Parse(tag="table", body="", parts=self.copy(rows), more=None)
        self.setSymbol("Table", table)
        Fixture().doTables(table)

    # note the commented out if statement that puts the tree where it belongs.
    def copy(self, tree):
        return tree
        if tree is None: return None
        return copy.deepcopy(tree)
##        return tree is None:
##            ? null
##            : new Parse(tree.tag, tree.body, copy(tree.parts), copy(tree.more));

