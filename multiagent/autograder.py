"""
Autograder module for Pacman AI projects.

This module handles running and grading student code against test cases.
It provides functionality for:
- Loading and running test cases
- Evaluating student solutions
- Generating solution files
- Producing formatted output for different grading platforms

Modified by:
- George Rudolph 20 Dec 2021: Use importlib instead of imp which is deprecated.
  Run using Python 3.10.
- George Rudolph 22 Nov 2024: Added comprehensive docstrings with Args/Returns sections.
  Added type hints throughout module. Improved code organization and readability.
  Added constants type annotations. Added return type hints for all functions.
  Added parameter type hints for all functions. Use f-strings for improved readability.
  Python 3.13 compatibility verified.

Licensing Information:  You are free to use or extend these projects for
educational purposes provided that (1) you do not distribute or publish
solutions, (2) you retain this notice, and (3) you provide clear
attribution to UC Berkeley, including a link to http://ai.berkeley.edu.

Attribution Information: The Pacman AI projects were developed at UC Berkeley.
The core projects and autograders were primarily created by John DeNero
(denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
Student side autograding was added by Brad Miller, Nick Hay, and
Pieter Abbeel (pabbeel@cs.berkeley.edu).
"""

# imports from python standard library
import random
import importlib
import optparse
import os
import pprint
import re
import sys
import projectParams
import grading

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
        Parsed options object containing argument values
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
    Prompt for confirmation before generating solution files.
    
    Exits if user does not confirm with 'yes'.
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
def setModuleName(module: object, filename: str) -> None:
    """
    Set the module name in the file attribute of functions and classes.
    
    Args:
        module: Module object to modify
        filename: Filename to set
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


def loadModuleFile(moduleName: str, filePath: str) -> object:
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
        root: Optional root directory
        
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


def splitStrings(d: dict) -> dict:
    """
    Split string values in dictionary on newlines.
    
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
        print(f"   | {line}")
    print("Solution:")
    for line in solutionDict["__raw_lines__"]:
        print(f"   | {line}")


def runTest(testName: str, moduleDict: dict, printTestCase: bool = False, display: object = None) -> None:
    """
    Run a single test case.
    
    Args:
        testName: Name of test to run
        moduleDict: Dictionary of loaded modules
        printTestCase: Whether to print test case details
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


def getDepends(testParser: object, testRoot: str, question: str) -> list[str]:
    """
    Get ordered list of question dependencies.
    
    Args:
        testParser: TestParser object
        testRoot: Root test directory
        question: Question to get dependencies for
        
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

def getTestSubdirs(testParser: object, testRoot: str, questionToGrade: str = None) -> list[str]:
    """
    Get list of questions to grade.
    
    Args:
        testParser: TestParser object
        testRoot: Root test directory
        questionToGrade: Optional specific question to grade
        
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
             printTestCase: bool = False, questionToGrade: str = None, display: object = None) -> float:
    """
    Evaluate student code against test cases.
    
    Args:
        generateSolutions: Whether to generate solution files
        testRoot: Root test directory
        moduleDict: Dictionary of loaded modules
        exceptionMap: Map of exceptions to hint messages
        edxOutput: Whether to generate edX output
        muteOutput: Whether to suppress output
        gsOutput: Whether to generate Gradescope output
        printTestCase: Whether to print test cases
        questionToGrade: Optional specific question to grade
        display: Display object for visualization
        
    Returns:
        Total points earned
    """
    # imports of testbench code.  note that the testClasses import must follow
    # the import of student code due to dependencies
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


def getDisplay(graphicsByDefault: bool, options: optparse.Values = None) -> object:
    """
    Get appropriate display object based on options.
    
    Args:
        graphicsByDefault: Whether to use graphics by default
        options: Optional command line options
        
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
