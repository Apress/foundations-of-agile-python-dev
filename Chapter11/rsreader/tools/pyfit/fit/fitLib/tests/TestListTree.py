# Unit tests for ListTree support module from FitLibrary
# Copyright 2004 Rick Mugridge University of Auckland, NZ
# Released under the terms of the GNU General Public License version 2 or later
# Translation to Python copyright 2005 John H. Roth Jr.

import unittest
from fitLib.ListTree import ListTree

try:
    False
except:
    True = 1
    False = 0

def makeListTreeTest():
    theSuite = unittest.makeSuite(Test_ListTree, 'test')
#    theSuite.addTest(unittest.makeSuite(Test_FooBar, 'Test'))
    return theSuite

class Test_ListTree(unittest.TestCase):
    topTree = None
    tree = None
    toplessTree = None
    
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        self.topTree = ListTree("top")
        self.tree = ListTree("tree", [ListTree("a"),
                                      ListTree("b", [ListTree("c")])])
        self.toplessTree = ListTree("", [ListTree("a"), ListTree("b")])

    def testEqualsSameOne(self):
        self.treesEqual(self.topTree, self.topTree)

    def testEqualsSimilarOne(self):
        self.treesEqual(self.topTree, ListTree("top"))

    def testNotEqualsSimilarOne(self):
        self.treesUnEqual(self.topTree, ListTree("bottom"))
        
    def testTopToString(self):
        print self.topTree.toString()
        assert "top" == self.topTree.toString()

    def testToplessTreeToString(self):
        assert ("<ul><li>a</li><li>b</li></ul>" ==
                self.toplessTree.toString())

    def testEqualsSameTree(self):
        self.treesEqual(self.tree, self.tree)

    def testEqualsSimilarTree(self):
        tree2 = ListTree("tree", [ListTree("a"),
                                  ListTree("b", [ListTree("c")])])
        self.treesEqual(self.tree, tree2)

    def testNotEqualsTop(self):
        self.treesUnEqual(self.tree, self.topTree)
        self.treesUnEqual(self.topTree, self.toplessTree)
        
    def testNotEqualsSimilarShapedTree(self):
        tree2 = ListTree("tree", [ListTree("a"),
                                   ListTree("b", [ListTree("C")])])
        self.treesUnEqual(self.tree, tree2)

        
    def testNotEqualsDifferentShapedTree(self):
        tree2 = ListTree("tree", [ListTree("a", [ListTree("c")]),
                                           ListTree("b")])
        self.treesUnEqual(self.tree, tree2)
        self.treesUnEqual(self.tree, self.toplessTree)

    def testTreeToString(self):
        tree = "tree<ul><li>a</li><li>b<ul><li>c</li></ul></li></ul>"
        result = self.tree.toString()
        print tree
        print result
        assert tree == self.tree.toString()

    def testParseTop(self):
        assert self.topTree, ListTree.parse("top")

    def testParseTree1(self):
        text = "tree<ul><li>a</li></ul>"
        parsed = ListTree.parse(text).toString()
        print text
        print parsed
        assert text == parsed

    def testParseTree(self):
        self.assertParsed(
            "tree<ul><li>a</li><li>b<ul><li>c</li></ul></li></ul>")

    def testParseToplessTree(self):
        self.assertParsed(
            "<ul><li>a</li><li>b<ul><li>c</li></ul></li></ul>")

    def testParseTags0(self):
        self.assertParsed("<i>a</i>")

    def testParseSpace(self):
        assert "a" == ListTree.parse("<i>a  </i>").text

    def testParseTags1(self):
        self.assertParsed("tree<ul><li><i>a</i></li></ul>")

    def testParseTags2(self):
        self.assertParsed("tree<ul><li>a<i>b</i><b>c</b></li></ul>")

    def testEqualsSimilarWithTags(self):
        self.treesEqual(self.topTree, ListTree("<i>top</i>"))

    def testTopText(self):
        assert "top" == ListTree("top").textToString()

    def testToplessTreeText(self):
        text = "<ul><li>a</li><li>b</li></ul>"
        result = self.toplessTree.textToString()
        assert text == result

    def testTopTextWithTags(self):
        assert "top" == ListTree("<i><b>top</b></i>").textToString()

    def testTreeText(self):
        assert ("tree<ul><li>a</li><li>b<ul><li>c</li></ul></li></ul>" ==
                self.tree.textToString())

    def testTreeTextWithTags(self):
        s = "tree<ul><li>a<i>b</i><b>c</b></li></ul>"
        assert "tree<ul><li>abc</li></ul>" == ListTree.parse(s).textToString()
        
    def testParseTreeNoCloseLi(self):
        try:
            ListTree.parse("tree<ul><li>a<li>b<ul><li>c</ul></ul>")
        except Exception:
            pass
        else:
            self.fail("Doesn't handle lists with </li> missing.")

    def assertParsed(self, s):
        print s
        result = ListTree.parse(s).toString()
        print result
        assert s == result

    def treesEqual(self, t1, t2):
        assert t1 == t2
        assert t2 == t1
        assert ListTree.equals(t1, t2)
        assert ListTree.equals(t2, t1)


    def treesUnEqual(self, t1, t2):
        assert t1 != t2
        assert t2 != t1
        assert not ListTree.equals(t1, t2)
        assert not ListTree.equals(t2, t1)


if __name__ == '__main__':
    unittest.main(defaultTest='makeListTreeTest')
