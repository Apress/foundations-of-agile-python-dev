import os
import sys

import feedparser
from nose.tools import assert_equals
from pmock import eq, Mock, once, same, return_value

from shared_data import *
from rsreader.application import AggregateFeed, FeedEntry, FeedWriter, RSReader

'''Test the application class RSReader'''

def test_listing_from_feed():
    computed_items = RSReader().listing_from_feed(xkcd_feed)
    assert_equals(xkcd_output, computed_items)

def test_listing_from_item():
    computed_line = RSReader().listing_from_item(xkcd_feed, xkcd_items[0])
    assert_equals(xkcd_listings[0], computed_line)

def test_feed_from_url():
    url = "http://www.xkcd.com/rss.xml"
    def parse_stub(url): # define stub
        return xkcd_feed
    real_parse = feedparser.parse # save real value
    feedparser.parse = parse_stub # attach stub
    try:
        assert_equals(xkcd_feed, RSReader().feed_from_url(url))
    finally:
        feedparser.parse = real_parse # restore real value

def test_combine_feeds():
    """Should combine feeds into a list of FeedEntries"""
    subject = AggregateFeed()
    mock_feeds = [Mock(), Mock()]
    aggregate_feed = Mock()
    aggregate_feed.expects(once()).add_single_feed(same(aggregate_feed),
    same(mock_feeds[0]))
    aggregate_feed.expects(once()).add_single_feed(same(aggregate_feed),
    same(mock_feeds[1]))
    subject.combine_feeds(aggregate_feed, mock_feeds)
    aggregate_feed.verify()

def test_add_singled_feed():
    """Should add a single xkcd_feed to a set of feeds"""
    entries = [Mock(), Mock()]
    xkcd_feed = {'entries': entries}
    aggregate_feed = Mock()
    aggregate_feed.expects(once()).create_entry(same(aggregate_feed),
                                                same(xkcd_feed), same(entries[0]))
    aggregate_feed.expects(once()).create_entry(same(aggregate_feed),
                                                same(xkcd_feed), same(entries[1]))
    AggregateFeed().add_single_feed(aggregate_feed, xkcd_feed)
    aggregate_feed.verify()

def test_create_entry():
    """Create a xkcd_feed item from a xkcd_feed and a xkcd_feed entry"""
    agg_feed = AggregateFeed()
    agg_feed.feed_factory = Mock()
    (aggregate_feed, xkcd_feed, entry, converted) = (Mock(), Mock(), Mock(), Mock())
    agg_feed.feed_factory.expects(once()).from_parsed_feed(same(xkcd_feed),
                                                           same(entry)).will(return_value(converted))
    aggregate_feed.expects(once()).add(same(converted))
    agg_feed.create_entry(aggregate_feed, xkcd_feed, entry)
    aggregate_feed.verify()
    
def test_aggregate_feed_creates_factory():
    """Verify that the AggregatedFed object creates a factory
    when instantiated"""
    assert_equals(FeedEntry, AggregateFeed().feed_factory)
    
def test_add():
    """Add a xkcd_feed entry to the aggregate"""
    entry = Mock()
    subject = AggregateFeed()
    subject.add(entry)
    assert_equals(set([entry]), subject.entries)
    
def test_feed_entry_from_parsed_feed():
    """Factory method to create a new xkcd_feed entry from a parsed xkcd_feed"""
    feed_entry = FeedEntry.from_parsed_feed(xkcd_feed, xkcd_items[0])
    assert_equals(xkcd_items[0]['date'], feed_entry.date)
    assert_equals(xkcd_items[0]['date_parsed'], feed_entry.date_parsed)
    assert_equals(xkcd_items[0]['title'], feed_entry.title)
    assert_equals(xkcd_feed['feed']['title'], feed_entry.feed_title)
    
def test_feed_entry_listing():
    """Should produce a correctly formatted listing from a feed entry"""
    entry = FeedEntry.from_parsed_feed(xkcd_feed, xkcd_items[0])
    assert_equals(xkcd_listings[0], entry.listing())

def test_get_feeds_from_urls():
    """Should get a feed for every URL"""
    urls = [Mock(), Mock()]
    feeds = [Mock(), Mock()]
    subject = AggregateFeed()
    subject.feedparser = Mock()
    subject.feedparser.expects(once()).parse(same(urls[0])).will(
            return_value(feeds[0]))
    subject.feedparser.expects(once()).parse(same(urls[1])).will(
            return_value(feeds[1]))
    returned_feeds = subject.feeds_from_urls(urls)
    assert_equals(feeds, returned_feeds)
    subject.feedparser.verify()
    
def test_aggregate_feed_initializes_feed_parser():
    """Ensure AggregateFeed initializes dependency on feedparser"""
    assert_equals(feedparser, AggregateFeed().feedparser)

def test_from_urls():
    """Should get feeds from URLs and combine them"""
    urls = [Mock(), Mock()]
    feeds = [Mock(), Mock()]
    subject = AggregateFeed()
    aggregate_feed = Mock()
    subject.feedparser = Mock()
    #
    subject.feedparser.expects(once()).parse(same(urls[0])).will(
        return_value(feeds[0]))
    aggregate_feed.expects(once()).\
        add_single_feed(same(aggregate_feed), same(feeds[0]))
    #
    subject.feedparser.expects(once()).parse(same(urls[1])).will(
        return_value(feeds[1]))
    aggregate_feed.expects(once()).\
        add_single_feed(same(aggregate_feed), same(feeds[1]))
    #
    subject.from_urls(aggregate_feed, urls)
    subject.feedparser.verify()
    aggregate_feed.verify()

def test_aggregate_feed_listing_should_be_sorted():
    """Should produce a sorted listing of feed entries."""
    unsorted = [FeedEntry.from_parsed_feed(xkcd_feed, xkcd_items[1]),
    FeedEntry.from_parsed_feed(xkcd_feed, xkcd_items[0])]
    aggregate_feed = AggregateFeed()
    aggregate_feed.entries = unsorted
    aggregate_listing = FeedWriter().entry_listings(aggregate_feed)
    assert_equals(xkcd_output, aggregate_listing)
    
def test_print_entry_listings():
    """Verify that a listing was printed"""
    subject = FeedWriter()
    (feed_writer, aggregate_feed, listings) = (Mock(), Mock(), Mock())
    subject.stdout = Mock()
    aggregate_feed.expects(once()).is_empty().will(
        return_value(False))
    feed_writer.expects(once()).entry_listings(same(aggregate_feed)).\
        will(return_value(listings))
    subject.stdout.expects(once()).write(same(listings))
    subject.stdout.expects(once()).write(eq(os.linesep))
    subject.print_entry_listings(feed_writer, aggregate_feed)
    feed_writer.verify()
    subject.stdout.verify()

def test_feed_writer_intializes_stdout():
    """Ensure that feed writer initializes stdout from sys.stdout"""
    assert_equals(sys.stdout, FeedWriter().stdout)

def test_feed_writer_prints_nothing_with_an_empty_feed():
    """Empty aggregate feed should print nothing"""
    subject = FeedWriter()
    (feed_writer, aggregate_feed) = (Mock(), Mock())
    subject.stdout = Mock()
    aggregate_feed.expects(once()).is_empty().will(return_value(True))
    subject.print_entry_listings(feed_writer, aggregate_feed)
    aggregate_feed.verify()
    subject.stdout.verify()
    
def test_is_empty():
    """Unsure is empty works"""
    aggregate_feed = AggregateFeed()
    assert aggregate_feed.is_empty()
    aggregate_feed.add("foo")
    assert not aggregate_feed.is_empty()

def test_main():
    """"Main should create a feed and print results"""
    args = ["unused_program_name", "x1"]
    reader = RSReader()
    reader.aggregate_feed = Mock()
    reader.feed_writer = Mock()
    reader.aggregate_feed.expects(once()).from_urls(same(reader.aggregate_feed),
        eq(["x1"]))
    reader.feed_writer.expects(once()).print_entry_listings(same(reader.feed_writer), \
        same(reader.aggregate_feed))
    reader.main(args)
    reader.aggregate_feed.verify()
    reader.feed_writer.verify()
    
def test_rsreader_initializes_dependencies():
    """RSReader should initialize dependencies"""
    reader = RSReader()
    assert isinstance(reader.aggregate_feed, AggregateFeed)
    assert isinstance(reader.feed_writer, FeedWriter)

test_from_urls()