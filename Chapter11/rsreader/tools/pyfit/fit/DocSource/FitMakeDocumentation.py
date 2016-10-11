#! python
# simplistic make utility.
# copyright 2004-2005 John H. Roth Jr. All rights reserved.
# Released under the terms of the GNU General Public License, version 2.0 or later

# All it does is check if a module has been
# updated between the DocSource and Doc directories, and invoke
# docutils if it hasn't.

import os, os.path

class Make:
    def doit(self, txtDirName, htmDirName):
        thePath = os.getcwd()
        txtPathName = os.path.join(thePath, txtDirName)
        txtDirList = os.listdir(txtPathName)
        txtDirList.sort()
        htmPathName = os.path.join(thePath, htmDirName)
        htmDirList = os.listdir(htmPathName)
        htmDirList.sort()
        i = j = 0
        while (i < len(txtDirList) and (j < len(htmDirList))):
            txtRoot, txtExt = os.path.splitext(txtDirList[i])
            if txtExt != ".txt":
                i += 1
                continue
            htmRoot, htmExt = os.path.splitext(htmDirList[j])
            if htmExt != ".htm":
                j += 1
                continue
                                               
            if txtRoot == htmRoot:
                txtFileName = os.path.join(txtPathName, txtDirList[i])
                txtTime = os.stat(txtFileName)
                htmFileName = os.path.join(htmPathName, htmDirList[j])
                htmTime = os.stat(htmFileName)
                if txtTime.st_mtime > htmTime.st_mtime:
                    print "%s is being updated" % txtDirList[i]
                    os.system('html2 "%s" "%s"' % (txtFileName, htmFileName))
                else:
                    print "%s does not need to be updated" % txtDirList[i]
                i += 1
                j += 1
            elif txtDirList[i] < htmDirList[j]:
                if txtExt == ".txt":
                    txtFileName = os.path.join(txtPathName, txtDirList[i])
                    txtRoot, txtExt = os.path.splitext(txtDirList[i])
                    htmFileName = os.path.join(htmPathName, txtRoot + ".htm")
                    print "%s is a new module" % txtDirList[i]
                    os.system('html2 "%s" "%s"' % (txtFileName, htmFileName))
                i += 1
            else:
                print "%s is an obsolete module" % htmDirList[j]
                j += 1
        while i < len(txtDirList):
            txtRoot, txtExt = os.path.splitext(txtDirList[i])
            if txtExt == ".txt":
                txtFileName = os.path.join(txtPathName, txtDirList[i])
                txtRoot, txtExt = os.path.splitext(txtDirList[i])
                htmFileName = os.path.join(htmPathName, txtRoot + ".htm")
                print "%s is a new module" % txtDirList[i]
                os.system('html2 "%s" "%s"' % (txtFileName, htmFileName))
            i += 1
        while j < len(htmDirList):
            print "%s is an obsolete module" % htmDirList[j]
            j += 1

if __name__ == "__main__":
    Make().doit(".", "../Doc")
            
            
        
    