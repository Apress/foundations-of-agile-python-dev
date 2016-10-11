# Import fixture from FitNesse
#legalStuff jr04-05
# Copyright 2004-2005 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalStuff

from Fixture import Fixture

class Import(Fixture):
    def doRow(self, row):
        if row.parts.more is None or row.parts.more.text().strip() == "":
            packageName = row.parts.text()
            self.rememberPackage(packageName)
        else:
            alias = row.parts.text()
            packageName = row.parts.more.text()
            self.addRenameToRenameTable(alias, packageName)
