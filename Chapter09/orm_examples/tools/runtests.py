import nose

"""Runs nose with the --with-isolation option

This script exists becase nose doesn't recognize the
--with-isolation option when running from './setup.py test'.

This option is necessary to clear out SQLObject's cache
when testing multiple schema versions
"""

nose.main(argv=['--verbose', '3', '--with-isolation'])
