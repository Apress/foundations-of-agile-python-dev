This is release 0.8a2 of the Python version of the FIT framework.
0.8a2 is mostly a bug fix release. There is one new feature and
one change that might require a change to existing fixtures.
0.8a1 includes a large number of changes and new features over
the 0.7 series; see the changelog for a summary and the 
documentation set for details.
 
The original FIT framework is by Ward Cunningham (fit.c2.com)
The original port to Python is by Simon Michael.
The base products are copyright by Ward Cunningham (Java version of
FIT), Simon Michael (Python port of an early version of FIT), 
James Shore (current versions of Java FIT) and
Object Mentor (Fitnesse www.fitnesse.org).
FitLibrary was developed and is copyright by Rick Mugridge.
All the rest of the code is copyright 2003-2006 by John Roth.
See the comments at the beginning of each Python module for the
copyright claims that apply to that module.

This package requires Python 2.2.0 or higher to run.

---------------------------------------------------------------

To install:

1. unzip the package into a convenient directory.

2. Locate the directory which contains setup.py. Execute 

python setup.py install

from a command line using this directory as the current directory. 
On successful completion, FIT should be installed in the 
Lib/site-packages directory of your Python installation.

Scripts will have been installed in both the Scripts directory
(/usr/bin for unices) and the fit directory. Use the version 
in the fit directory; the ones in the Scripts directory will
cause a number of strange problems.

At present, text files will not have had their line endings 
fixed, though.

It's also possible to install by copying the directory tree,
beginning with the directory contain FileRunner.py, to anywhere
convenient, and then fixing the first line in the scripts in the
top level directory manually. This will not fix line endings 
on .txt files, and it may not create several empty directories 
needed for tests.

For a minimum installation, you may discard the DocSource, eg,
fat and tests directories. You may also discard everything under
the FitLib directory except the Python modules in the FitLib
directory itself.

If you are going to use FitNesse, see the topic "Using FIT"
in the documentation for the commands needed to invoke tests.

-----------------------------------------------------------------

To uninstall:

Delete the fit directory, the fit.pth file and any scripts
in the Scripts (/usr/bin for unices) directory.

-----------------------------------------------------------------

All code is distributed under the GPL, version 2. See License.txt
in the root directory and the DistDoc directory for a full
copy of the GNU General Public License. All code in
this release is source, there are no compiled executables.

-----------------------------------------------------------------

See the documentation in the Doc directory. The root of the 
documentation is AAStart.htm.
