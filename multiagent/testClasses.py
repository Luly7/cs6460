"""Test classes for the Pacman AI projects.

This module provides the core testing infrastructure used in the autograding system.
It defines base classes for questions and test cases that are used to evaluate
student submissions. The testing framework supports different types of tests
and grading criteria through an extensible class hierarchy.

Originally developed at UC Berkeley for CS188 Intro to AI.
Modified by George Rudolph on 12 Nov 2024:
- Added type hints throughout the codebase
- Improved documentation and docstrings
- Verified compatibility with Python 3.13

Original Licensing Information:  
You are free to use or extend these projects for educational purposes provided that
(1) you do not distribute or publish solutions
(2) you retain this notice
(3) you provide clear attribution to UC Berkeley, including a link to http://ai.berkeley.edu

Original Attribution:
The Pacman AI projects were developed at UC Berkeley.
Core projects and autograders created by John DeNero (denero@cs.berkeley.edu) 
and Dan Klein (klein@cs.berkeley.edu).
Student side autograding added by Brad Miller, Nick Hay, and Pieter Abbeel (pabbeel@cs.berkeley.edu).
"""


from typing import Any, Callable, List, Tuple, Dict
import inspect
import re
import sys


class Question:
    """Models a question in a project.
    
    A Question represents a graded component that has a maximum point value
    and consists of a series of test cases that must be executed to determine
    the score.
    
    Attributes:
        maxPoints: Maximum points possible for this question
        testCases: List of (testCase, test_function) tuples
        display: Display interface for showing output
    """

    def raiseNotDefined(self) -> None:
        """Raises an error when a required method is not implemented."""
        print(f'Method not implemented: {inspect.stack()[1][3]}')
        sys.exit(1)

    def __init__(self, questionDict: dict, display: Any) -> None:
        """Initialize a Question with points and display.
        
        Args:
            questionDict: Dictionary containing question metadata including max_points
            display: Display interface for showing output
        """
        self.maxPoints = int(questionDict['max_points'])
        self.testCases: List[Tuple[Any, Callable]] = []
        self.display = display

    def getDisplay(self) -> Any:
        """Get the display interface.
        
        Returns:
            The display interface object
        """
        return self.display

    def getMaxPoints(self) -> int:
        """Get maximum points possible.
        
        Returns:
            Maximum points possible for this question
        """
        return self.maxPoints

    def addTestCase(self, testCase: Any, thunk: Callable[[Any], bool]) -> None:
        """Add a test case to this question.
        
        Args:
            testCase: The test case to add
            thunk: Function that accepts a grading object and returns bool
        """
        self.testCases.append((testCase, thunk))

    def execute(self, grades: Any) -> None:
        """Execute all test cases and assign grade.
        
        Args:
            grades: Grading object to record results
        """
        self.raiseNotDefined()

# Question in which all test cases must be passed in order to receive credit
class PassAllTestsQuestion(Question):
    """Question that requires all test cases to pass to receive any credit.
    
    This question type assigns zero credit if any test fails, and full credit
    only if all tests pass. There is no partial credit.
    """

    def execute(self, grades: Any) -> None:
        """Execute all test cases and assign grade based on all-or-nothing criteria.
        
        Args:
            grades: Grading object to record test results and assign credit
        """
        # TODO: is this the right way to use grades? The autograder doesn't seem to use it.
        testsFailed = False
        grades.assignZeroCredit()
        for _, f in self.testCases:
            if not f(grades):
                testsFailed = True
        if testsFailed:
            grades.fail("Tests failed.")
        else:
            grades.assignFullCredit()


class ExtraCreditPassAllTestsQuestion(Question):
    """Question that awards extra credit points if all test cases pass.
    
    This question type assigns zero credit if any test fails. If all tests pass,
    it awards both full credit and additional extra credit points specified in
    the question dictionary.
    """

    def __init__(self, questionDict: Dict[str, Any], display: Any) -> None:
        """Initialize the extra credit question.
        
        Args:
            questionDict: Dictionary containing question properties including 'extra_points'
            display: Display object for visualization
        """
        Question.__init__(self, questionDict, display)
        self.extraPoints = int(questionDict['extra_points'])

    def execute(self, grades: Any) -> None:
        """Execute all test cases and assign grade plus extra credit if all pass.
        
        Args:
            grades: Grading object to record test results and assign credit
        """
        # TODO: is this the right way to use grades? The autograder doesn't seem to use it.
        testsFailed = False
        grades.assignZeroCredit()
        for _, f in self.testCases:
            if not f(grades):
                testsFailed = True
        if testsFailed:
            grades.fail("Tests failed.")
        else:
            grades.assignFullCredit()
            grades.addPoints(self.extraPoints)

class HackedPartialCreditQuestion(Question):
    """Question that awards partial credit based on test cases with points property.
    
    Test cases can specify points to award if they pass. Any test case without
    a points property is considered mandatory and must pass. Total points are 
    awarded only if all mandatory tests pass.
    """

    def execute(self, grades: Any) -> None:
        """Execute test cases and assign partial credit.
        
        Args:
            grades: Grading object to record test results and assign credit
        """
        # TODO: is this the right way to use grades? The autograder doesn't seem to use it.
        grades.assignZeroCredit()

        points = 0
        passed = True
        for testCase, f in self.testCases:
            testResult = f(grades)
            if "points" in testCase.testDict:
                if testResult:
                    points += float(testCase.testDict["points"])
            else:
                passed = passed and testResult

        # FIXME: Below terrible hack to match q3's logic
        if int(points) == self.maxPoints and not passed:
            grades.assignZeroCredit()
        else:
            grades.addPoints(int(points))


class Q6PartialCreditQuestion(Question):
    """Question that fails if any test returns False, otherwise preserves grades.
    
    This question type allows for partial credit by letting individual test cases
    add points to the grade. The entire question fails (zero credit) if any test 
    returns False, but passing tests can contribute their specified points.
    """

    def execute(self, grades: Any) -> None:
        """Execute test cases and assign credit based on results.
        
        Args:
            grades: Grading object to record test results and assign credit
        """
        grades.assignZeroCredit()

        results = []
        for _, f in self.testCases:
            results.append(f(grades))
        if False in results:
            grades.assignZeroCredit()


class PartialCreditQuestion(Question):
    """Question that fails if any test returns False, otherwise preserves grades.
    
    This question type allows tests to add points for partial credit, but fails
    the entire question (zero credit) if any individual test returns False.
    
    Inherits from Question base class.
    """

    def execute(self, grades: Any) -> bool:
        """Execute test cases and assign credit based on results.
        
        Args:
            grades: Grading object to record test results and assign credit
            
        Returns:
            False if any test fails, implicitly True otherwise
        """
        grades.assignZeroCredit()

        for _, f in self.testCases:
            if not f(grades):
                grades.assignZeroCredit()
                grades.fail(f"Tests failed.")
                return False


class NumberPassedQuestion(Question):
    """Question that assigns points based on number of passing test cases.
    
    The grade for this question type is determined by counting the number of test cases
    that return True. Each passing test adds one point to the total grade.
    
    Inherits from Question base class.
    """

    def execute(self, grades: Any) -> None:
        """Execute test cases and assign points for each passing test.
        
        Args:
            grades: Grading object to record test results and assign credit
        """
        grades.addPoints([f(grades) for _, f in self.testCases].count(True))


# Template modeling a generic test case
class TestCase(object):
    """Base class for test cases used in autograding.
    
    This class provides the template and common functionality for test cases.
    Specific test case types should inherit from this class and implement
    the abstract methods.
    """

    def raiseNotDefined(self) -> None:
        """Raise error for unimplemented methods."""
        print(f'Method not implemented: {inspect.stack()[1][3]}')
        sys.exit(1)

    def getPath(self) -> str:
        """Get the test case file path.
        
        Returns:
            Path to the test case file
        """
        return self.path

    def __init__(self, question: Any, testDict: dict) -> None:
        """Initialize test case with question and test dictionary.
        
        Args:
            question: Question object this test case belongs to
            testDict: Dictionary containing test case configuration
        """
        self.question = question
        self.testDict = testDict
        self.path = testDict['path']
        self.messages = []

    def __str__(self) -> str:
        """Return string representation of test case.
        
        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        self.raiseNotDefined()

    def execute(self, grades: Any, moduleDict: dict, solutionDict: dict) -> None:
        """Execute the test case.
        
        Args:
            grades: Grading object to record results
            moduleDict: Dictionary containing student code modules
            solutionDict: Dictionary containing solution code
            
        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        self.raiseNotDefined()

    def writeSolution(self, moduleDict: dict, filePath: str) -> bool:
        """Write solution for this test case.
        
        Args:
            moduleDict: Dictionary containing student code modules
            filePath: Path to write solution file
            
        Returns:
            True if solution was written successfully
            
        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        self.raiseNotDefined()
        return True

    def testPass(self, grades: Any) -> bool:
        """Record a passing test result.
        
        Args:
            grades: Grading object to record results
            
        Returns:
            True to indicate test passed
        """
        grades.addMessage(f'PASS: {self.path}')
        for line in self.messages:
            grades.addMessage(f'    {line}')
        return True

    def testFail(self, grades: Any) -> bool:
        """Record a failing test result.
        
        Args:
            grades: Grading object to record results
            
        Returns:
            False to indicate test failed
        """
        grades.addMessage(f'FAIL: {self.path}')
        for line in self.messages:
            grades.addMessage(f'    {line}')
        return False

    def testPartial(self, grades: Any, points: float, maxPoints: float) -> bool:
        """Record a partially passing test result with partial credit.
        
        Args:
            grades: Grading object to record results
            points: Points earned on this test
            maxPoints: Maximum possible points for this test
            
        Returns:
            True to indicate test completed
        """
        grades.addPoints(points)
        extraCredit = max(0, points - maxPoints)
        regularCredit = points - extraCredit

        grades.addMessage(f'{"PASS" if points >= maxPoints else "FAIL"}: {self.path} ({regularCredit} of {maxPoints} points)')
        if extraCredit > 0:
            grades.addMessage(f'EXTRA CREDIT: {extraCredit} points')

        for line in self.messages:
            grades.addMessage(f'    {line}')

        return True

    def addMessage(self, message: str) -> None:
        """Add a message to be displayed in test output.
        
        Args:
            message: Message text to add, can contain newlines
        """
        self.messages.extend(message.split('\n'))
