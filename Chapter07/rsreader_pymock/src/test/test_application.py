import os
import sys

import feedparser
from nose.tools import assert_equals
from pymock import dummy, method, mock, override, replay, returns, use_pymock, verify


from shared_data import *
import rsreader
from rsreader.application import AggregateFeed, FeedEntry, FeedWriter, RSReader

'''Test the application class RSReader'''

@use_pymock
def test_from_urls():
    """Should retrieve feeds and add them to the aggregate"""
    urls = [dummy(), dummy()]
    feeds = [dummy(), dummy()]
    subject = AggregateFeed()
    #
    override(feedparser, 'parse').expects(urls[0]).returns(feeds[0])
    override(subject, 'add_single_feed').expects(feeds[0])
    #
    override(feedparser, 'parse').expects(urls[1]).returns(feeds[1])
    override(subject, 'add_single_feed').expects(feeds[1])
    #
    replay()
    subject.from_urls(urls)
    verify()

@use_pymock
def test_add_single_feed():
    """Should create a new entry for each entry in the feed"""
    subject = AggregateFeed()
    entries = [dummy(), dummy()]
    feed = mock()
    feed.entries; returns(entries)
    override(subject, 'create_entry').expects(feed, entries[0])
    override(subject, 'create_entry').expects(feed, entries[1])
    replay()
    subject.add_single_feed(feed)
    verify()

@use_pymock
def test_create_entry():
    """Should create an entry and add it to the collection"""
    subject = AggregateFeed()
    (feed, entry) = (dummy(), dummy())
    new_entry = dummy()
    override(rsreader.application, 'FeedEntry')\
    .expects(feed, entry)\
    .returns(new_entry)
    override(subject, 'add').expects(new_entry)
    replay()
    subject.create_entry(feed, entry)
    verify()
    
@use_pymock
def test_add():
    """Add an a feed entry to the aggregate"""
    entry = mock()
    subject = AggregateFeed()
    subject.add(entry)
    assert_equals(set([entry]), subject.entries)

def test_entries_is_always_defined():
    """The entries set should always be defined"""
    assert_equals(set(), AggregateFeed().entries)
    
def test_feed_entry_constructor():
    """Verify settings extracted from feed and entry"""
    subject = FeedEntry(xkcd_feed, xkcd_items[0])
    assert_equals(xkcd_items[0]['date'], subject.date)
    assert_equals(xkcd_items[0]['date_parsed'], subject.date_parsed)
    assert_equals(xkcd_items[0]['title'], subject.title)
    assert_equals(xkcd_feed['feed']['title'], subject.feed_title)
    
def test_feed_entry_listing():
    """Should produce a correctly formatted listing form a feed item"""
    subject = FeedEntry(xkcd_feed, xkcd_items[0])
    assert_equals(xkcd_listings[0], subject.listing())

def test_aggregate_feed_listing_should_be_sorted():
    """Should produce a sorted listing of feed entries."""
    unsorted_entries = [FeedEntry(xkcd_feed, xkcd_items[1]),
    FeedEntry(xkcd_feed, xkcd_items[0])]
    aggregate_feed = AggregateFeed()
    aggregate_feed.entries = unsorted_entries
    assert_equals(xkcd_output, FeedWriter().entry_listings(aggregate_feed))

@use_pymock
def test_print_agg_feed_listing_is_printed():
    """Should print listing of feed entries"""
    unsorted_entries = [FeedEntry(xkcd_feed, xkcd_items[1]),
    FeedEntry(xkcd_feed, xkcd_items[0])]
    aggregate_feed = AggregateFeed()
    aggregate_feed.entries = unsorted_entries
    override(sys, 'stdout')
    method(sys.stdout, 'write').expects(xkcd_output + os.linesep)
    replay()
    FeedWriter().print_entry_listings(aggregate_feed)
    verify()

@use_pymock
def test_print_entry_listing_does_nothing_with_an_empty_aggregate():
    """Ensure that nothing is printed with an empty aggregate"""
    empty_aggregate_feed = AggregateFeed()
    override(sys, 'stdout')
    replay()
    FeedWriter().print_entry_listings(empty_aggregate_feed)
    verify()
    
def test_is_empty():
    """Ensure that is_empty reports emptiness as expected"""
    empty_aggregate_feed = AggregateFeed()
    non_empty_aggregate_feed = AggregateFeed()
    non_empty_aggregate_feed.add("foo")
    assert empty_aggregate_feed.is_empty() is True
    assert non_empty_aggregate_feed.is_empty() is False

@use_pymock
def test_main():
    """Hook components together"""
    args = ["unused_program_name", "u1"]
    subject = RSReader()
    subject.aggregate_feed = mock()
    subject.feed_writer = mock()
    method(subject.aggregate_feed, 'from_urls').expects(["u1"])
    method(subject.feed_writer, 'print_entry_listings').\
    expects(subject.aggregate_feed)
    replay()
    subject.main(args)
    verify()
    
def test_rsreader_dependency_initialization():
    """Ensure that dependencies are correctly initialized"""
    assert isinstance(RSReader().aggregate_feed, AggregateFeed)
    assert isinstance(RSReader().feed_writer, FeedWriter)