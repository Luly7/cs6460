"""Test classes for grading student project submissions.

This module provides base classes and utilities for implementing test cases
and grading student project submissions. It includes classes for representing
questions, test cases, and managing test execution and grading.

Original Licensing Information:
You are free to use or extend these projects for educational purposes provided that
(1) you do not distribute or publish solutions, (2) you retain this notice, and
(3) you provide clear attribution to UC Berkeley, including a link to 
http://ai.berkeley.edu.

Original Attribution:
The Pacman AI projects were developed at UC Berkeley. The core projects and
autograders were primarily created by John DeNero (denero@cs.berkeley.edu) and
Dan Klein (klein@cs.berkeley.edu). Student side autograding was added by
Brad Miller, Nick Hay, and Pieter Abbeel (pabbeel@cs.berkeley.edu).

Author: George Rudolph
Date: 9 Nov 2024
Changes:
- Added type hints throughout
- Improved documentation and docstrings
- f-strings used for string formatting
"""

import inspect
import re
import sys
from typing import Dict, List, Tuple, Any, Callable, Optional


class Question:
    """
    Base class representing a question in a project.
    Questions have a maximum number of points they 
    are worth and are composed of a series of test cases.

    Attributes:
        maxPoints (int): Maximum points possible for this question
        testCases (list): List of (testCase, function) tuples for this question
        display: Display object for showing question output

    Methods:
        getDisplay(): Get the display object
        getMaxPoints(): Get maximum points possible
        addTestCase(): Add a test case and grading function
        execute(): Run all test cases (must be implemented by subclasses)
    """

    def raiseNotDefined(self) -> None:
        """Raise error when required method not implemented."""
        print(f'Method not implemented: {inspect.stack()[1][3]}')
        sys.exit(1)

    def __init__(self, questionDict: Dict[str, Any], display: Any) -> None:
        """
        Initialize Question with points and display.

        Args:
            questionDict: Dictionary containing question parameters
            display: Display object for output
        """
        self.maxPoints = int(questionDict['max_points'])
        self.testCases: List[Tuple[Any, Callable]] = []
        self.display = display

    def getDisplay(self) -> Any:
        """Return the display object."""
        return self.display

    def getMaxPoints(self) -> int:
        """Return the maximum points possible."""
        return self.maxPoints

    def addTestCase(self, testCase: Any, thunk: Callable) -> None:
        """
        Add a test case and its grading function.

        Args:
            testCase: Test case object
            thunk: Function that accepts a grading object and returns bool
        """
        self.testCases.append((testCase, thunk))

    def execute(self, grades: Any) -> None:
        """
        Execute all test cases for this question.
        Must be implemented by subclasses.

        Args:
            grades: Grading object to track scores
        """
        self.raiseNotDefined()

class PassAllTestsQuestion(Question):
    """
    Question type that requires all test cases to pass to receive credit.
    
    If any test case fails, zero credit is assigned. If all pass, full credit
    is assigned.
    """

    def execute(self, grades: 'Grades') -> None:
        """
        Execute all test cases and assign credit based on results.
        
        Args:
            grades: Grading object to track scores and assign credit
            
        Returns:
            None
        """
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
    """
    Question type that awards extra credit points if all test cases pass.
    
    If any test case fails, zero credit is assigned. If all pass, full credit
    plus extra credit points are assigned.
    
    Args:
        questionDict: Dictionary containing question configuration
        display: Display object for output
    """
    def __init__(self, questionDict: Dict[str, Any], display: Any) -> None:
        Question.__init__(self, questionDict, display)
        self.extraPoints = int(questionDict['extra_points'])

    def execute(self, grades: 'Grades') -> None:
        """
        Execute all test cases and assign credit based on results.
        
        Args:
            grades: Grading object to track scores and assign credit
            
        Returns:
            None
        """
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
    """
    Question type that awards partial credit based on test cases with points property.
    
    Test cases can specify points they are worth in their testDict. Test cases without
    points are treated as mandatory and must all pass. If any mandatory test fails,
    zero credit is assigned even if points were earned from other tests.
    
    Inherits from Question base class.
    """

    def execute(self, grades: 'Grades') -> None:
        """
        Execute test cases and assign credit based on results.
        
        Test cases with 'points' property award those points if passed.
        Test cases without 'points' must all pass to get any credit.
        
        Args:
            grades: Grading object to track scores and assign credit
            
        Returns:
            None
        """
        grades.assignZeroCredit()

        points = 0.0
        passed = True
        for testCase, f in self.testCases:
            testResult = f(grades)
            if "points" in testCase.testDict:
                if testResult:
                    points += float(testCase.testDict["points"])
            else:
                passed = passed and testResult

        # Only award points if all mandatory (non-points) tests pass
        if int(points) == self.maxPoints and not passed:
            grades.assignZeroCredit()
        else:
            grades.addPoints(int(points))

class Q6PartialCreditQuestion(Question):
    """
    Question type that fails any test returning False, otherwise preserves grades.
    
    Tests can award partial credit points if they pass. If any test fails by returning
    False, zero credit is assigned regardless of other test results.
    
    Inherits from Question base class.
    """

    def execute(self, grades: 'Grades') -> None:
        """
        Execute test cases and assign credit based on results.
        
        Runs all test cases and tracks their results. If any test returns False,
        assigns zero credit. Otherwise preserves existing grade state to allow
        partial credit from individual tests.
        
        Args:
            grades: Grading object to track scores and assign credit
            
        Returns:
            None
        """
        grades.assignZeroCredit()

        results = []
        for _, f in self.testCases:
            results.append(f(grades))
        if False in results:
            grades.assignZeroCredit()

class PartialCreditQuestion(Question):
    """
    Question type that fails any test returning False, otherwise preserves grades.
    
    Tests can award partial credit points if they pass. If any test returns False,
    zero credit is assigned and the question is marked as failed.
    
    Inherits from Question base class.
    """

    def execute(self, grades: 'Grades') -> bool:
        """
        Execute test cases and assign credit based on results.
        
        Runs test cases until a failure is encountered. If any test returns False,
        assigns zero credit and marks question as failed. Otherwise preserves existing 
        grade state to allow partial credit from individual tests.
        
        Args:
            grades: Grading object to track scores and assign credit
            
        Returns:
            bool: False if any test failed, implicitly True otherwise
        """
        grades.assignZeroCredit()

        for _, f in self.testCases:
            if not f(grades):
                grades.assignZeroCredit()
                grades.fail("Tests failed.")
                return False


class NumberPassedQuestion(Question):
    """
    Question type where grade is based on number of passing tests.
    
    Awards points equal to the count of test cases that return True.
    Each passing test adds one point to the total score.
    
    Inherits from Question base class.
    """

    def execute(self, grades: 'Grades') -> None:
        """
        Execute test cases and award points for passing tests.
        
        Runs all test cases and counts how many return True. Adds that count
        as points to the grade.
        
        Args:
            grades: Grading object to track scores and assign credit
            
        Returns:
            None
        """
        grades.addPoints([f(grades) for _, f in self.testCases].count(True))

# Template modeling a generic test case
class TestCase(object):
    """
    Base class for test cases.
    
    Provides template methods and utilities for implementing test cases.
    Subclasses should override execute(), writeSolution() and __str__().
    
    Attributes:
        question: The Question object this test belongs to
        testDict: Dictionary containing test configuration 
        path: Path identifying this test case
        messages: List of message strings from test execution
    """

    def raiseNotDefined(self) -> None:
        """Raise error for unimplemented methods."""
        print(f'Method not implemented: {inspect.stack()[1][3]}')
        sys.exit(1)

    def getPath(self) -> str:
        """Get the path identifying this test case.
        
        Returns:
            str: Test case path
        """
        return self.path

    def __init__(self, question: 'Question', testDict: Dict[str, Any]) -> None:
        """Initialize test case with question and config.
        
        Args:
            question: Question object this test belongs to
            testDict: Dictionary containing test configuration
        """
        self.question = question
        self.testDict = testDict
        self.path = testDict['path']
        self.messages: List[str] = []

    def __str__(self) -> str:
        """Get string representation of test case.
        
        Returns:
            str: String representation
        
        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        self.raiseNotDefined()

    def execute(self, grades: 'Grades', moduleDict: Dict[str, Any], solutionDict: Dict[str, Any]) -> bool:
        """Execute the test case.
        
        Args:
            grades: Grading object to track scores
            moduleDict: Dictionary containing student code modules
            solutionDict: Dictionary containing solution code
            
        Returns:
            bool: True if test passes, False otherwise
            
        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        self.raiseNotDefined()

    def writeSolution(self, moduleDict: Dict[str, Any], filePath: str) -> bool:
        """Write solution for test to file.
        
        Args:
            moduleDict: Dictionary containing student code modules
            filePath: Path to write solution file
            
        Returns:
            bool: True if solution written successfully
            
        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        self.raiseNotDefined()
        return True

    def testPass(self, grades: 'Grades') -> bool:
        """Record test case passed.
        
        Args:
            grades: Grading object to track scores
            
        Returns:
            bool: Always returns True
        """
        grades.addMessage(f'PASS: {self.path}')
        for line in self.messages:
            grades.addMessage(f'    {line}')
        return True

    def testFail(self, grades: 'Grades') -> bool:
        """Record test case failed.
        
        Args:
            grades: Grading object to track scores
            
        Returns:
            bool: Always returns False
        """
        grades.addMessage(f'FAIL: {self.path}')
        for line in self.messages:
            grades.addMessage(f'    {line}')
        return False

    def testPartial(self, grades: 'Grades', points: float, maxPoints: float) -> bool:
        """Record partial credit for test case.
        
        Args:
            grades: Grading object to track scores
            points: Points earned on test
            maxPoints: Maximum points possible
            
        Returns:
            bool: Always returns True
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
        """Add message from test execution.
        
        Args:
            message: Message string to add
        """
        self.messages.extend(message.split('\n'))
