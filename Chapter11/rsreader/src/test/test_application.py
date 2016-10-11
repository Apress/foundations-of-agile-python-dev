import os
from nose.tools import assert_equals

import feedparser

from shared_data import *
from rsreader.application import RSReader

'''Test the application class RSReader'''


items = [{'date': "Wed, 05 Dec 2007 05:00:00 -0000",
          'title': "Python"},
          {'date': "Mon, 03 Dec 2007 05:00:00 -0000",
           'title': "Far Away"}]
feed = {'feed': {'title': "xkcd.com"}, 'entries': items}

def test_listing_from_feed():
    computed_items = RSReader().listing_from_feed(feed)
    assert_equals(xkcd_output, computed_items)

def test_listing_from_item():
    computed_line = RSReader().listing_from_item(feed, items[0])
    assert_equals(expected_items[0], computed_line)

def test_feed_from_url():
    url = "http://www.xkcd.com/rss.xml"
    def parse_stub(url): # define stub
        return feed
    real_parse = feedparser.parse # save real value
    feedparser.parse = parse_stub # attach stub
    try:
        assert_equals(feed, RSReader().feed_from_url(url))
    finally:
        feedparser.parse = real_parse # restore real value
