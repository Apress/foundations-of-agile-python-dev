# ListTree support module from FitLibrary
#legalStuff rm05 jr05
# Original version Contains code developed by Rick Mugridge.
# University of Auckland, NZ. Copyright 2005 Rick Mugridge.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# changes Copyright 2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

# Support for a tree structure that is rendered as an HTML unordered list.

import sys
import types
from fit.Parse import Parse

def em(msg):
    return
    if msg[-1] != "\n":
        msg += "\n"
    sys.stderr.write(msg)

# marker interface for ListTree and mocks.
class Tree(object):
    def getTitle(self): return ""
    def getText(self): return ""
    def getChildren(self): return []
    def text(self): return ""

# Marker interface for Tree type adapters and subclasses
class TreeInterface(object):
    def toTree(self): return None
#//    public static boolean equals(Object o1, Object o2);
#//    public static Tree parseTree(String s);

class ListTree(Tree):
    _title = ""
    _text = ""
    _children = [] # elements of type Tree

    def __init__(self, title, children=None):
        self.setTitle(title)
        if type(children) != type([]):
            self._children = []
        else:
            self._children = children

    def getTitle(self):
        return self._title

    def setTitle(self, title):
        self._title = title.strip()
        self.setText(self._title)
    title = property(getTitle, setTitle)

    def getText(self):
        return self._text

    def setText(self, text):
        self._text = self.removeTags(text).strip()
    text = property(getText, setText)

    def getChildren(self):
        return self._children

    def clearChildren(self):
        self._children = []

    def addChild(self, tree):
        self._children.append(tree)
    children = property(getChildren, addChild, clearChildren)

    def toString(self, depth=999):
        if not self._children:
            return self._title
        result = []
        result += self._toString(depth)
        return "".join(result)

    def _toString(self, depth):
        if not self._children or depth <= 1:
            return [self.title]
        result = [self._title, "<ul>"]
        for child in self._children:
            result.append("<li>")
            result += child._toString(depth - 1)
            result.append("</li>")
        result.append("</ul>")
        return result

    def textToString(self):
        if not self._children:
            return self._text
        result = []
        result += self._textToString()
        return "".join(result)

    def _textToString(self):
        if not self._children:
            return [self.text]
        result = [self.text, "<ul>"]
        for child in self._children:
            result.append("<li>")
            result += child._textToString()
            result.append("</li>")
        result.append("</ul>")
        return result

    def __ne__(self, other):
        return not self == other

    def __eq__(self, other):
        em("in ListTree.== other: '%s'" % other)
        if not isinstance(other, Tree):
            return False
        em("--- before _text compare. a: '%s' b: '%s'" % (self._text,
                                                          other._text))
        if self._text != other._text:
            return False
        if len(self._children) != len(other._children):
            return False
        for t1, t2 in zip(self._children, other._children):
            if t1 == t2:
                continue
            return False
        return True

    def equals(t1, t2):
        em("in ListTree.equals")
        if isinstance(t1, Tree) and isinstance(t2, Tree):
            em("--- both operands are trees. invoking == operator. "
               "t1._text: '%s' t2._text: '%s'" % (t1._text, t2._text))
            return t1 == t2
        if isinstance(t1, types.ListType) and isinstance(t2, types.ListType):
            return t1 == t2
        if isinstance(t1, types.StringTypes):
            if isinstance(t2, Tree):
                t2s = t2.toString()
            elif isinstance(t2, types.ListType):
                t2s = [x.toString() for x in t2]
                t2s = "[%s]" % ", ".join(t2s)
            else:
                print ("in ListTree.equals. 2nd operand '%s' "
                       "has unexpected type '%s'" % (t2, type(t2)))
                raise Exception, ("invalid type for 2nd operand to "
                                  "ListTree.equals: %s" % str(type(t2)))
            if t1 == t2s:
                return True
            if t1 == ListTree.removeTags(t2s):
                return True
            return False
        if t1 == t2:
            return True
        return False
    equals = staticmethod(equals)

    def parseTree(self, tree):
        return tree

    def parse(aString):
        if aString.find("<ul>") == -1:
            return ListTree(aString)
        parsed = Parse(aString, ("ul", "li"))
        ListTree._parse(parsed)
        result = ListTree._parse2(parsed)
        return result
    parse = staticmethod(parse)

    def _parse(node):
        while node is not None:
            print "in _parse. node.body: '%s'" % node.body
            body = node.body
            if body.find("<ul>") > -1:
                nextLevel = Parse(body, ("ul", "li"))
                node.parts = nextLevel
                node.body = ""
                ListTree._parse(node.parts)
            node = node.more
    _parse = staticmethod(_parse)

    def _parse2(node): # returns listTree node
        # we should have a <ul> node at this point
        children = []
        chNode = node.parts
        while chNode is not None:
            if chNode.parts is None:
                children.append(ListTree(chNode.body))
            else:
                children.append(ListTree._parse2(chNode.parts))
            chNode = chNode.more
        result = ListTree(node.leader, children)
        return result
    _parse2 = staticmethod(_parse2)

    def removeTags(aString):
        result = []
        start = 0
        while True:
            nextLT = aString.find("<", start)
            if nextLT > -1:
                result.append(aString[start:nextLT])
            else:
                result.append(aString[start:])
                break
            nextGT = aString.find(">", nextLT+1)
            if nextGT == -1:
                break
            start = nextGT + 1
        return "".join(result)
    removeTags = staticmethod(removeTags)

    def toTree(self):
        return self

"""
    # since I'm not quite sure what this does, I'm going to ignore it
    # until the tests get here!
    public String prune(int max) {
        int count = nodeCount(1);
        for (int depth = 2; ; depth++) {
            int nextCount = nodeCount(depth);
            if (nextCount > max || nextCount == count)
                return toString(depth-1);
            count = nextCount;
        }
    }
    private int nodeCount(int depth) {
        if (depth <= 1 || children.isEmpty())
            return 1;
        int count = 1;
        for (Iterator it = children.iterator(); it.hasNext(); )
            count += ((ListTree)it.next()).nodeCount(depth-1);
        return count;
    }
}
 """

class TreeTypeAdapter(TreeInterface): # extends MetaTypeAdapter {
    fitAdapterProtocol = "RawString"
    def __init__(self):
        pass
    
    def parse(self, aString):
        return ListTree.parse(aString)

    def toString(self, obj):
        if obj is None:
            return "null"
        if hasattr(obj, "toString"):
            return obj.toString()
        if isinstance(obj, types.ListType):
            result = [x.toString() for x in obj]
            result = "[%s]" % ", ".join(result)
            return result
        return str(obj)

    def equals(self, aString, b):
        if isinstance(aString, ListTree):
            return ListTree.equals(aString, b)
        if isinstance(aString, types.StringTypes):
            return ListTree.equals(self.parse(aString), b)
        return False
