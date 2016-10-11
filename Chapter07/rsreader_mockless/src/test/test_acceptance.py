import StringIO
import sys
from unittest import TestCase

from test.shared_data import *
from rsreader.application import main

module = sys.modules[__name__]
this_dir = os.path.dirname(os.path.abspath(module.__file__))

xkcd_rss_xml = os.path.join(this_dir, 'data', 'xkcd.rss.xml')

class AcceptanceTests(TestCase):

    def setUp(self):
        self.old_value_of_stdout = sys.stdout
        sys.stdout = StringIO.StringIO()
        self.old_value_of_argv = sys.argv

    def tearDown(self):
        sys.stdout = self.old_value_of_stdout
        sys.argv = self.old_value_of_argv

    def test_should_get_one_URL_and_print_output(self):
        sys.argv = ["unused_prog_name", xkcd_rss_xml]
        main()
        self.assertStdoutEquals(xkcd_output + os.linesep)

    def test_no_urls_should_print_nothing(self):
        sys.argv = ["unused_prog_name"]
        main()
        self.assertStdoutEquals("")

    def test_many_urls_should_print_first_results(self):
        sys.argv = ["unused_prog_name", xkcd_rss_xml, "excess"]
        main()
        self.assertStdoutEquals(xkcd_output + os.linesep)

    def assertStdoutEquals(self, expected_output):
        self.assertEquals(expected_output, sys.stdout.getvalue())