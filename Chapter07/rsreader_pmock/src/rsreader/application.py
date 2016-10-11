"""Main entry point for a command line rss reader"""

import os
import sys

import feedparser

def main():
    RSReader().main(sys.argv)

class RSReader(object):

    def __init__(self):
        self.aggregate_feed = AggregateFeed()
        self.feed_writer = FeedWriter()

    def main(self, argv):
        self.aggregate_feed.from_urls(self.aggregate_feed, argv[1:])
        self.feed_writer.print_entry_listings(self.feed_writer, self.aggregate_feed)

    def listing_from_item(self, feed, item):
        subst = (item['date'], feed['feed']['title'], item['title'])
        return "%s: %s: %s" % subst

    def listing_from_feed(self, feed):
        item_listings = [self.listing_from_item(feed, x) for x in feed['entries']]
        return os.linesep.join(item_listings)
    
    def feed_from_url(self, url):
        return feedparser.parse(url)


class AggregateFeed(object):
    """Aggregates several feeds"""

    def __init__(self):
        self.entries = set()
        self.feed_factory = FeedEntry
        self.feedparser = feedparser
        
    def combine_feeds(self, aggregate_feed, feeds):
        for x in feeds:
            aggregate_feed.add_single_feed(aggregate_feed, x)

    def add_single_feed(self, aggregate_feed, feed):
        for e in feed['entries']:
            aggregate_feed.create_entry(aggregate_feed, feed, e)

    def create_entry(self, feed_aggregator, feed, entry):
        feed_aggregator.add(self.feed_factory.from_parsed_feed(feed, entry))

    def add(self, entry):
        self.entries.add(entry)

    def feeds_from_urls(self, urls):
        """Get feeds from URLs"""
        return [self.feedparser.parse(url) for url in urls]
        
    def from_urls(self, aggregate_feed, urls):
        """Produce aggregated feeds from URLs"""
        for x in urls:
            aggregate_feed.add_single_feed(aggregate_feed, self.feedparser.parse(x))

    def is_empty(self):
        """True if set is empty, and False otherwise"""
        return not self.entries


class FeedEntry(object):
    """Combines elements of a feed and a feed entry.
    Allows multiple feeds to be aggregated without loosing
    feed specific information."""

    @classmethod
    def from_parsed_feed(cls, feed, entry):
        """Factory method producing a new object from an existing feed."""
        feed_entry = FeedEntry()
        feed_entry.date = entry['date']
        feed_entry.date_parsed = entry['date_parsed']
        feed_entry.feed_title = feed['feed']['title']
        feed_entry.title = entry['title']
        return feed_entry
    
    def listing(self):
        return "%s: %s: %s" % (self.date, self.feed_title, self.title)
    

class FeedWriter(object):
    """Prints an aggregate feed"""

    def __init__(self):
        self.stdout = sys.stdout    

    def entry_listings(self, aggregate_feed):
        """Produce a sorted listing of an aggregate feed"""
        sorted_entries = sorted(aggregate_feed.entries,
            key=lambda x: x.date_parsed,
            reverse=True)
        return os.linesep.join([x.listing() for x in sorted_entries])

    def print_entry_listings(self, feed_writer, aggregate_feed):
        """Print listing"""
        if not aggregate_feed.is_empty():
            self.stdout.write(feed_writer.entry_listings(aggregate_feed))
            self.stdout.write(os.linesep)

