# Copyright (c) 2002 Cunningham & Cunningham, Inc.
# Released under the terms of the GNU General Public License version 2 or later.
# Conversion to Python copyright 2004 John H. Roth Jr.

class Money:
    cents = 0

    def __init__(self, s):
        stripped = ""
        for c in s:
            if c.isdigit() or c == '.':
                stripped += c
        self.cents = int(100.0 * float(stripped))

    def __eq__(self, other):
        return self.cents == other.cents

    def __hash__(self):
        return self.cents

    def __str__(self):
        dollars, cents = divmod(self.cents, 100)
        return "%i.%02u" % (dollars, cents)


