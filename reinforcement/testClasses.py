"""
Test classes for autograding framework.

This module provides classes for managing test cases, questions, and grading in the
autograding framework. It includes different question types that handle grading
in various ways (all-or-nothing, partial credit, etc) and a generic test case
template. The framework supports automated testing and grading of student code
submissions.

Classes:
    Question: Base class defining core question functionality
    PassAllTestsQuestion: Question requiring all tests to pass for credit
    ExtraCreditPassAllTestsQuestion: Question offering bonus points
    HackedPartialCreditQuestion: Question with point-based partial credit
    Q6PartialCreditQuestion: Special partial credit handler for Q6
    PartialCreditQuestion: Standard partial credit implementation
    NumberPassedQuestion: Question scored by number of passing tests
    TestCase: Template class for individual test case implementation

Functions:
    None

Python Version: 3.13
Last Modified: 24 Nov 2024
Modified by: George Rudolph

Changes:
- Added comprehensive module docstring
- Added function section to docstring
- Improved class descriptions
- Verified Python 3.13 compatibility
- Added modifier attribution

# testClasses.py
# -------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).
"""

import inspect
import re
import sys
from typing import List, Dict, Tuple, Any, Optional, Callable


class Question:
    """Base class for autograder questions."""

    def raiseNotDefined(self) -> None:
        """Raise error for unimplemented methods."""
        print(f'Method not implemented: {inspect.stack()[1][3]}')
        sys.exit(1)

    def __init__(self, questionDict: Dict[str, Any], display: Any) -> None:
        """Initialize Question with points and display.
        
        Args:
            questionDict: Dictionary containing question parameters
            display: Display object for output
        """
        self.maxPoints = int(questionDict['max_points'])
        self.testCases: List[Tuple[Any, Callable]] = []
        self.display = display

    def getDisplay(self) -> Any:
        """Get the display object.
        
        Returns:
            The display object for this question
        """
        return self.display

    def getMaxPoints(self) -> int:
        """Get maximum points possible.
        
        Returns:
            Maximum points that can be earned
        """
        return self.maxPoints

    def addTestCase(self, testCase: Any, thunk: Callable) -> None:
        """Add a test case to this question.
        
        Args:
            testCase: The test case object
            thunk: Function that executes the test case
        """
        self.testCases.append((testCase, thunk))

    def execute(self, grades: Any) -> None:
        """Execute all test cases.
        
        Args:
            grades: Grading object to record results
        """
        self.raiseNotDefined()


class PassAllTestsQuestion(Question):
    """Question requiring all test cases to pass for credit."""

    def execute(self, grades: Any) -> None:
        """Execute tests, assigning full credit only if all pass.
        
        Args:
            grades: Grading object to record results
        """
        # TODO: is this the right way to use grades?  The autograder doesn't seem to use it.
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
    """Question with potential extra credit points."""
    
    def __init__(self, questionDict: Dict[str, Any], display: Any) -> None:
        """Initialize with extra credit points.
        
        Args:
            questionDict: Dictionary containing question parameters
            display: Display object for output
        """
        Question.__init__(self, questionDict, display)
        self.extraPoints = int(questionDict['extra_points'])

    def execute(self, grades: Any) -> None:
        """Execute tests, including extra credit if all pass.
        
        Args:
            grades: Grading object to record results
        """
        # TODO: is this the right way to use grades?  The autograder doesn't seem to use it.
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
    """Question with partial credit based on points property."""

    def execute(self, grades: Any) -> None:
        """Execute tests, assigning partial credit based on points.
        
        Args:
            grades: Grading object to record results
        """
        # TODO: is this the right way to use grades?  The autograder doesn't seem to use it.
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
    """Special partial credit question for Q6."""

    def execute(self, grades: Any) -> None:
        """Execute tests, failing if any return False.
        
        Args:
            grades: Grading object to record results
        """
        grades.assignZeroCredit()

        results = []
        for _, f in self.testCases:
            results.append(f(grades))
        if False in results:
            grades.assignZeroCredit()


class PartialCreditQuestion(Question):
    """Standard partial credit question."""

    def execute(self, grades: Any) -> None:
        """Execute tests, failing immediately if any return False.
        
        Args:
            grades: Grading object to record results
        """
        grades.assignZeroCredit()

        for _, f in self.testCases:
            if not f(grades):
                grades.assignZeroCredit()
                grades.fail("Tests failed.")
                return False


class NumberPassedQuestion(Question):
    """Question graded on number of test cases passed."""

    def execute(self, grades: Any) -> None:
        """Execute tests, points equal number passed.
        
        Args:
            grades: Grading object to record results
        """
        grades.addPoints([f(grades) for _, f in self.testCases].count(True))


class TestCase:
    """Template class for individual test cases."""

    def raiseNotDefined(self) -> None:
        """Raise error for unimplemented methods."""
        print(f'Method not implemented: {inspect.stack()[1][3]}')
        sys.exit(1)

    def getPath(self) -> str:
        """Get test case path.
        
        Returns:
            Path to this test case
        """
        return self.path

    def __init__(self, question: Question, testDict: Dict[str, Any]) -> None:
        """Initialize test case.
        
        Args:
            question: Question this test belongs to
            testDict: Dictionary of test parameters
        """
        self.question = question
        self.testDict = testDict
        self.path = testDict['path']
        self.messages: List[str] = []

    def __str__(self) -> str:
        """Get string representation.
        
        Returns:
            String representation of test case
        """
        self.raiseNotDefined()

    def execute(self, grades: Any, moduleDict: Dict[str, Any], solutionDict: Dict[str, Any]) -> None:
        """Execute this test case.
        
        Args:
            grades: Grading object to record results
            moduleDict: Dictionary of student's code modules
            solutionDict: Dictionary of solution modules
        """
        self.raiseNotDefined()

    def writeSolution(self, moduleDict: Dict[str, Any], filePath: str) -> bool:
        """Write solution for this test case.
        
        Args:
            moduleDict: Dictionary of student's code modules
            filePath: Path to write solution
            
        Returns:
            True if solution successfully written
        """
        self.raiseNotDefined()
        return True

    def testPass(self, grades: Any) -> bool:
        """Record that test passed.
        
        Args:
            grades: Grading object to record results
            
        Returns:
            True to indicate pass
        """
        grades.addMessage(f'PASS: {self.path}')
        for line in self.messages:
            grades.addMessage(f'    {line}')
        return True

    def testFail(self, grades: Any) -> bool:
        """Record that test failed.
        
        Args:
            grades: Grading object to record results
            
        Returns:
            False to indicate failure
        """
        grades.addMessage(f'FAIL: {self.path}')
        for line in self.messages:
            grades.addMessage(f'    {line}')
        return False

    def testPartial(self, grades: Any, points: float, maxPoints: float) -> bool:
        """Record partial credit for test.
        
        Args:
            grades: Grading object to record results
            points: Points earned
            maxPoints: Maximum points possible
            
        Returns:
            True to indicate completion
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
        """Add message to test output.
        
        Args:
            message: Message to add
        """
        self.messages.extend(message.split('\n'))
