# ParseUtility from FitLibrary,
# copyright 2004, 2005 Rick Mugridge, University of Auckland, NZ
# Released under the General Public License, version 2.0 or later.
# Python translation copyright 2005, John H. Roth Jr.

import sys
from fit.Parse import Parse

ASCII_ENCODING = "ASCII"
START_BODY = "<body>"
END_BODY = "</body>"

def toString(tables):
    return tables.toString() # returns either normal or unicode string.

# XXX untested!
def printParse(tables, title):
    print "---------Parse tables for "+title+":----------"
    if tables is None:
        output = "No output to print!"
    else:
        output = tables.toString()
        if type(output) == type(u""):
            output = output.encode(sys.getdefaultencoding(), "replace")
    print output
    print "----------------------------"

# !!! should be appendRowToTable
# XXX untested
def addRowToTable(table, cells):
    if type(cells) != type([]):
        cells = [cells]
    if not len(cells):
            raise ValueError("Can't have an empty row.") # xxx better exception!
    root = Parse(tag="td", body="fake anchor")
    here = root
    for cell in cells:
        here.more = Parse(tag="td", body=cell)
        here = here.more
    table.parts.last().more = Parse(tag="tr", body="", more=root.more)

#   Append the second Parse to the first, which is a setup.
#   Transfer trailer on the front to the leader of the back.
def appendToSetUp(front, back):
        if back is None:
            return
        changeHeader(front, removeHeader(back))
        fixTrailers(front, back)
        front.last().more = back

#   Append the second Parse to the first, transferring
#   any trailer on the front to the leader of the back */
def append(front, back):
    if back is None:
        return
    removeHeader(back)
    fixTrailers(front, back)
    front.last().more = back

#   Move the last trailer of the front onto the leader of the back.
#   That's because logically the 'next' element of a node points either
#       to another node or to text (or nothing). It can't point to both.
def fixTrailers(front, back):
    # NB, Parse makes the leader a "\n" by default.
    frontLast = front.last()
    frontTrailer = frontLast.trailer
    extra = frontTrailer
    # this is clearly a special case, but why?
    # should it attempt to migrate the </body></html> to the end?
    index = frontTrailer.find(END_BODY)
    if index >= 0:
        extra = frontTrailer[0:index]
    if extra != "":
        if back.leader in ("\n<br>", "\n", "<br>"):
            back.leader = extra + back.leader
        else:
            back.leader = extra + "<br>" + back.leader
    frontLast.trailer = ""

def removeHeader(tables):
        index = tables.leader.find(START_BODY)
        if index < 0:
            return ""
        index += len(START_BODY)
        result = tables.leader[0:index]
        tables.leader = tables.leader[index:] 
        return result

def changeHeader(tables, tablesHeader):
        index = tables.leader.find(START_BODY)
        if index < 0:
            tables.leader = tablesHeader + tables.leader
        else:
            tables.leader = tablesHeader + tables.leader[index+len(START_BODY):]

def completeTrailer(tables):
    last = tables.last()
    index = last.trailer.find(END_BODY)
    if index < 0:
        last.trailer += "\n</body></html>\n"

def copyParse(tables):
        if tables is None:
            return None
        parse = Parse(tag="", body=tables.body,
                parts=copyParse(tables.parts), more=copyParse(tables.more))
        parse.tag = tables.tag
        parse.end = tables.end
        parse.leader = tables.leader
        parse.trailer = tables.trailer
        return parse

# XXX Untested
# if the encoding is unicode, this will return UTF-8, not one of the 8-bit character sets.
def writeParse(reportPath, parse):
    output = open(reportPath, "w")
    output.write(parse.toPrint)
    output.close()
