"""Autograder for testing student code submissions.

This module provides functionality for automatically grading student code submissions
by running test cases and comparing outputs against expected solutions.

Original Authors:
    John DeNero (denero@cs.berkeley.edu)
    Dan Klein (klein@cs.berkeley.edu)
    Brad Miller
    Nick Hay
    Pieter Abbeel (pabbeel@cs.berkeley.edu)

Modified by:
    George Rudolph
    Date: 9 Nov 2024

Changes:
    - Updated to run with Python 3.13
    - Added comprehensive docstrings
    - Added type hints throughout
    - Improved code organization

Previous Changes (George Rudolph):
    20 Dec 2021 - Use importlib instead of deprecated imp, run using Python 3.10
    21 Jan 2022 - Use argparse instead of deprecated optparse
    21 Jan 2022 - Disable pylint line-too-long warning
    21 Jan 2022 - Fix escape sequences in regex expressions
    24 Jan 2022 - Clean up pylint errors and warnings

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
#pylint: disable = line-too-long

# imports from python standard library
import importlib
import argparse
import os
import re
import sys
import random
from typing import Any, Dict, List, Optional, Callable
import grading
import projectParams
import testParser
import testClasses
import graphicsDisplay
import textDisplay
import util

random.seed(0)


def read_command() -> argparse.Namespace:
    """Parse and return command line arguments.
    
    Returns:
        argparse.Namespace: Parsed command line arguments with the following fields:
            - testRoot: Root test directory containing question subdirectories
            - studentCode: Comma separated list of student code files
            - codeRoot: Root directory containing student and test code
            - testCaseCode: Class containing test classes for this project
            - generateSolutions: Whether to write generated solutions to .solution file
            - edxOutput: Whether to generate edX output files 
            - gsOutput: Whether to generate GradeScope output files
            - muteOutput: Whether to mute test execution output
            - printTestCase: Whether to print each test case before running
            - runTest: Single test to run (relative to test root)
            - gradeQuestion: Single question to grade
            - noGraphics: Whether to disable graphics display for Pacman games
    """
    parser = argparse.ArgumentParser(description='Run public tests on student code')
    parser.set_defaults(generateSolutions=False, edxOutput=False, gsOutput=False, muteOutput=False, printTestCase=False, noGraphics=False)
    parser.add_argument('--test-directory',
                      dest='testRoot',
                      default='test_cases',
                      help='Root test directory which contains subdirectories corresponding to each question')
    parser.add_argument('--student-code',
                      dest='studentCode',
                      default=projectParams.STUDENT_CODE_DEFAULT,
                      help='comma separated list of student code files')
    parser.add_argument('--code-directory',
                    dest='codeRoot',
                    default="",
                    help='Root directory containing the student and testClass code')
    parser.add_argument('--test-case-code',
                      dest='testCaseCode',
                      default=projectParams.PROJECT_TEST_CLASSES,
                      help='class containing testClass classes for this project')
    parser.add_argument('--generate-solutions',
                      dest='generateSolutions',
                      action='store_true',
                      help='Write solutions generated to .solution file')
    parser.add_argument('--edx-output',
                    dest='edxOutput',
                    action='store_true',
                    help='Generate edX output files')
    parser.add_argument('--gradescope-output',
                    dest='gsOutput',
                    action='store_true',
                    help='Generate GradeScope output files')
    parser.add_argument('--mute',
                    dest='muteOutput',
                    action='store_true',
                    help='Mute output from executing tests')
    parser.add_argument('--print-tests', '-p',
                    dest='printTestCase',
                    action='store_true',
                    help='Print each test case before running them.')
    parser.add_argument('--test', '-t',
                      dest='runTest',
                      default=None,
                      help='Run one particular test. Relative to test root.')
    parser.add_argument('--question', '-q',
                    dest='gradeQuestion',
                    default=None,
                    help='Grade one particular question.')
    parser.add_argument('--no-graphics',
                    dest='noGraphics',
                    action='store_true',
                    help='No graphics display for pacman games.')
    args = parser.parse_args()
    return args
    

def confirm_generate() -> None:
    """
    Confirm whether to author/overwrite solution files.
    
    Prompts user for yes/no confirmation. Default is False.
    If user answers 'no', program exits.
    """
    print('WARNING: this action will overwrite any solution files.')
    print('Are you sure you want to proceed? (yes/no)')
    while True:
        ans = sys.stdin.readline().strip()
        if ans == 'yes':
            break
        if ans == 'no':
            sys.exit(0)
        print('please answer either "yes" or "no"')


def load_module_file(module_name: str) -> Any:
    """
    Load and return specified Python module.
    
    Args:
        module_name: Name of module to import
        
    Returns:
        Imported module object
    """
    return importlib.import_module(module_name)


def read_file(path: str, root: str = "") -> str:
    """
    Read file from disk at specified path and return contents.
    
    Args:
        path: Path to file to read
        root: Optional root directory to prepend to path
        
    Returns:
        str: Contents of file as string
    """
    with open(os.path.join(root, path), 'r') as handle:
        return handle.read()


def print_test(test_dict: Dict[str, Any], solution_dict: Dict[str, Any]) -> None:
    """
    Print result of running a test case and its solution.
    
    Args:
        test_dict: Dictionary containing test case data
        solution_dict: Dictionary containing solution data
    """
    print("Test case:")
    for line in test_dict["__raw_lines__"]:
        print(f"   | {line}")
    print("Solution:")
    for line in solution_dict["__raw_lines__"]:
        print(f"   | {line}")

def run_test(test_name: str, module_dict: Dict[str, Any], print_test_case: bool = False, display: Any = None) -> None:
    """
    Run a single test case.
    
    Args:
        test_name: Name of test to run
        module_dict: Dictionary mapping module names to module objects
        print_test_case: Whether to print test case details
        display: Display object for visualization
    """
    # Add modules to global namespace
    for module in module_dict:
        setattr(sys.modules[__name__], module, module_dict[module])

    test_dict = testParser.TestParser(f"{test_name}.test").parse()
    solution_dict = testParser.TestParser(f"{test_name}.solution").parse()
    test_out_file = os.path.join(f'{test_name}.test_output')
    test_dict['test_out_file'] = test_out_file
    test_class = getattr(projectTestClasses, test_dict['class'])

    question_class = getattr(testClasses, 'Question')
    question = question_class({'max_points': 0}, display)
    test_case = test_class(question, test_dict)

    if print_test_case:
        print_test(test_dict, solution_dict)

    # Create stub grades object
    grades = grading.Grades(projectParams.PROJECT_NAME, [(None,0)])
    test_case.execute(grades, module_dict, solution_dict)


def get_depends(test_parser: Any, test_root: str, question: str) -> List[str]:
    """
    Get all test dependencies needed to run a question.
    
    Args:
        test_parser: Parser object for reading test files
        test_root: Root directory containing test files
        question: Question name to get dependencies for
        
    Returns:
        List of test names that need to be run first
    """
    all_deps = [question]
    question_dict = test_parser.TestParser(os.path.join(test_root, question, 'CONFIG')).parse()
    if 'depends' in question_dict:
        depends = question_dict['depends'].split()
        for dependency in depends:
            # Run dependencies first
            all_deps = get_depends(test_parser, test_root, dependency) + all_deps
    return all_deps


def get_test_subdirs(test_parser: Any, test_root: str, question_to_grade: Optional[str]) -> List[str]:
    """
    Get list of test subdirectories to grade.
    
    Args:
        test_parser: Parser object for reading test files
        test_root: Root directory containing test files
        question_to_grade: Specific question to grade, if any
        
    Returns:
        List of test directory names to grade
    """
    problem_dict = test_parser.TestParser(os.path.join(test_root, 'CONFIG')).parse()
    if question_to_grade is not None:
        questions = get_depends(testParser, test_root, question_to_grade)
        if len(questions) > 1:
            print(f'Note: due to dependencies, the following tests will be run: {" ".join(questions)}')
        return questions
    if 'order' in problem_dict:
        return problem_dict['order'].split()
    return sorted(os.listdir(test_root))

def evaluate(generate_solutions: bool, test_root: str, module_dict: Dict[str, Any],
            edx_output: bool = False, mute_output: bool = False, gs_output: bool = False,
            print_test_case: bool = False, question_to_grade: Optional[str] = None, 
            display: Any = None) -> float:
    """
    Evaluate student code by running tests.
    
    Args:
        generate_solutions: Whether to generate solution files
        test_root: Root directory containing test files
        module_dict: Dictionary mapping module names to module objects
        edx_output: Whether to format output for edX
        mute_output: Whether to suppress output
        gs_output: Whether to output in gradescope format
        print_test_case: Whether to print test case details
        question_to_grade: Specific question to grade, if any
        display: Display object for visualization
        
    Returns:
        Total points earned
    """
    # Add modules to global namespace
    for module in module_dict:
        setattr(sys.modules[__name__], module, module_dict[module])

    questions = []
    question_dicts = {}
    test_subdirs = get_test_subdirs(testParser, test_root, question_to_grade)
    for question_item in test_subdirs:
        subdir_path = os.path.join(test_root, question_item)
        if not os.path.isdir(subdir_path) or question_item[0] == '.':
            continue

        # Create question object
        question_dict = testParser.TestParser(os.path.join(subdir_path, 'CONFIG')).parse()
        question_class = getattr(testClasses, question_dict['class'])
        question = question_class(question_dict, display)
        question_dicts[question_item] = question_dict

        # Load test cases into question
        tests = filter(lambda t: re.match('[^#~.].*\\.test\\Z', t), os.listdir(subdir_path))
        tests = map(lambda t: re.match('(.*)\\.test\\Z', t).group(1), tests)
        for test_item in sorted(tests):
            test_file = os.path.join(subdir_path, f'{test_item}.test')
            solution_file = os.path.join(subdir_path, f'{test_item}.solution')
            test_out_file = os.path.join(subdir_path, f'{test_item}.test_output')
            test_dict = testParser.TestParser(test_file).parse()
            if test_dict.get("disabled", "false").lower() == "true":
                continue
            test_dict['test_out_file'] = test_out_file
            test_class = getattr(projectTestClasses, test_dict['class'])
            test_case = test_class(question, test_dict)

            def grade_func1(test_case: Any, solution_file: str) -> Callable:
                if generate_solutions:
                    # Write solution file to disk
                    return lambda grades: test_case.writeSolution(module_dict, solution_file)

                # Read solution dictionary and pass as argument
                test_dict = testParser.TestParser(test_file).parse()
                solution_dict = testParser.TestParser(solution_file).parse()
                if print_test_case:
                    return lambda grades: print_test(test_dict, solution_dict) or test_case.execute(grades, module_dict, solution_dict)
                return lambda grades: test_case.execute(grades, module_dict, solution_dict)

            question.addTestCase(test_case, grade_func1(test_case, solution_file))

        def grade_func2(question: Any) -> Callable:
            return lambda grades: question.execute(grades)

        setattr(sys.modules[__name__], question_item, grade_func2(question))
        questions.append((question_item, question.getMaxPoints()))

    grades = grading.Grades(projectParams.PROJECT_NAME, questions,
                          gsOutput=gs_output, edxOutput=edx_output, muteOutput=mute_output)
    if question_to_grade is None:
        for question_item in question_dicts:
            for prereq in question_dicts[question_item].get('depends', '').split():
                grades.addPrereq(question_item, prereq)

    grades.grade(sys.modules[__name__], bonusPic = projectParams.BONUS_PIC)
    return grades.points

def get_display(graphics_by_default: bool, options: Optional[argparse.Namespace] = None) -> Any:
    """Configure and return the appropriate display for Pacman output.
    
    Args:
        graphics_by_default: Whether to use graphics display by default
        options: Command line options containing display preferences
        
    Returns:
        Either a PacmanGraphics object for graphical display or 
        NullGraphics object for text-only display
    """
    graphics = graphics_by_default
    if options is not None and options.noGraphics:
        graphics = False
    if graphics:
        return graphicsDisplay.PacmanGraphics(1, frameTime=.05)
    return textDisplay.NullGraphics()

def main() -> None:
    """Main program entry point.
    
    Parses command line arguments, loads student code modules,
    and runs tests/evaluation based on provided options.
    """
    options = read_command()
    if options.generateSolutions:
        confirm_generate()
    code_paths = options.studentCode.split(',')

    module_dict: Dict[str, Any] = {}
    for code_path in code_paths:
        module_name = re.match(r'.*?([^/]*).py', code_path).group(1)
        module_dict[module_name] = load_module_file(module_name)
    module_name = re.match(r'.*?([^/]*).py', options.testCaseCode).group(1)
    module_dict['projectTestClasses'] = load_module_file(module_name)

    if options.runTest:
        run_test(options.runTest, module_dict, printTestCase=options.printTestCase, 
                display=get_display(True, options))
    else:
        evaluate(options.generateSolutions, options.testRoot, module_dict,
                gs_output=options.gsOutput,
                edx_output=options.edxOutput, 
                mute_output=options.muteOutput,
                print_test_case=options.printTestCase,
                question_to_grade=options.gradeQuestion,
                display=get_display(options.gradeQuestion is not None, options))

if __name__ == '__main__':
    main()
