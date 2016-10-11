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
        """Read argument lists and coordinate aggregates"""
        self.aggregate_feed.from_urls(argv[1:])
        self.feed_writer.print_entry_listings(self.aggregate_feed)


class AggregateFeed(object):
    """Several parsed feeds combined"""

    def __init__(self):
        self.entries = set()

    def is_empty(self):
        """True if empty, False otherwise"""
        return not self.entries
                
    def from_urls(self, feeds):
        """Combine a set of parsed feeds"""
        for f in feeds:
            self.add_single_feed(feedparser.parse(f))

    def add_single_feed(self, feed):
        """Add a single parsed feed"""
        for entry in feed.entries:
            self.create_entry(feed, entry)
            
    def create_entry(self, feed, entry):
        """Add a single entry"""
        self.add(FeedEntry(feed, entry))

    def add(self, entry):
        """Add an entry"""
        self.entries.add(entry)


class FeedEntry(object):
    """Combines elements of a feed and a feed entry.
    Allows multiple feeds to be aggregated without loosing feed specific
    information."""

    def __init__(self, feed, entry):
        self.date = entry['date']
        self.date_parsed = entry['date_parsed']
        self.feed_title = feed['feed']['title']
        self.title = entry['title']

    def listing(self):
        return "%s: %s: %s" % (self.date, self.feed_title, self.title)


class FeedWriter(object):
    """Prints an aggregate feed"""

    def entry_listings(self, aggregate_feed):
        """Produce a sorted listing of an aggregate feed"""
        sorted_entries = sorted(aggregate_feed.entries,
        key=lambda x: x.date_parsed,
        reverse=True)
        return os.linesep.join([x.listing() for x in sorted_entries])

    def print_entry_listings(self, aggregate_feed):
        """Print an entry_listing to sys.stdout"""
        if not aggregate_feed.is_empty():
            entry_listings = self.entry_listings(aggregate_feed)
            sys.stdout.write(entry_listings + os.linesep)