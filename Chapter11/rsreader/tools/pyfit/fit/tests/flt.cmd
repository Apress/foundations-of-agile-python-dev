@echo off

rem Fit Library unit test command router.

set fittest=""
if "%1" == "?" goto listit
if "%1" == "all" set fittest="AllTests"
if "%1" == "calc" set fittest="CalculateFixtureTest"
if "%1" == "do" set fittest="DoFixtureTest"
if "%1" == "du" set fittest="TestDisplayUtility"
if "%1" == "ecc" set fittest="ExtendedCamelCaseTest"
if "%1" == "ff" set fittest="FixtureFixtureTest"
if "%1" == "fff" set fittest="FlowFixtureFixtureTest"
if "%1" == "pu" set fittest="TestParseUtility"
if "%1" == "tree" set fittest="TestListTree"
if not %fittest% == "" goto testcmd

echo Can't understand %1
goto skip

:listit
type t.cmd
goto skip

:testcmd
python ../fitLib/tests/%fittest%.py > testout\%fittest%.txt

:skip