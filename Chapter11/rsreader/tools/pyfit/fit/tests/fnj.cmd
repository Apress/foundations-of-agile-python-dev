@echo off
rem FitNesse Java tests
rem Fitnesse must be up for these tests!


java -cp c:/fitnesse/fitnesse.jar fitnesse.runner.TestRunner -xml 'stdout' localhost 80 FitNesse.SuiteAcceptanceTests.SuiteFixtureTests