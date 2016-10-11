@echo off
rem Run all tests

if "%1" == "prod" goto site
if "%1" == "test" goto doit
echo Can't understand %1
echo running tests against development system
goto doit

:site
echo setting current path to python directory
cd c:\Python23\Lib\site-packages\fit\tests

:doit



cd ..
echo Core Fit unit tests
python tests/AllTests.py > tests/testout/AllTests-t-all.txt
echo,
echo Fit Library Unit Tests
python fitLib/tests/AllTests.py > tests/testout\AllTests-flt.txt
echo,
echo FitNesse unit tests
python tests/FitServerTest.py > tests/testout/AllTests-fnt.txt
echo,
echo Batch Acceptance Tests from AllTests.txt script
echo,
python FileRunner.py +q et fat/Documents/AllTests.txt fat/Reports > tests/testout/AllTests-a-all.txt
echo,
echo Batch acceptance tests from fat/Documents
echo,
python FileRunner.py +q et fit/AccTests/AllTests.txt fit/Results > tests/testout/AllTests-a-allp2.txt
echo,
echo Fit 1.1 Specification Tests
echo Failures in Fixtures.html are expected.
echo,

python FolderRunner.py +e +q et fat/Fit1_1Tests fat/Reports fat/Fit1_1Tests/FixtureRenames.txt > tests/testout/AllTests-1_1.txt


cd fitLib
echo,
echo Fit Library Specification Tests
python ../FolderRunner.py +rv +q et tests/FixtureSpecifications tests/Results > ../tests/testout/AllTests-flt.txt
cd ..

if "%1" == "prod" goto site2
goto doit2

:site2
cd %thisdir%
:doit2


cd tests
