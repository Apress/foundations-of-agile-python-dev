@echo off

rem unit test command router.
set fittest=""
if "%1" == "?" goto listit
if "%1" == "all" set fittest="AllTests"
if "%1" == "af" set fittest="ActionFixtureTest"
if "%1" == "c" set fittest="CellHandlerTest"
if "%1" == "col" set fittest="ColumnFixtureTest"
if "%1" == "cftf" set fittest="ColumnFixtureTestFixtureTest"
if "%1" == "check" set fittest="CheckTests"
if "%1" == "fex" set fittest="FitExceptionTest"
if "%1" == "fl" set fittest="FixtureLoaderTest"
if "%1" == "fwk" set fittest="FrameworkTest"
if "%1" == "fx" set fittest="FixtureTest"
if "%1" == "i" set fittest="TestImport"
if "%1" == "misc" set fittest="MiscTest"
if "%1" == "opt" set fittest="OptionsTest"
if "%1" == "p" set fittest="ParseTest"
if "%1" == "pro" set fittest="taProtocolTest"
if "%1" == "row" set fittest="RowFixtureTest"
if "%1" == "ri" set fittest="RunnerImplementationTest"
if "%1" == "ta" set fittest="TypeAdapterTest"
if "%1" == "var" set fittest="VariationsTest"
if not %fittest% == "" goto testcmd

if "%1" == "mp" set fittest="MusicPlayerTest"
if "%1" == "mp2" set fittest="MusicPlayer2Test"
if not %fittest% == "" goto egTest


echo Can't understand %1
goto skip

:listit
type t.cmd
goto skip

:testcmd
cd ..
python tests/%fittest%.py > tests/testout/%fittest%.txt
cd tests

goto skip

:egTest
cd ..
python eg/%fittest%.py > tests/testout/%fittest%.txt
cd tests


:skip