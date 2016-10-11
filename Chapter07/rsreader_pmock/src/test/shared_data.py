from time import mktime
import os

xkcd_listings = [
    "Wed, 05 Dec 2007 05:00:00 -0000: xkcd.com: Python",
    "Mon, 03 Dec 2007 05:00:00 -0000: xkcd.com: Far Away""",
]
xkcd_output = os.linesep.join(xkcd_listings)

xkcd_items = [{'date': "Wed, 05 Dec 2007 05:00:00 -0000",
        'date_parsed': mktime((2007, 12, 5, 5, 0, 0, 2, 0, 0)),
        'title': "Python"},
    {'date': "Mon, 03 Dec 2007 05:00:00 -0000",
        'date_parsed': mktime((2007, 12, 3, 5, 0, 0, 2, 0, 0)),
        'title': "Far Away"}]

xkcd_feed = {'feed': {'title': "xkcd.com"}, 'entries': xkcd_items}
