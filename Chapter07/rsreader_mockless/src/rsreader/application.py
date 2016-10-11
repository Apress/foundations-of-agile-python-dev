"""Main entry point for a command line rss reader"""

import os
import sys

import feedparser

def main():
    RSReader().main(sys.argv)

class RSReader(object):

    xkcd_items = \
"""Wed, 05 Dec 2007 05:00:00 -0000: xkcd.com: Python
Mon, 03 Dec 2007 05:00:00 -0000: xkcd.com: Far Away"""

    def main(self, argv):
        if argv[1:]:
            url = argv[1]
            print self.listing_from_feed(self.feed_from_url(url))            

    def listing_from_item(self, feed, item):
        subst = (item['date'], feed['feed']['title'], item['title'])
        return "%s: %s: %s" % subst

    def listing_from_feed(self, feed):
        item_listings = [self.listing_from_item(feed, x) for x in feed['entries']]
        return os.linesep.join(item_listings)
    
    def feed_from_url(self, url):
        return feedparser.parse(url)
