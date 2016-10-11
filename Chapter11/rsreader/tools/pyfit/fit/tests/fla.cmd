@echo off
rem Fit Library acceptance test command router.
set fittest=""

if "%1" == "?" goto listit

rem options processing

set options="-v"
if "%2" == "" goto endOptions
set options="%1"
shift

:endOptions

rem All Tests

if "%1" == "all" goto RunAllTests

rem FixtureFixture
if "%1" == "ff" goto ffRunAll
if "%1" == "ff1" set fittest="BadFixtureClass.html"
if "%1" == "ff2" set fittest="ColourTests.html"
if "%1" == "ff3" set fittest="EmptyTable.html"
if "%1" == "ff4" set fittest="FirstTest.html"
if "%1" == "ff5" set fittest="IncorrectRowAdditions.html"
if "%1" == "ff6" set fittest="LongerRowAdditions.html"
if "%1" == "ff7" set fittest="MissingFixtureClass.html"
if "%1" == "ff8" set fittest="MissingRowAdditions.html"
if "%1" == "ff9" set fittest="ReportTests.html"
if "%1" == "ff10" set fittest="ReportWrongTests.html"
if "%1" == "ff11" set fittest="RowAdds.html"
if "%1" == "ff12" set fittest="RowInsertions.html"
if "%1" == "ff13" set fittest="UnexpectedRowAdditions.html"
if "%1" == "ff14" set fittest="UnexpectedRowAdditionsTwo.html"
if not %fittest% == "" goto ffcmd

rem ColumnFixture

set dir="SpecifyColumnFixture"
if "%1" == "col" goto RunEntireDirectory
if "%1" == "col1" set fittest="CamelNames.html"
if "%1" == "col2" set fittest="CannotParse.html"
if "%1" == "col3" set fittest="MissingField.html"
if "%1" == "col4" set fittest="MissingFirstRow.html"
if "%1" == "col5" set fittest="MissingMethod.html"
if "%1" == "col6" set fittest="RowsLong.html"
if "%1" == "col7" set fittest="RowsShort.html"
if "%1" == "col8" set fittest="SpecialEmpty.html"
if "%1" == "col9" set fittest="SpecialError.html"
if "%1" == "col10" set fittest="SpecialErrorWrong.html"
if "%1" == "col11" set fittest="TestDifferingResults.html"
if "%1" == "col12" set fittest="TestFieldsAndMethods.html"
if "%1" == "col13" set fittest="TestLeftToRight.html"
if "%1" == "col14" set fittest="TestsExplicit.html"
if "%1" == "col15" set fittest="TestsFail.html"
if "%1" == "col16" set fittest="VoidMethod.html"
if "%1" == "col17" set fittest="WrongType.html"
if not %fittest% == "" goto GenericSpecifyCommand

rem ActionFixture
set dir="SpecifyActionFixture"
if "%1" == "act" goto RunEntireDirectory
if "%1" == "act1" set fittest="ActionExceptions.html"
if "%1" == "act2" set fittest="ActionsExistWithRightType.html"
if "%1" == "act3" set fittest="BooleanEqualsProblem.html"
if "%1" == "act4" set fittest="EmptyTable.html"
if "%1" == "act5" set fittest="ExtraCellsInRows.html"
if "%1" == "act6" set fittest="MissingCellsInRows.html"
if "%1" == "act7" set fittest="NoStart.html"
if "%1" == "act8" set fittest="PressCanBeVoid.html"
if "%1" == "act9" set fittest="SameActor.html"
if "%1" == "act10" set fittest="SelfStarter.html"
if "%1" == "act11" set fittest="StartMustExist.html"
if "%1" == "act12" set fittest="StartNotFixture.html"
if "%1" == "act13" set fittest="SwitchActor.html"
if "%1" == "act14" set fittest="UsualOperation.html"
if not %fittest% == "" goto GenericSpecifyCommand

rem RowFixture

set dir="SpecifyRowFixture"
if "%1" == "row" goto RunEntireDirectory
if "%1" == "row1" set fittest="RowsCorrect.html"
if "%1" == "row2" set fittest="RowsAnyOrder.html"
if "%1" == "row3" set fittest="ColumnsAnyOrder.html"
if "%1" == "row4" set fittest="ColumnsRepeated.html"
if "%1" == "row5" set fittest="SomeColumns.html"
if "%1" == "row6" set fittest="MissingRow.html"
if "%1" == "row7" set fittest="SurplusRow.html"
if "%1" == "row8" set fittest="WrongNonKey.html"
if "%1" == "row9" set fittest="WrongKey.html"
if "%1" == "row10" set fittest="WrongKeyDuplicated.html"
if "%1" == "row11" set fittest="InconsistentColumns.html"
if "%1" == "row12" set fittest="BadFieldNames.html"
if "%1" == "row13" set fittest="CamelNames.html"
if "%1" == "row14" set fittest="FirstRowNeeded.html"
if "%1" == "row15" set fittest="ExtraCellsIgnored.html"
if "%1" == "row16" set fittest="MissingCells.html"
if "%1" == "row17" set fittest="SpecialCellValue.html"
if not %fittest% == "" goto GenericSpecifyCommand

rem Miscellanious Tests

if "%1" == "summary" set fittest="SpecifySummary.html"
if "%1" == "graph" set fittest="SpecifyGraphics.html"
if "%1" == "image" set fittest="SpecifyImageFixture.html"
if "%1" == "camel" set fittest="TestExtendedCamel.html"
if "%1" == "tree" set fittest="SpecifyTrees.html"
if "%1" == "table" set fittest="SpecifyTables.html"
if "%1" == "comb" set fittest="SpecifyCombineFixture.html"
if "%1" == "const" set fittest="SpecifyConstraintFixture.html"
if not %fittest% == "" goto MiscCmd

rem Fixture Specifications

set dir="SpecifyFixture"
if "%1" == "fix" goto RunEntireDirectory
if "%1" == "fix1" set fittest="UnknownFixture.html"
if "%1" == "fix2" set fittest="FixtureConstructorHidden.html"
if "%1" == "fix3" set fittest="NoNullaryConstructor.html"
if "%1" == "fix4" set fittest="NotFixture.html"
if "%1" == "fix5" set fittest="IgnoringFixture.html"
if not %fittest% == "" goto GenericSpecifyCommand

rem DoFixture Specifications

set dir="SpecifyDoFixture"
if "%1" == "do" goto RunEntireDirectory
if "%1" == "do1" set fittest="TestActions.html"
if "%1" == "do2" set fittest="TestKeywords.html"
if "%1" == "do3" set fittest="TestExtendedCamel.html"
if "%1" == "do4" set fittest="TestNote.html"
if "%1" == "do5" set fittest="TestBooleanAction.html"
if "%1" == "do6" set fittest="TestEnsure.html"
if "%1" == "do7" set fittest="TestNot.html"
if "%1" == "do8" set fittest="TestShow.html"
if "%1" == "do9" set fittest="TestOtherTypes.html"
if "%1" == "do10" set fittest="TestSpecialAction.html"
if "%1" == "do11" set fittest="TestFixtureOverride.html"
if "%1" == "do12" set fittest="TestUnexpectedException.html"
if "%1" == "do13" set fittest="TestBadType.html"
if "%1" == "do14" set fittest="TestBadAction.html"
if "%1" == "do15" set fittest="SetUp.html"
if not %fittest% == "" goto GenericSpecifyCommand

rem SequenceFixture Specifications

set dir="SpecifySequenceFixture"
if "%1" == "seq" goto RunEntireDirectory
if "%1" == "seq1" set fittest="TestActions.html"
if "%1" == "seq2" set fittest="TestParameters.html"
if "%1" == "seq3" set fittest="TestExtendedCamel.html"
if "%1" == "seq4" set fittest="TestNote.html"
if "%1" == "seq5" set fittest="TestBooleanAction.html"
if "%1" == "seq6" set fittest="TestNot.html"
if "%1" == "seq7" set fittest="TestShow.html"
if "%1" == "seq8" set fittest="TestOtherTypes.html"
if "%1" == "seq9" set fittest="TestSpecialAction.html"
if "%1" == "seq10" set fittest="TestFixtureOverride.html"
if "%1" == "seq11" set fittest="TestUnexpectedException.html"
if "%1" == "seq12" set fittest="TestBadType.html"
if "%1" == "seq13" set fittest="TestBadAction.html"
if "%1" == "seq14" set fittest="SetUp.html"
if not %fittest% == "" goto GenericSpecifyCommand

rem DoFixtureFlow Specifications

set dir="SpecifyDoFixtureFlow"
if "%1" == "dof" goto RunEntireDirectory
if "%1" == "dof1" set fittest="TestActions.html"
if "%1" == "dof2" set fittest="TestKeywords.html"
if "%1" == "dof3" set fittest="TestExtendedCamel.html"
if "%1" == "dof4" set fittest="TestNote.html"
if "%1" == "dof5" set fittest="TestBooleanAction.html"
if "%1" == "dof6" set fittest="TestNot.html"
if "%1" == "dof7" set fittest="TestShow.html"
if "%1" == "dof8" set fittest="TestOtherTypes.html"
if "%1" == "dof9" set fittest="TestSpecialAction.html"
if "%1" == "dof10" set fittest="TestFixtureOverride.html"
if "%1" == "dof11" set fittest="TestReturnedFixture.html"
if "%1" == "dof12" set fittest="TestExplicitFixture.html"
if "%1" == "dof13" set fittest="TestNaming.html"
if "%1" == "dof14" set fittest="TestNamingObject.html"
if "%1" == "dof15" set fittest="TestAutoEmbeddedFixture.html"
if "%1" == "dof16" set fittest="TestAutoListFixture.html"
if "%1" == "dof17" set fittest="TestCalculateFixture.html"
if "%1" == "dof18" set fittest="TestAutoPropertyAccess.html"
if "%1" == "dof19" set fittest="TestMultiStepAccess.html"
if "%1" == "dof20" set fittest="TestUnexpectedException.html"
if "%1" == "dof21" set fittest="TestBadType.html"
if "%1" == "dof22" set fittest="TestBadAction.html"
if "%1" == "dof23" set fittest="TestNameOnlyObject.html"
if "%1" == "dof24" set fittest="TestUseOnlyNamed.html"
if "%1" == "dof25" set fittest="TestFlow.html"
if not %fittest% == "" goto GenericSpecifyCommand

rem CalculateFixture Specifications

set dir="SpecifyCalculateFixture"
if "%1" == "calc" goto RunEntireDirectory
if "%1" == "calc1" set fittest="TestsExplicit.html"
if "%1" == "calc2" set fittest="TestsFail.html"
if "%1" == "calc3" set fittest="TestSeveralMethods.html"
if "%1" == "calc4" set fittest="TestLeftToRight.html"
if "%1" == "calc5" set fittest="TestDifferingResults.html"
if "%1" == "calc6" set fittest="RowsShort.html"
if "%1" == "calc7" set fittest="CamelNames.html"
if "%1" == "calc8" set fittest="EmptyGivenNames.html"
if "%1" == "calc9" set fittest="SpecialError.html"
if "%1" == "calc10" set fittest="SpecialErrorWrong.html"
if "%1" == "calc11" set fittest="SpecialEmptyDoubleQuote.html"
if "%1" == "calc12" set fittest="SpecialEmptyBlank.html"
if "%1" == "calc13" set fittest="TestGraphics.html"
if "%1" == "calc14" set fittest="EmptyColumnMissing.html"
if "%1" == "calc15" set fittest="NoExpectedColumns.html"
if "%1" == "calc16" set fittest="MissingMethod.html"
if "%1" == "calc17" set fittest="VoidMethod.html"
if "%1" == "calc18" set fittest="WrongType.html"
if "%1" == "calc19" set fittest="CannotParse.html"
if "%1" == "calc20" set fittest="MissingFirstRow.html"
if "%1" == "calc21" set fittest="RowsLong.html"
if not %fittest% == "" goto GenericSpecifyCommand

rem SetUpFixture Specifications

set dir="SpecifySetUpFixture"
if "%1" == "setup" goto RunEntireDirectory
if "%1" == "setup1" set fittest="MissingFirstRow.html"
if "%1" == "setup2" set fittest="MissingMethod.html"
if "%1" == "setup3" set fittest="RowsShort.html"
if "%1" == "setup4" set fittest="TestAddFails.html"
if "%1" == "setup5" set fittest="TestSetUpCall.html"
if "%1" == "setup6" set fittest="TestSimple.html"
if not %fittest% == "" goto GenericSpecifyCommand

rem SpecifySequenceFixtureFlow Specifications

set dir="SpecifySequenceFixtureFlow"
if "%1" == "seqf" goto RunEntireDirectory
if "%1" == "seqf1" set fittest="TestActions.html"
if "%1" == "seqf2" set fittest="TestParameters.html"
if "%1" == "seqf3" set fittest="TestExtendedCamel.html"
if "%1" == "seqf4" set fittest="TestNote.html"
if "%1" == "seqf5" set fittest="TestBooleanAction.html"
if "%1" == "seqf6" set fittest="TestEnsure.html"
if "%1" == "seqf7" set fittest="TestNot.html"
if "%1" == "seqf8" set fittest="TestShow.html"
if "%1" == "seqf9" set fittest="TestOtherTypes.html"
if "%1" == "seqf10" set fittest="TestSpecialAction.html"
if "%1" == "seqf11" set fittest="TestFixtureOverride.html"
if "%1" == "seqf12" set fittest="TestReturnedFixture.html"
if "%1" == "seqf13" set fittest="TestExplicitFixture.html"
if "%1" == "seqf14" set fittest="TestNaming.html"
if "%1" == "seqf15" set fittest="TestUnexpectedException.html"
if "%1" == "seqf16" set fittest="TestBadType.html"
if "%1" == "seqf17" set fittest="TestBadAction.html"
if "%1" == "seqf18" set fittest="TestNameOnlyObject.html"
if "%1" == "seqf19" set fittest="TestUseOnlyNamed.html"
if not %fittest% == "" goto GenericSpecifyCommand

rem SpecifyArrayFixture

set dir="SpecifyArrayFixture"
if "%1" == "array" goto RunEntireDirectory
if "%1" == "array1" set fittest="TestAll.html"
if "%1" == "array2" set fittest="TestSomeInOrder.html"
if "%1" == "array3" set fittest="TestOutOfOrder.html"
if "%1" == "array4" set fittest="TestInsertAtStart.html"
if "%1" == "array5" set fittest="TestNoneExpected.html"
if "%1" == "array6" set fittest="TestAllWithProperty.html"
if "%1" == "array7" set fittest="TestMixedObjects.html"
if "%1" == "array8" set fittest="TestNoActuals.html"
if "%1" == "array9" set fittest="TestNoActualsSoMissing.html"
if "%1" == "array10" set fittest="TestMapCollection.html"
if "%1" == "array11" set fittest="TestMapCollectionOutOfOrder.html"
if "%1" == "array12" set fittest="TestMixedCollection.html"
if "%1" == "array13" set fittest="TestTrees.html"
if "%1" == "array14" set fittest="TestExtraCells.html"
if "%1" == "array15" set fittest="TestMissingCells.html"
if "%1" == "array16" set fittest="TestMissingRows.html"
if "%1" == "array17" set fittest="TestUnknownField.html"
if not %fittest% == "" goto GenericSpecifyCommand

rem SpecifySetFixture

set dir="SpecifySetFixture"
if "%1" == "set" goto RunEntireDirectory
if "%1" == "set1" set fittest="TestAll.html"
if "%1" == "set2" set fittest="TestAllDifferentOrder.html"
if "%1" == "set3" set fittest="TestAllWithProperty.html"
if "%1" == "set4" set fittest="TestBag.html"
if "%1" == "set5" set fittest="TestExtraCells.html"
if "%1" == "set6" set fittest="TestGraphics.html"
if "%1" == "set7" set fittest="TestInsertAtStart.html"
if "%1" == "set8" set fittest="TestMissing.html"
if "%1" == "set9" set fittest="TestMissingAtStart.html"
if "%1" == "set10" set fittest="TestMissingCells.html"
if "%1" == "set11" set fittest="TestMissingRows.html"
if "%1" == "set12" set fittest="TestMixedObjects.html"
if "%1" == "set15" set fittest="TestNoActuals.html"
if "%1" == "set14" set fittest="TestNoActualsSoMissing.html"
if "%1" == "set13" set fittest="TestNoneExpected.html"
if "%1" == "set16" set fittest="TestSurplus.html"
if "%1" == "set17" set fittest="TestUnknownField.html"
if not %fittest% == "" goto GenericSpecifyCommand

rem SpecifySubsetFixture

set dir="SpecifySubsetFixture"
if "%1" == "sub" goto RunEntireDirectory
if "%1" == "sub1" set fittest="TestAll.html"
if "%1" == "sub2" set fittest="TestFewer.html"
if "%1" == "sub3" set fittest="TestMismatch.html"
if "%1" == "sub4" set fittest="TestMissing.html"
if "%1" == "sub5" set fittest="TestNone.html"
if not %fittest% == "" goto GenericSpecifyCommand

rem SpecifyGridFixture

set dir="SpecifyGridFixture"
if "%1" == "grid" goto RunEntireDirectory
if "%1" == "grid1" set fittest="EmptyGrid.html"
if "%1" == "grid2" set fittest="EmptyGridExpected.html"
if "%1" == "grid3" set fittest="EmptyGridNotExpected.html"
if "%1" == "grid4" set fittest="ImageGrid.html"
if "%1" == "grid5" set fittest="IntGrid.html"
if "%1" == "grid6" set fittest="StringGrid.html"
if "%1" == "grid7" set fittest="TreeGrid.html"
if not %fittest% == "" goto GenericSpecifyCommand

rem SpecifyFileCompare

set dir="SpecifyFileCompare"
if "%1" == "file" goto RunEntireDirectory
if "%1" == "cfile" set fittest="TestFiles.html"
if "%1" == "cdir" set fittest="TestDirectories.html"
if not %fittest% == "" goto CompareFileSpecifyCommand


echo Can't understand %1
goto skip

:RunEntireDirectory
cd ..
echo Tests in directory %dir%
python FolderRunner.py %options% -v fitLib/tests/FixtureSpecifications/%dir% fitLib/tests/Results > fitLib/tests/Results/%dir%.txt
cd tests
goto skip

:listit
type fla.cmd
goto skip

:ffcmd
cd ..
echo %fittest%
python FileRunner.py FitLib/Tests/FixtureFixtureSpecification/%fittest% FitLib/Tests/Results/%fittest% > FitLib/Tests/Results/%fittest%.txt
cd tests
goto skip

:ffRunAll
cd ..
echo %fittest%
python FolderRunner.py +v FitLib/Tests/FixtureFixtureSpecification FitLib/Tests/Results > FitLib/Tests/Results/FixtureFixtureAll.txt
cd tests
goto skip

:MiscCmd
cd ..
echo %fittest%
python FileRunner.py FitLib/Tests/FixtureSpecifications/%fittest% FitLib/Tests/Results/%fittest% > FitLib/Tests/Results/%fittest%.txt
cd tests
goto skip

:GenericSpecifyCommand
cd ..
echo %fittest%
python HtmlRunner.py FitLib/Tests/FixtureSpecifications/%dir%/%fittest% FitLib/Tests/Results/%fittest% >FitLib/Tests/Results/%fittest%.txt
cd tests
goto skip

:RunAllTests
cd ../fitLib
echo All Tests
python ../FolderRunner.py %options% +v +q et tests/FixtureSpecifications tests/Results > tests/Results/AllTests.txt
cd ../tests
goto skip

:CompareFileSpecifyCommand
cd ../fitLib
echo %fittest%
python ../HtmlRunner.py tests/FixtureSpecifications/%dir%/%fittest% tests/Results/%fittest% >tests/Results/%fittest%.txt
cd ../tests

:skip