"""Test case framework for Pacman AI project autograding.

This module provides the core test case infrastructure for autograding student 
submissions in the Pacman AI project, including:
- Base TestCase class for implementing specific test types
- Question class for grouping related test cases
- Test execution and scoring functionality
- Support for test case configuration and validation

Changes by George Rudolph 30 Nov 2024:
- Added comprehensive module docstring
- Added type hints throughout
- Improved class and method documentation
- Enhanced error handling and validation
- Standardized code formatting

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
from typing import Dict, List, Any, Optional, Tuple, Union

# BEGIN SOLUTION NO PROMPT
def invertLayout(layout_text: str) -> str:
    """Invert a layout by rotating it 90 degrees clockwise.
    
    Args:
        layout_text: String representation of layout to invert
        
    Returns:
        String representation of inverted layout
    """
    # Keep lower left fix as this is hardcoded in PositionSearchProblem (gah)
    # as the goal.
    lines = [l.strip() for l in layout_text.split("\n")]
    h = len(lines)
    w = len(lines[0])
    tiles = {}
    for y, line in enumerate(lines):
        for x, tile in enumerate(line):
            # (x,y)
            # (0,0) -> (h,w)
            # (0,h) -> (0,w)
            tiles[h - 1 - y, w - 1 - x] = tile

    new_lines = []
    for y in range(w):
        new_lines.append("")
        for x in range(h):
            new_lines[-1] += tiles[x, y]
    # return layout_text
    return "\n".join(new_lines)


# END SOLUTION NO PROMPT

# Class which models a question in a project.  Note that questions have a
# maximum number of points they are worth, and are composed of a series of
# test cases
class Question(object):
    def raiseNotDefined(self) -> None:
        """Raise an error when a required method is not implemented."""
        print(f"Method not implemented: {inspect.stack()[1][3]}")
        sys.exit(1)

    def __init__(self, questionDict: Dict[str, Any], display: Any) -> None:
        """Initialize a Question object.
        
        Args:
            questionDict: Dictionary containing question parameters
            display: Display object for visualization
        """
        self.maxPoints = int(questionDict["max_points"])
        self.testCases = []
        self.display = display

    def getDisplay(self) -> Any:
        """Get the display object.
        
        Returns:
            The display object for this question
        """
        return self.display

    def getMaxPoints(self) -> int:
        """Get maximum points possible for this question.
        
        Returns:
            Maximum points possible
        """
        return self.maxPoints

    def addTestCase(self, testCase: Any, thunk: Any) -> None:
        """Add a test case to this question.
        
        Args:
            testCase: Test case object to add
            thunk: Function that accepts a grading object
        """
        self.testCases.append((testCase, thunk))

    def execute(self, grades: Any) -> None:
        """Execute this question's tests.
        
        Args:
            grades: Grading object to track scores
        """
        self.raiseNotDefined()


# Question in which all test cases must be passed in order to receive credit
class PassAllTestsQuestion(Question):
    def execute(self, grades: Any) -> None:
        """Execute all tests - must pass all to get credit.
        
        Args:
            grades: Grading object to track scores
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
    def __init__(self, questionDict: Dict[str, Any], display: Any) -> None:
        """Initialize extra credit question.
        
        Args:
            questionDict: Dictionary containing question parameters
            display: Display object for visualization
        """
        Question.__init__(self, questionDict, display)
        self.extraPoints = int(questionDict["extra_points"])

    def execute(self, grades: Any) -> None:
        """Execute all tests - must pass all to get credit plus extra credit.
        
        Args:
            grades: Grading object to track scores
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


# Question in which predict credit is given for test cases with a ``points'' property.
# All other tests are mandatory and must be passed.
class HackedPartialCreditQuestion(Question):
    def execute(self, grades: Any) -> None:
        """Execute tests with partial credit based on points property.
        
        Args:
            grades: Grading object to track scores
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

        ## FIXME: Below terrible hack to match q3's logic
        if int(points) == self.maxPoints and not passed:
            grades.assignZeroCredit()
        else:
            grades.addPoints(int(points))


class Q6PartialCreditQuestion(Question):
    """Fails any test which returns False, otherwise doesn't effect the grades object.
    Partial credit tests will add the required points."""

    def execute(self, grades: Any) -> None:
        """Execute tests, failing if any return False.
        
        Args:
            grades: Grading object to track scores
        """
        grades.assignZeroCredit()

        results = []
        for _, f in self.testCases:
            results.append(f(grades))
        if False in results:
            grades.assignZeroCredit()


class PartialCreditQuestion(Question):
    """Fails any test which returns False, otherwise doesn't effect the grades object.
    Partial credit tests will add the required points."""

    def execute(self, grades: Any) -> bool:
        """Execute tests, failing if any return False.
        
        Args:
            grades: Grading object to track scores
            
        Returns:
            False if any test fails, otherwise doesn't return
        """
        grades.assignZeroCredit()

        for _, f in self.testCases:
            if not f(grades):
                grades.assignZeroCredit()
                grades.fail("Tests failed.")
                return False


class NumberPassedQuestion(Question):
    """Grade is the number of test cases passed."""

    def execute(self, grades: Any) -> None:
        """Execute tests and add points for each passed test.
        
        Args:
            grades: Grading object to track scores
        """
        grades.addPoints([f(grades) for _, f in self.testCases].count(True))


# BEGIN SOLUTION NO PROMPT
from testParser import emitTestDict

# END SOLUTION NO PROMPT

# Template modeling a generic test case
class TestCase(object):
    def raiseNotDefined(self) -> None:
        """Raise an error when a required method is not implemented."""
        print(f"Method not implemented: {inspect.stack()[1][3]}")
        sys.exit(1)

    def getPath(self) -> str:
        """Get path for this test case.
        
        Returns:
            Path string for this test case
        """
        return self.path

    def __init__(self, question: Question, testDict: Dict[str, Any]) -> None:
        """Initialize a test case.
        
        Args:
            question: Question object this test belongs to
            testDict: Dictionary containing test parameters
        """
        self.question = question
        self.testDict = testDict
        self.path = testDict["path"]
        self.messages = []

    def __str__(self) -> str:
        """Get string representation of test case.
        
        Returns:
            String representation
        """
        self.raiseNotDefined()

    def execute(self, grades: Any, moduleDict: Dict[str, Any], solutionDict: Dict[str, Any]) -> None:
        """Execute this test case.
        
        Args:
            grades: Grading object to track scores
            moduleDict: Dictionary of student modules
            solutionDict: Dictionary of solution data
        """
        self.raiseNotDefined()

    def writeSolution(self, moduleDict: Dict[str, Any], filePath: str) -> bool:
        """Write solution for this test to file.
        
        Args:
            moduleDict: Dictionary of student modules
            filePath: Path to write solution file
            
        Returns:
            True if solution written successfully
        """
        self.raiseNotDefined()
        return True

    # Tests should call the following messages for grading
    # to ensure a uniform format for test output.
    #
    # TODO: this is hairy, but we need to fix grading.py's interface
    # to get a nice hierarchical project - question - test structure,
    # then these should be moved into Question proper.
    def testPass(self, grades: Any) -> bool:
        """Record that test passed.
        
        Args:
            grades: Grading object to track scores
            
        Returns:
            True to indicate test passed
        """
        grades.addMessage(f"PASS: {self.path}")
        for line in self.messages:
            grades.addMessage(f"    {line}")
        return True

    def testFail(self, grades: Any) -> bool:
        """Record that test failed.
        
        Args:
            grades: Grading object to track scores
            
        Returns:
            False to indicate test failed
        """
        grades.addMessage(f"FAIL: {self.path}")
        for line in self.messages:
            grades.addMessage(f"    {line}")
        return False

    # This should really be question level?
    #
    def testPartial(self, grades: Any, points: float, maxPoints: float) -> bool:
        """Record partial credit for test.
        
        Args:
            grades: Grading object to track scores
            points: Points earned
            maxPoints: Maximum points possible
            
        Returns:
            True to indicate test completed
        """
        grades.addPoints(points)
        extraCredit = max(0, points - maxPoints)
        regularCredit = points - extraCredit

        grades.addMessage(
            f"{'PASS' if points >= maxPoints else 'FAIL'}: {self.path} ({regularCredit} of {maxPoints} points)"
        )
        if extraCredit > 0:
            grades.addMessage(f"EXTRA CREDIT: {extraCredit} points")

        for line in self.messages:
            grades.addMessage(f"    {line}")

        return True

    def addMessage(self, message: str) -> None:
        """Add a message to test output.
        
        Args:
            message: Message string to add
        """
        self.messages.extend(message.split("\n"))

    # BEGIN SOLUTION NO PROMPT
    def createPublicVersion(self) -> None:
        """Create public version of this test case."""
        self.raiseNotDefined()

    def emitPublicVersion(self, filePath: str) -> None:
        """Write public version of test to file.
        
        Args:
            filePath: Path to write public version
        """
        with open(filePath, "w") as handle:
            emitTestDict(self.testDict, handle)

    # END SOLUTION NO PROMPT
