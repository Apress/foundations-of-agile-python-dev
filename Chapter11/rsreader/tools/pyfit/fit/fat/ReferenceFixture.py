# ReferenceFixture from FIT Acceptance Tests
# Copyright 2004 Jim Shore
# Copyright released via the GNU General Public License, version 2.0 or later
# Python translation copyright 2005 John H. Roth Jr.

# A fixture that processes other Fit documents.

from fit.ColumnFixture import ColumnFixture

class ReferenceFixture(ColumnFixture):
    _typeDict = {"Description": "String",
                 "Location": "String",
                 }
    Description = ""
    Location = ""

    _typeDict["Result"] = "String"
    def Result(self):
        inputFileName = "../../spec/" + self.Location
#        outputFileName = "output/spec/" + self.Location
        return "file not found: " + inputFileName

##        try:
##            FileRunner runner = new FileRunner();
##            runner.args(new String[]{inputFileName, outputFileName});
##            runner.process();
##            runner.output.close();
##            
##            Counts counts = runner.fixture.counts;
##            if ((counts.exceptions == 0) && (counts.wrong == 0)) {
##                return "pass";
##            }
##            else {
##                return "fail: " + counts.right + " right, " + counts.wrong + " wrong, " + counts.exceptions + " exceptions";
##            }
##        }
##        catch (IOException e) {
##            File inputFile = new File(inputFileName);
##            String fileDescription;
##            try {
##                fileDescription = inputFile.getCanonicalPath();
##            }
##            catch (IOException e2) {
##                fileDescription = inputFile.getAbsolutePath();
##            }
##            return "file not found: " + fileDescription;
##        }
##    }
##}
