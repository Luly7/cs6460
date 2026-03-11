"""
Autograder for Berkeley AI Pacman Projects

This module provides functionality for automated grading of student code submissions
for the Berkeley AI Pacman projects. It runs test cases, validates solutions, and 
generates detailed feedback reports.

Key Features:
- Command line interface for running tests and grading assignments
- Flexible test case framework with support for dependencies
- Optional graphical display of Pacman game execution
- Multiple output formats (console, edX, Gradescope)
- Robust error handling and detailed feedback
- Support for both individual and batch grading

Modifications:
1. Reordered imports according to pylint rules (April 2022)
2. Added docstrings (April 2022)
3. Put main code in main function (April 2022) 
4. Replaced deprecated imp module with importlib (April 2022)
5. Removed unused code: functions, imports (April 2022)
6. Replace deprecated optparse with argparse (April 2022)
7. Proper escape of backslashes in regex matches (April 2022)
8. Updated docstrings and documentation (1 Dec 2024, George Rudolph)
9. Verified compatibility with Python 3.13 (1 Dec 2024, George Rudolph)

Attribution:
The Pacman AI projects were developed at UC Berkeley by John DeNero, Dan Klein,
Brad Miller, Nick Hay, and Pieter Abbeel.

License:
Original Berkeley course materials remain under their original license.
Modifications copyright (c) 2024 George Rudolph
"""
#pylint: disable = line-too-long

# imports from python standard library

import importlib
import argparse
import os
import re
import sys
import random
import pprint
import shutil

import projectParams
#from pacman import GameState
import grading
import testParser
import testClasses


def read_command() -> argparse.Namespace:
    '''Register command line arguments and return parsed arguments'''
    parser = argparse.ArgumentParser(description="Run public tests on student code")
    parser.set_defaults(
        generateSolutions=False,
        edxOutput=False,
        gsOutput=False,
        muteOutput=False,
        printTestCase=False,
        noGraphics=False,
    )
    # BEGIN SOLUTION NO PROMPT
    parser.set_defaults(generatePublicTests=False)
    # END SOLUTION NO PROMPT
    parser.add_argument(
        "--test-directory",
        dest="testRoot",
        default="test_cases",
        help="Root test directory which contains subdirectories corresponding to each question",
    )
    parser.add_argument(
        "--student-code",
        dest="studentCode",
        default=projectParams.STUDENT_CODE_DEFAULT,
        help="comma separated list of student code files",
    )
    parser.add_argument(
        "--code-directory",
        dest="codeRoot",
        default="",
        help="Root directory containing the student and testClass code",
    )
    parser.add_argument(
        "--test-case-code",
        dest="testCaseCode",
        default=projectParams.PROJECT_TEST_CLASSES,
        help="class containing testClass classes for this project",
    )
    parser.add_argument(
        "--generate-solutions",
        dest="generateSolutions",
        action="store_true",
        help="Write solutions generated to .solution file",
    )
    parser.add_argument(
        "--edx-output",
        dest="edxOutput",
        action="store_true",
        help="Generate edX output files",
    )
    parser.add_argument(
        "--gradescope-output",
        dest="gsOutput",
        action="store_true",
        help="Generate GradeScope output files",
    )
    parser.add_argument(
        "--mute",
        dest="muteOutput",
        action="store_true",
        help="Mute output from executing tests",
    )
    parser.add_argument(
        "--print-tests",
        "-p",
        dest="printTestCase",
        action="store_true",
        help="Print each test case before running them.",
    )
    parser.add_argument(
        "--test",
        "-t",
        dest="runTest",
        default=None,
        help="Run one particular test.  Relative to test root.",
    )
    parser.add_argument(
        "--question",
        "-q",
        dest="gradeQuestion",
        default=None,
        help="Grade one particular question.",
    )
    parser.add_argument(
        "--no-graphics",
        dest="noGraphics",
        action="store_true",
        help="No graphics display for pacman games.",
    )
    # BEGIN SOLUTION NO PROMPT
    parser.add_argument(
        "--generate-public-tests",
        dest="generatePublicTests",
        action="store_true",
        help="Generate ./test_cases/* from ./private_test_cases/*",
    )
    # END SOLUTION NO PROMPT
    args = parser.parse_args()
    return args



def confirm_generate() -> None:
    '''Prompt user to confirm generating solution files, which will overwrite existing ones'''
    print("WARNING: this action will overwrite any solution files.")
    print("Are you sure you want to proceed? (yes/no)")
    while True:
        ans = sys.stdin.readline().strip()
        if ans == "yes":
            break
        if ans == "no":
            sys.exit(0)
        print('please answer either "yes" or "no"')

def load_module_file(module_name: str) -> object:
    '''Import and return module from file using importlib'''
    return importlib.import_module(module_name)


def read_file(path: str, root: str = "") -> str:
    """Read and return contents of file at given path relative to root directory"""
    with open(os.path.join(root, path), "r") as handle:
        return handle.read()

def print_test(testDict: dict, solutionDict: dict) -> None:
    '''Print test case and solution in a readable format
    
    Args:
        testDict: Dictionary containing test case data
        solutionDict: Dictionary containing solution data
    '''
    pp = pprint.PrettyPrinter(indent=4)
    print("Test case:")
    for line in testDict["__raw_lines__"]:
        print("   |", line)
    print("Solution:")
    for line in solutionDict["__raw_lines__"]:
        print("   |", line)

def run_test(testName: str, moduleDict: dict, printTestCase: bool = False, display: object = None) -> None:
    '''Run a single test case
    
    Args:
        testName: Name of test to run
        moduleDict: Dictionary of loaded student/test modules
        printTestCase: Whether to print test details
        display: Display object for graphics
    '''

    for module in moduleDict:
        # setattr(sys.modules[__name__], module, moduleDict[module])
        globals()[module] = moduleDict[module]

    testDict = testParser.TestParser(f"{testName}.test").parse()
    solutionDict = testParser.TestParser(f"{testName}.solution").parse()
    test_out_file = os.path.join(f"{testName}.test_output")
    testDict["test_out_file"] = test_out_file
    testClass = getattr(projectTestClasses, testDict["class"])

    questionClass = getattr(testClasses, "Question")
    question = questionClass({"max_points": 0}, display)
    testCase = testClass(question, testDict)

    if printTestCase:
        printTest(testDict, solutionDict)

    # This is a fragile hack to create a stub grades object
    grades = grading.Grades(projectParams.PROJECT_NAME, [(None, 0)])
    testCase.execute(grades, moduleDict, solutionDict)


def getDepends(testParser: object, testRoot: str, question: str) -> list:
    '''Get ordered list of dependencies for a question
    
    Args:
        testParser: Parser for test files
        testRoot: Root directory containing tests
        question: Question to get dependencies for
        
    Returns:
        List of question names in dependency order
    '''
    allDeps = [question]
    questionDict = testParser.TestParser(
        os.path.join(testRoot, question, "CONFIG")
    ).parse()
    if "depends" in questionDict:
        depends = questionDict["depends"].split()
        for d in depends:
            # run dependencies first
            allDeps = getDepends(testParser, testRoot, d) + allDeps
    return allDeps


def getTestSubdirs(testParser: object, testRoot: str, questionToGrade: str = None) -> list:
    '''Get list of question subdirectories to grade
    
    Args:
        testParser: Parser for test files
        testRoot: Root directory containing tests
        questionToGrade: Specific question to grade, if any
        
    Returns:
        List of question directory names to grade
    '''
    problemDict = testParser.TestParser(os.path.join(testRoot, "CONFIG")).parse()
    if questionToGrade != None:
        questions = getDepends(testParser, testRoot, questionToGrade)
        if len(questions) > 1:
            print(
                f"Note: due to dependencies, the following tests will be run: {' '.join(questions)}"
            )
        return questions
    if "order" in problemDict:
        return problemDict["order"].split()
    return sorted(os.listdir(testRoot))


def evaluate(
    generateSolutions: bool,
    testRoot: str,
    moduleDict: dict,
    edxOutput: bool = False,
    muteOutput: bool = False,
    gsOutput: bool = False,
    printTestCase: bool = False,
    questionToGrade: str = None,
    display: object = None,
) -> float:
    '''Evaluate student code and return score
    
    Args:
        generateSolutions: Whether to generate solution files
        testRoot: Root directory containing tests
        moduleDict: Dictionary of loaded student/test modules
        edxOutput: Whether to generate edX output
        muteOutput: Whether to suppress output
        gsOutput: Whether to generate Gradescope output
        printTestCase: Whether to print test details
        questionToGrade: Specific question to grade
        display: Display object for graphics
        
    Returns:
        Total points earned
    '''
    # imports of testbench code.  note that the testClasses import must follow
    # the import of student code due to dependencies
    import testParser
    import testClasses

    for module in moduleDict:
        # setattr(sys.modules[__name__], module, moduleDict[module])
        globals()[module] = moduleDict[module]

    questions = []
    questionDicts = {}
    test_subdirs = getTestSubdirs(testParser, testRoot, questionToGrade)
    for q in test_subdirs:
        subdir_path = os.path.join(testRoot, q)
        if not os.path.isdir(subdir_path) or q[0] == ".":
            continue

        # create a question object
        questionDict = testParser.TestParser(
            os.path.join(subdir_path, "CONFIG")
        ).parse()
        questionClass = getattr(testClasses, questionDict["class"])
        question = questionClass(questionDict, display)
        questionDicts[q] = questionDict

        # load test cases into question
        tests = list(
            filter(lambda t: re.match("[^#~.].*\\.test\\Z", t), os.listdir(subdir_path))
        )
        tests = list(map(lambda t: re.match("(.*)\\.test\\Z", t).group(1), tests))
        for t in sorted(tests):
            test_file = os.path.join(subdir_path, f"{t}.test")
            solution_file = os.path.join(subdir_path, f"{t}.solution")
            test_out_file = os.path.join(subdir_path, f"{t}.test_output")
            testDict = testParser.TestParser(test_file).parse()
            if testDict.get("disabled", "false").lower() == "true":
                continue
            testDict["test_out_file"] = test_out_file
            testClass = getattr(projectTestClasses, testDict["class"])
            testCase = testClass(question, testDict)

            def makefun(testCase, solution_file):
                if generateSolutions:
                    # write solution file to disk
                    return lambda grades: testCase.writeSolution(
                        moduleDict, solution_file
                    )
                else:
                    # read in solution dictionary and pass as an argument
                    testDict = testParser.TestParser(test_file).parse()
                    solutionDict = testParser.TestParser(solution_file).parse()
                    if printTestCase:
                        return lambda grades: printTest(
                            testDict, solutionDict
                        ) or testCase.execute(grades, moduleDict, solutionDict)
                    else:
                        return lambda grades: testCase.execute(
                            grades, moduleDict, solutionDict
                        )

            question.addTestCase(testCase, makefun(testCase, solution_file))

        # Note extra function is necessary for scoping reasons
        def makefun(question):
            return lambda grades: question.execute(grades)

        setattr(sys.modules[__name__], q, makefun(question))
        questions.append((q, question.getMaxPoints()))

    grades = grading.Grades(
        projectParams.PROJECT_NAME,
        questions,
        gsOutput=gsOutput,
        edxOutput=edxOutput,
        muteOutput=muteOutput,
    )
    if questionToGrade == None:
        for q in questionDicts:
            for prereq in questionDicts[q].get("depends", "").split():
                grades.addPrereq(q, prereq)

    grades.grade(sys.modules[__name__], bonusPic=projectParams.BONUS_PIC)
    return grades.points


def getDisplay(graphicsByDefault: bool, options: object = None) -> object:
    '''Get appropriate display object based on options
    
    Args:
        graphicsByDefault: Whether graphics should be enabled by default
        options: Command line options object
        
    Returns:
        Display object for graphics
    '''
    graphics = graphicsByDefault
    if options is not None and options.noGraphics:
        graphics = False
    if graphics:
        try:
            import graphicsDisplay

            return graphicsDisplay.PacmanGraphics(1, frameTime=0.05)
        except ImportError:
            pass
    import textDisplay

    return textDisplay.NullGraphics()


# BEGIN SOLUTION NO PROMPT


def copy(srcDir: str, destDir: str, filename: str) -> None:
    '''Copy a file from source to destination directory
    
    Args:
        srcDir: Source directory path
        destDir: Destination directory path
        filename: Name of file to copy
    '''
    srcFilename = os.path.join(srcDir, filename)
    destFilename = os.path.join(destDir, filename)
    print(f"Copying {srcFilename} -> {destFilename}")
    shutil.copy(srcFilename, destFilename)
    # with open(os.path.join(srcDir, filename), 'r') as f1:
    #     with open(os.path.join(destDir, filename), 'w') as f2:
    #         f2.write(f1.read())


def generatePublicTests(
    moduleDict: dict, privateRoot: str = "private_test_cases", publicRoot: str = "test_cases"
) -> None:
    '''Generate public test files from private test cases
    
    Args:
        moduleDict: Dictionary of loaded modules
        privateRoot: Directory containing private test cases
        publicRoot: Directory to write public test cases
    '''
    import testParser
    import testClasses

    for module in moduleDict:
        setattr(sys.modules[__name__], module, moduleDict[module])

    if not os.path.exists(publicRoot):
        os.mkdir(publicRoot)
    copy(privateRoot, publicRoot, "CONFIG")
    for q in sorted(os.listdir(privateRoot)):
        private_subdir_path = os.path.join(privateRoot, q)
        public_subdir_path = os.path.join(publicRoot, q)
        if not os.path.exists(public_subdir_path):
            os.mkdir(public_subdir_path)

        if not os.path.isdir(private_subdir_path) or q[0] == ".":
            continue

        copy(private_subdir_path, public_subdir_path, "CONFIG")

        # create a question object
        questionDict = testParser.TestParser(
            os.path.join(public_subdir_path, "CONFIG")
        ).parse()
        questionClass = getattr(testClasses, questionDict["class"])
        question = questionClass(questionDict, getDisplay(False))

        tests = list(
            filter(
                lambda t: re.match("[^#~.].*\\.test\\Z", t),
                os.listdir(private_subdir_path),
            )
        )
        tests = list(map(lambda t: re.match("(.*)\\.test\\Z", t).group(1), tests))
        for t in sorted(tests):
            test_file = os.path.join(private_subdir_path, f"{t}.test")
            public_test_file = os.path.join(public_subdir_path, f"{t}.test")
            test_out_file = os.path.join(public_subdir_path, f"{t}.test_output")
            print(
                f"Creating public test case {public_test_file} from {test_file}"
            )

            testDict = testParser.TestParser(test_file).parse()
            if testDict.get("disabled", "false").lower() == "true":
                continue
            testDict["test_out_file"] = test_out_file
            testClass = getattr(projectTestClasses, testDict["class"])
            testCase = testClass(question, testDict)

            testCase.createPublicVersion()
            testCase.emitPublicVersion(public_test_file)


# END SOLUTION NO PROMPT


def main() -> None:
    '''Main entry point for autograder'''
    random.seed(0)
    options = read_command()
    if options.generateSolutions:
        confirm_generate()
    codePaths = options.studentCode.split(",")
    moduleDict = {}
    for cp in codePaths:
        moduleName = re.match(".*?([^/]*)\\.py", cp).group(1)
        moduleDict[moduleName] = load_module_file(moduleName)
    moduleName = re.match(".*?([^/]*)\\.py", options.testCaseCode).group(1)
    moduleDict["projectTestClasses"] = load_module_file(moduleName)

    # BEGIN SOLUTION NO PROMPT
    if options.generatePublicTests:
        generatePublicTests(moduleDict)
        sys.exit()
    # END SOLUTION NO PROMPT

    if options.runTest is not None:
        runTest(
            options.runTest,
            moduleDict,
            printTestCase=options.printTestCase,
            display=getDisplay(True, options),
        )
    else:
        evaluate(
            options.generateSolutions,
            options.testRoot,
            moduleDict,
            gsOutput=options.gsOutput,
            edxOutput=options.edxOutput,
            muteOutput=options.muteOutput,
            printTestCase=options.printTestCase,
            questionToGrade=options.gradeQuestion,
            display=getDisplay(options.gradeQuestion is not None, options),
        )


if __name__ == "__main__":
    main()
