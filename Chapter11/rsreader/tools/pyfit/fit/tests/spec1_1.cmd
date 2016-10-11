@echo off
rem Fit 1.1 specification tests

cd ..
python FolderRunner.py +e -q yt fat/Fit1_1Tests fat/Reports fat/Fit1_1Tests/FixtureRenames.txt > tests/testout/Fit1_1Tests.txt
cd tests

