All of the source projects in this zip file can be worked with from
the command line, or they can be imported into Eclipse.  (For
information on starting with Eclipse, please see Chapter 2.)

You can import these projects into Eclipse using the following procedure:
Select General -> 'Import Existing Projects into Workspace' from the
Import dialog.  Choose this directory as the root directory.  You
should see a list of projects (chapter03, chapter04, ..., chapter11).
Clicking Finish will import them.

Depending upon what modules have been installed, you may need to go
to the root of each package and run the command 'python ./setup.py
install' as discussed in Chapter 4.  Setuptools will import the
packages needed for each project.

Each chapter's directory contains a README.txt file.  This file contains
more information about the directories in that chapter.

As a note, Chapter 7 as printed contains a fair number of errors.  The
errors are corrected in this zip file, and you will find this chapter
to be much more coherent if you have this code by your side.

The only other differences that I know of are in Chapter 9.  There is
an ommission relating to cascading deletes in SQLAlchemy, and I've
refined some spots in the harness code for SQLObject.  With the 
exception of the cascading delete test case all other examples are
correct.

