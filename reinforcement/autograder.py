"""
Autograder for Student Code Evaluation and Testing

This module provides a comprehensive testing framework for evaluating student code
submissions in the Pacman AI projects. It handles test execution, grading, and
result reporting with support for both automated and interactive testing modes.

Key Components:
- Test Runner: Executes test cases and validates outputs
- Grading System: Scores submissions based on test results
- Output Formatter: Generates detailed test reports
- Solution Generator: Creates reference solutions
- Display Manager: Handles graphics/text visualization

Key Features:
- Flexible command line interface for test configuration
- Support for multiple student code files and test cases
- Detailed output formatting with multiple display modes
- Interactive graphics mode for visual validation
- Automated grading with customizable scoring

Originally from UC Berkeley CS188 Pacman Projects.
Modified for use in USAFA CS330 course.

Python Version: 3.13
Last Modified: 24 Nov 2024
Modified by: George Rudolph

Changes in this version:
- Verified compatibility with Python 3.13
- Improved docstring organization and clarity
- Added detailed component descriptions
- Updated formatting for better readability
- Modernized imports using importlib

Attribution: The Pacman AI projects were developed at UC Berkeley.
The core projects and autograders were primarily created by John DeNero
(denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
Student side autograding was added by Brad Miller, Nick Hay, and
Pieter Abbeel (pabbeel@cs.berkeley.edu).
"""

from typing import List, Optional, Dict, Any, Tuple, Union

import grading
import importlib
import optparse
import os
import re
import sys
import projectParams
import random
random.seed(0)
try:
    from pacman import GameState
except:
    pass

def readCommand(argv: list[str]) -> optparse.Values:
    """
    Parse and validate command line arguments.

    Args:
        argv: List of command line arguments

    Returns:
        Parsed options object containing all configuration settings
    """
    parser = optparse.OptionParser(
        description='Run public tests on student code')
    parser.set_defaults(generateSolutions=False, edxOutput=False, gsOutput=False,
                        muteOutput=False, printTestCase=False, noGraphics=False)
    parser.add_option('--test-directory',
                      dest='testRoot',
                      default='test_cases',
                      help='Root test directory which contains subdirectories corresponding to each question')
    parser.add_option('--student-code',
                      dest='studentCode',
                      default=projectParams.STUDENT_CODE_DEFAULT,
                      help='comma separated list of student code files')
    parser.add_option('--code-directory',
                      dest='codeRoot',
                      default="",
                      help='Root directory containing the student and testClass code')
    parser.add_option('--test-case-code',
                      dest='testCaseCode',
                      default=projectParams.PROJECT_TEST_CLASSES,
                      help='class containing testClass classes for this project')
    parser.add_option('--generate-solutions',
                      dest='generateSolutions',
                      action='store_true',
                      help='Write solutions generated to .solution file')
    parser.add_option('--edx-output',
                      dest='edxOutput',
                      action='store_true',
                      help='Generate edX output files')
    parser.add_option('--gradescope-output',
                      dest='gsOutput',
                      action='store_true',
                      help='Generate GradeScope output files')
    parser.add_option('--mute',
                      dest='muteOutput',
                      action='store_true',
                      help='Mute output from executing tests')
    parser.add_option('--print-tests', '-p',
                      dest='printTestCase',
                      action='store_true',
                      help='Print each test case before running them.')
    parser.add_option('--test', '-t',
                      dest='runTest',
                      default=None,
                      help='Run one particular test.  Relative to test root.')
    parser.add_option('--question', '-q',
                      dest='gradeQuestion',
                      default=None,
                      help='Grade one particular question.')
    parser.add_option('--no-graphics',
                      dest='noGraphics',
                      action='store_true',
                      help='No graphics display for pacman games.')
    (options, args) = parser.parse_args(argv)
    return options


def confirmGenerate() -> None:
    """
    Prompt for confirmation before overwriting solution files.
    
    Exits program if user does not confirm with 'yes'.
    """
    print('WARNING: this action will overwrite any solution files.')
    print('Are you sure you want to proceed? (yes/no)')
    while True:
        ans = sys.stdin.readline().strip()
        if ans == 'yes':
            break
        elif ans == 'no':
            sys.exit(0)
        else:
            print('please answer either "yes" or "no"')


# TODO: Fix this so that it tracebacks work correctly
# Looking at source of the traceback module, presuming it works
# the same as the intepreters, it uses co_filename.  This is,
# however, a readonly attribute.
def setModuleName(module: Any, filename: str) -> None:
    """
    Set the module name for better error tracebacks.

    Args:
        module: Python module object to modify
        filename: Name to set as the module's filename
    """
    functionType = type(confirmGenerate)
    classType = type(optparse.Option)

    for i in dir(module):
        o = getattr(module, i)
        if hasattr(o, '__file__'):
            continue

        if type(o) == functionType:
            setattr(o, '__file__', filename)
        elif type(o) == classType:
            setattr(o, '__file__', filename)
            # TODO: assign member __file__'s?
        # print i, type(o)

import py_compile


def loadModuleFile(moduleName: str, filePath: str) -> Any:
    """
    Load a Python module from file.

    Args:
        moduleName: Name of module to load
        filePath: Path to module file

    Returns:
        Loaded module object
    """
    return importlib.import_module(moduleName)


def readFile(path: str, root: str = "") -> str:
    """
    Read file from disk at specified path and return as string.

    Args:
        path: Path to file
        root: Optional root directory to prepend to path

    Returns:
        Contents of file as string
    """
    with open(os.path.join(root, path), 'r') as handle:
        return handle.read()


#######################################################################
# Error Hint Map
#######################################################################

# TODO: use these
ERROR_HINT_MAP = {
    'q1': {
        "<type 'exceptions.IndexError'>": """
      We noticed that your project threw an IndexError on q1.
      While many things may cause this, it may have been from
      assuming a certain number of successors from a state space
      or assuming a certain number of actions available from a given
      state. Try making your code more general (no hardcoded indices)
      and submit again!
    """
    },
    'q3': {
        "<type 'exceptions.AttributeError'>": """
        We noticed that your project threw an AttributeError on q3.
        While many things may cause this, it may have been from assuming
        a certain size or structure to the state space. For example, if you have
        a line of code assuming that the state is (x, y) and we run your code
        on a state space with (x, y, z), this error could be thrown. Try
        making your code more general and submit again!

    """
    }
}

import pprint


def splitStrings(d: dict) -> dict:
    """
    Split multi-line strings in dictionary values.

    Args:
        d: Dictionary to process

    Returns:
        New dictionary with string values split on newlines
    """
    d2 = dict(d)
    for k in d:
        if k[0:2] == "__":
            del d2[k]
            continue
        if d2[k].find("\n") >= 0:
            d2[k] = d2[k].split("\n")
    return d2


def printTest(testDict: dict, solutionDict: dict) -> None:
    """
    Print a test case and its solution.

    Args:
        testDict: Dictionary containing test case
        solutionDict: Dictionary containing solution
    """
    pp = pprint.PrettyPrinter(indent=4)
    print("Test case:")
    for line in testDict["__raw_lines__"]:
        print(f"   |{line}")
    print("Solution:")
    for line in solutionDict["__raw_lines__"]:
        print(f"   |{line}")


def runTest(testName: str, moduleDict: dict, printTestCase: bool = False, display: Any = None) -> None:
    """
    Run a single test case.

    Args:
        testName: Name of test to run
        moduleDict: Dictionary of loaded modules
        printTestCase: Whether to print test details
        display: Display object for visualization
    """
    import testParser
    import testClasses
    for module in moduleDict:
        setattr(sys.modules[__name__], module, moduleDict[module])

    testDict = testParser.TestParser(f"{testName}.test").parse()
    solutionDict = testParser.TestParser(f"{testName}.solution").parse()
    test_out_file = os.path.join(f'{testName}.test_output')
    testDict['test_out_file'] = test_out_file
    testClass = getattr(projectTestClasses, testDict['class'])

    questionClass = getattr(testClasses, 'Question')
    question = questionClass({'max_points': 0}, display)
    testCase = testClass(question, testDict)

    if printTestCase:
        printTest(testDict, solutionDict)

    # This is a fragile hack to create a stub grades object
    grades = grading.Grades(projectParams.PROJECT_NAME, [(None, 0)])
    testCase.execute(grades, moduleDict, solutionDict)


def getDepends(testParser: Any, testRoot: str, question: str) -> list[str]:
    """
    Get all dependencies needed to run a question.

    Args:
        testParser: Parser for test files
        testRoot: Root test directory
        question: Question to find dependencies for

    Returns:
        List of question names in dependency order
    """
    allDeps = [question]
    questionDict = testParser.TestParser(
        os.path.join(testRoot, question, 'CONFIG')).parse()
    if 'depends' in questionDict:
        depends = questionDict['depends'].split()
        for d in depends:
            # run dependencies first
            allDeps = getDepends(testParser, testRoot, d) + allDeps
    return allDeps

def getTestSubdirs(testParser: Any, testRoot: str, questionToGrade: Optional[str]) -> list[str]:
    """
    Get list of questions to grade.

    Args:
        testParser: Parser for test files
        testRoot: Root test directory
        questionToGrade: Specific question to grade, or None for all

    Returns:
        List of question names to grade
    """
    problemDict = testParser.TestParser(
        os.path.join(testRoot, 'CONFIG')).parse()
    if questionToGrade != None:
        questions = getDepends(testParser, testRoot, questionToGrade)
        if len(questions) > 1:
            print(f'Note: due to dependencies, the following tests will be run: {" ".join(questions)}')
        return questions
    if 'order' in problemDict:
        return problemDict['order'].split()
    return sorted(os.listdir(testRoot))


def evaluate(generateSolutions: bool, testRoot: str, moduleDict: dict, exceptionMap: dict = ERROR_HINT_MAP,
             edxOutput: bool = False, muteOutput: bool = False, gsOutput: bool = False,
             printTestCase: bool = False, questionToGrade: Optional[str] = None, display: Any = None) -> float:
    """
    Evaluate student code and return grade.

    Args:
        generateSolutions: Whether to generate solution files
        testRoot: Root test directory
        moduleDict: Dictionary of loaded modules
        exceptionMap: Map of exceptions to hint messages
        edxOutput: Whether to generate edX output
        muteOutput: Whether to suppress output
        gsOutput: Whether to generate Gradescope output
        printTestCase: Whether to print test details
        questionToGrade: Specific question to grade
        display: Display object for visualization

    Returns:
        Total points earned
    """
    import testParser
    import testClasses
    for module in moduleDict:
        setattr(sys.modules[__name__], module, moduleDict[module])

    questions = []
    questionDicts = {}
    test_subdirs = getTestSubdirs(testParser, testRoot, questionToGrade)
    for q in test_subdirs:
        subdir_path = os.path.join(testRoot, q)
        if not os.path.isdir(subdir_path) or q[0] == '.':
            continue

        # create a question object
        questionDict = testParser.TestParser(
            os.path.join(subdir_path, 'CONFIG')).parse()
        questionClass = getattr(testClasses, questionDict['class'])
        question = questionClass(questionDict, display)
        questionDicts[q] = questionDict

        # load test cases into question
        tests = [t for t in os.listdir(
            subdir_path) if re.match(r'[^#~.].*\.test\Z', t)]
        tests = [re.match(r'(.*)\.test\Z', t).group(1) for t in tests]
        for t in sorted(tests):
            test_file = os.path.join(subdir_path, f'{t}.test')
            solution_file = os.path.join(subdir_path, f'{t}.solution')
            test_out_file = os.path.join(subdir_path, f'{t}.test_output')
            testDict = testParser.TestParser(test_file).parse()
            if testDict.get("disabled", "false").lower() == "true":
                continue
            testDict['test_out_file'] = test_out_file
            testClass = getattr(projectTestClasses, testDict['class'])
            testCase = testClass(question, testDict)

            def makefun(testCase, solution_file):
                if generateSolutions:
                    # write solution file to disk
                    return lambda grades: testCase.writeSolution(moduleDict, solution_file)
                else:
                    # read in solution dictionary and pass as an argument
                    testDict = testParser.TestParser(test_file).parse()
                    solutionDict = testParser.TestParser(solution_file).parse()
                    if printTestCase:
                        return lambda grades: printTest(testDict, solutionDict) or testCase.execute(grades, moduleDict, solutionDict)
                    else:
                        return lambda grades: testCase.execute(grades, moduleDict, solutionDict)
            question.addTestCase(testCase, makefun(testCase, solution_file))

        # Note extra function is necessary for scoping reasons
        def makefun(question):
            return lambda grades: question.execute(grades)
        setattr(sys.modules[__name__], q, makefun(question))
        questions.append((q, question.getMaxPoints()))

    grades = grading.Grades(projectParams.PROJECT_NAME, questions,
                            gsOutput=gsOutput, edxOutput=edxOutput, muteOutput=muteOutput)
    if questionToGrade == None:
        for q in questionDicts:
            for prereq in questionDicts[q].get('depends', '').split():
                grades.addPrereq(q, prereq)

    grades.grade(sys.modules[__name__], bonusPic=projectParams.BONUS_PIC)
    return grades.points


def getDisplay(graphicsByDefault: bool, options: Optional[optparse.Values] = None) -> Any:
    """
    Get appropriate display object based on settings.

    Args:
        graphicsByDefault: Whether to use graphics by default
        options: Command line options object

    Returns:
        Display object for visualization
    """
    graphics = graphicsByDefault
    if options is not None and options.noGraphics:
        graphics = False
    if graphics:
        try:
            import graphicsDisplay
            return graphicsDisplay.PacmanGraphics(1, frameTime=.05)
        except ImportError:
            pass
    import textDisplay
    return textDisplay.NullGraphics()


if __name__ == '__main__':
    options = readCommand(sys.argv)
    if options.generateSolutions:
        confirmGenerate()
    codePaths = options.studentCode.split(',')
    # moduleCodeDict = {}
    # for cp in codePaths:
    #     moduleName = re.match('.*?([^/]*)\.py', cp).group(1)
    #     moduleCodeDict[moduleName] = readFile(cp, root=options.codeRoot)
    # moduleCodeDict['projectTestClasses'] = readFile(options.testCaseCode, root=options.codeRoot)
    # moduleDict = loadModuleDict(moduleCodeDict)

    moduleDict = {}
    for cp in codePaths:
        moduleName = re.match(r'.*?([^/]*)\.py', cp).group(1)
        moduleDict[moduleName] = loadModuleFile(
            moduleName, os.path.join(options.codeRoot, cp))
    moduleName = re.match(r'.*?([^/]*)\.py', options.testCaseCode).group(1)
    moduleDict['projectTestClasses'] = loadModuleFile(
        moduleName, os.path.join(options.codeRoot, options.testCaseCode))

    if options.runTest != None:
        runTest(options.runTest, moduleDict, printTestCase=options.printTestCase,
                display=getDisplay(True, options))
    else:
        evaluate(options.generateSolutions, options.testRoot, moduleDict,
                 gsOutput=options.gsOutput,
                 edxOutput=options.edxOutput, muteOutput=options.muteOutput, printTestCase=options.printTestCase,
                 questionToGrade=options.gradeQuestion, display=getDisplay(options.gradeQuestion != None, options))
