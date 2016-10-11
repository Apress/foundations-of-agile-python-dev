@echo off
rem Test Runner tests
rem Fitnesse must be up for these tests!

set fittest=""
if "%1" == "?" goto listit
rem if "%1" == "all" set fittest="AllTests"
if "%1" == "c1" set fittest=SuiteColumnFixtureSpec.TestSaveAndRecallSymbol
if "%1" == "row" set fittest=SuiteRowFixtureSpec
if not %fittest% == "" goto testcmd

if "%1" == "c1f" set fittest=SuiteColumnFixtureSpec.TestSaveAndRecallSymbol
if not %fittest% == "" goto testcmdf

if "%1" == "fl" set fittest=FitSpecifications.FixtureSpecifications
if not %fittest% == "" goto testfl
if "%1" == "fl3" set fittest=FitSpecifications.FixtureSpecifications
if not %fittest% == "" goto testfl3
if "%1" == "fl4" set fittest=FitSpecifications.FixtureSpecifications
if not %fittest% == "" goto testfl4


if "%1" == "dof" set fittest=SpecifyDoFixtureFlow
if not %fittest% == "" goto testfl2

if "%1" == "dot" set fittest=SpecifyGraphics
if not %fittest% == "" goto testfl5



echo Can't understand %1
goto skip

:listit
type t.cmd
goto skip

:testcmd
cd ..
python TestRunner.py +vrh -o fat/Reports localhost 80 FitNesse.SuiteAcceptanceTests.PythonSupport.PythonFixtureTests.%fittest%
cd tests
goto skip

:testcmdf
cd ..
python TestRunner.py +vfrh -o fat/Reports localhost 80 FitNesse.SuiteAcceptanceTests.PythonSupport.PythonFixtureTests.%fittest%
cd tests
goto skip

:testfl
cd ../fitLib
python ../TestRunner.py +vfrhx +o tests/Results +p FixtureRenames.txt localhost 80 %fittest% > tests/Results/allTests.txt
cd ../tests

goto skip

:testfl2
cd ../fitLib
python ../TestRunner.py +vfrhx -o tests/Results/%fittest% +p FixtureRenames.txt localhost 80 FitSpecifications.FixtureSpecifications.%fittest% > tests/Results/allTests.txt
cd ../tests
goto skip

:testfl3
cd ../fitLib
python ../TestRunner.py +vhx -f +o tests/Results +p FixtureRenames.txt localhost 80 %fittest% > tests/Results/allTests.txt
cd ../tests
goto skip

:testfl4
cd ../fitLib
python ../TestRunner.py +vehx -f +o tests/Results +p FixtureRenames.txt localhost 80 %fittest% > tests/Results/allTests.txt
cd ../tests
goto skip


:testfl5
cd ../fitLib
python ../TestRunner.py +vfrhx -o tests/Results +p FixtureRenames.txt localhost 80 FitSpecifications.FixtureSpecifications.%fittest% > tests/Results/allTests.txt
cd ../tests




:skip