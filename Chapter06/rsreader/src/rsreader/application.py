"""Main entry point for a command line rss reader"""

import sys

def main():
    xkcd_items = \
"""Wed, 05 Dec 2007 05:00:00 -0000: xkcd.com: Python
Mon, 03 Dec 2007 05:00:00 -0000: xkcd.com: Far Away"""
    if sys.argv[1:]:
        print xkcd_items
