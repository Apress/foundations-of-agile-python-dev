@echo off

rem unit test command router.
set fittest=""
if "%1" == "?" goto listit
if "%1" == "all" set fittest="FitServerTest"
rem if "%1" == "fs" set fittest="FitServerTest"
rem if "%1" == "tr" set fittest="TestRunnerTest"
if not %fittest% == "" goto testcmd

echo Can't understand %1
goto skip

:listit
type t.cmd
goto skip

:testcmd
cd ..
python tests/%fittest%.py > tests/testout/%fittest%.txt
cd tests


:skip