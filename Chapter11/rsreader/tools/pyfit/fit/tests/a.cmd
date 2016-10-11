@echo off
rem acceptance test command router.
set fittest=""
if "%1" == "?" goto echoDoc
if "%1" == "list" goto listit
if "%1" == "all" goto runall
if "%1" == "all2" goto runall2
if "%1" == "allp" goto runPython
if "%1" == "allp2" goto runPython2
if "%1" == "spec1.1" goto spec1_1Test

rem the following tests are all in fat.Documents
if "%1" == "ar" set fittest="arithmetic.html"
if "%1" == "calc" set fittest="CalculatorExample.html"
if "%1" == "cell" set fittest="CellHandlers.htm"
if "%1" == "parm" set fittest="ParmTest.htm"
if "%1" == "pe" set fittest="ParseExit.htm"
if "%1" == "bc" set fittest="BinaryChop.html"
if "%1" == "ex" set fittest="ExampleTests.html"
if "%1" == "spec" set fittest="FitSpecification.html"
if "%1" == "music" set fittest="MusicExample.html"
if "%1" == "mp" set fittest="MusicPlayer.html"
if "%1" == "mp2" set fittest="MusicPlayer2.html"
if "%1" == "s" set fittest="SimpleExample.html"
if "%1" == "u8" set fittest="UTF8Example.html"
if "%1" == "sym" set fittest="TestSaveAndRecallSymbol.html"
if "%1" == "sym2" set fittest="SymbolTest.htm"
if "%1" == "parse" set fittest="parse1_0.html"
if "%1" == "fixtures" set fittest="fixtures1_0.html"
if not %fittest% == "" goto filecmd

rem the following tests are in fit.AccTests
if "%1" == "fex" set fittest="FloatingPointExtensions.htm"
if "%1" == "ch" set fittest="CellHandlers.htm"
if "%1" == "foo" set fittest="foo.htm"
if not %fittest% == "" goto fitAccTest

echo Can't understand %1
goto skip

:echoDoc
echo Acceptance test router for Python FIT
echo a xxx runs test xxx
echo -- all -- tests in the fat directory
echo -- all2 -- passing tests in the fat directory
echo -- allp -- Python FIT specific tests
echo -- spec1.1 -- tests for FIT specification 1.1 compliance
echo ---- Parse and Annotation are expected to pass, Fixture is not expected to pass.
echo ---- It must be inspected manually to see if the required tests have passed.

:listit
type a.cmd
goto skip

:filecmd
cd ..
python FileRunner.py fat/Documents/%fittest% fat/Reports/%fittest% > tests/testout/%fittest%.txt
cd tests
goto skip

:fitAccTest
cd ..
python FileRunner.py fit/AccTests/%fittest% fit/Results/%fittest% > fit/Results/%fittest%.txt
cd tests
goto skip

:runall2
cd ..
python FolderRunner.py fat/Documents fat/Reports > tests/testout/allAcceptanceTests.txt
cd tests
goto skip

:runall
cd ..
python FileRunner.py fat/Documents/AllTests.txt fat/Reports > fat/Reports/allTests.txt
cd tests
goto skip

:runPython
cd ..
python FolderRunner.py -v fit/AccTests fit/Results > fit/Results/AllTests.txt
cd tests
goto skip

:runPython2
cd ..
python FileRunner.py fit/AccTests/AllTests.txt fit/Results > fit/Results/AllTests.txt
cd tests
goto skip

:spec1_1Test
cd ..
python FolderRunner.py +e -q yt fat/Fit1_1Tests fat/Reports fat/Fit1_1Tests/FixtureRenames.txt > fat/Reports/Fit1_1Tests.txt
cd tests



:skip