"""
Test classes for reinforcement learning algorithms.

This module provides test classes for evaluating value iteration and related 
reinforcement learning algorithms in the Pacman environment. It includes functionality 
for running agents, comparing outputs against expected results, and generating solution 
files. The module supports automated testing of student implementations of value 
iteration, Q-learning, and approximate Q-learning agents.

Classes:
    ValueIterationTest: Tests value iteration agent implementations
    ApproximateQLearningTest: Tests approximate Q-learning implementations
    QLearningTest: Tests tabular Q-learning agent implementations
    EpsilonGreedyTest: Tests epsilon-greedy action selection

Functions:
    None

Python Version: 3.13
Last Modified: 24 Nov 2024
Modified by: George Rudolph

Changes:
- Added comprehensive module docstring
- Added missing class descriptions
- Improved docstring formatting
- Verified Python 3.13 compatibility
- Added modifier attribution

# reinforcementTestClasses.py
# ---------------------------
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



import testClasses
import random, math, traceback, sys, os
import layout, textDisplay, pacman, gridworld
import time
from util import Counter, TimeoutFunction, FixedRandom, Experiences
from collections import defaultdict
from pprint import PrettyPrinter
from hashlib import sha1
from functools import reduce
from typing import Dict, List, Tuple, Any, Optional

pp = PrettyPrinter()
VERBOSE = False

import gridworld

LIVINGREWARD = -0.1
NOISE = 0.2

class ValueIterationTest(testClasses.TestCase):
    """Test class for evaluating value iteration agent implementations."""

    def __init__(self, question: Any, testDict: Dict[str, Any]) -> None:
        """Initialize value iteration test case.
        
        Args:
            question: Question object this test belongs to
            testDict: Dictionary containing test parameters
        """
        super(ValueIterationTest, self).__init__(question, testDict)
        self.discount = float(testDict['discount'])
        self.grid = gridworld.Gridworld(parseGrid(testDict['grid']))
        iterations = int(testDict['valueIterations'])
        if 'noise' in testDict: self.grid.setNoise(float(testDict['noise']))
        if 'livingReward' in testDict: self.grid.setLivingReward(float(testDict['livingReward']))
        maxPreIterations = 10
        self.numsIterationsForDisplay = list(range(min(iterations, maxPreIterations)))
        self.testOutFile = testDict['test_out_file']
        if maxPreIterations < iterations:
            self.numsIterationsForDisplay.append(iterations)

    def writeFailureFile(self, string: str) -> None:
        """Write failure output to file.
        
        Args:
            string: Failure output to write
        """
        with open(self.testOutFile, 'w') as handle:
            handle.write(string)

    def removeFailureFileIfExists(self) -> None:
        """Remove the failure output file if it exists."""
        if os.path.exists(self.testOutFile):
            os.remove(self.testOutFile)

    def execute(self, grades: Any, moduleDict: Dict[str, Any], solutionDict: Dict[str, Any]) -> bool:
        """Execute the test case.
        
        Args:
            grades: Grading object to record results
            moduleDict: Dictionary containing student code modules
            solutionDict: Dictionary containing correct solutions
            
        Returns:
            True if test passes, False otherwise
        """
        failureOutputFileString = ''
        failureOutputStdString = ''
        for n in self.numsIterationsForDisplay:
            checkPolicy = (n == self.numsIterationsForDisplay[-1])
            testPass, stdOutString, fileOutString = self.executeNIterations(grades, moduleDict, solutionDict, n, checkPolicy)
            failureOutputStdString += stdOutString
            failureOutputFileString += fileOutString
            if not testPass:
                self.addMessage(failureOutputStdString)
                self.addMessage(f'For more details to help you debug, see test output file {self.testOutFile}\n\n')
                self.writeFailureFile(failureOutputFileString)
                return self.testFail(grades)
        self.removeFailureFileIfExists()
        return self.testPass(grades)

    def executeNIterations(self, grades: Any, moduleDict: Dict[str, Any], solutionDict: Dict[str, Any], n: int, checkPolicy: bool) -> Tuple[bool, str, str]:
        """Execute n iterations of value iteration.
        
        Args:
            grades: Grading object to record results
            moduleDict: Dictionary containing student code modules  
            solutionDict: Dictionary containing correct solutions
            n: Number of iterations to run
            checkPolicy: Whether to check policy on this iteration
            
        Returns:
            Tuple of (passed, stdout string, file output string)
        """
        testPass = True
        valuesPretty, qValuesPretty, actions, policyPretty = self.runAgent(moduleDict, n)
        stdOutString = ''
        fileOutString = ''
        valuesKey = f"values_k_{n}"
        if self.comparePrettyValues(valuesPretty, solutionDict[valuesKey]):
            fileOutString += f"Values at iteration {n} are correct.\n"
            fileOutString += f"   Student/correct solution:\n {self.prettyValueSolutionString(valuesKey, valuesPretty)}\n"
        else:
            testPass = False
            outString = f"Values at iteration {n} are NOT correct.\n"
            outString += f"   Student solution:\n {self.prettyValueSolutionString(valuesKey, valuesPretty)}\n"
            outString += f"   Correct solution:\n {self.prettyValueSolutionString(valuesKey, solutionDict[valuesKey])}\n"
            stdOutString += outString
            fileOutString += outString
        for action in actions:
            qValuesKey = f'q_values_k_{n}_action_{action}'
            qValues = qValuesPretty[action]
            if self.comparePrettyValues(qValues, solutionDict[qValuesKey]):
                fileOutString += f"Q-Values at iteration {n} for action {action} are correct.\n"
                fileOutString += f"   Student/correct solution:\n {self.prettyValueSolutionString(qValuesKey, qValues)}\n"
            else:
                testPass = False
                outString = f"Q-Values at iteration {n} for action {action} are NOT correct.\n"
                outString += f"   Student solution:\n {self.prettyValueSolutionString(qValuesKey, qValues)}\n"
                outString += f"   Correct solution:\n {self.prettyValueSolutionString(qValuesKey, solutionDict[qValuesKey])}\n"
                stdOutString += outString
                fileOutString += outString
        if checkPolicy:
            if not self.comparePrettyValues(policyPretty, solutionDict['policy']):
                testPass = False
                outString = "Policy is NOT correct.\n"
                outString += f"   Student solution:\n {self.prettyValueSolutionString('policy', policyPretty)}\n"
                outString += f"   Correct solution:\n {self.prettyValueSolutionString('policy', solutionDict['policy'])}\n"
                stdOutString += outString
                fileOutString += outString
        return testPass, stdOutString, fileOutString

    def writeSolution(self, moduleDict: Dict[str, Any], filePath: str) -> bool:
        """Write solution for this test to a file.
        
        Args:
            moduleDict: Dictionary containing student code modules
            filePath: Path to write solution file
            
        Returns:
            True if successful
        """
        with open(filePath, 'w') as handle:
            policyPretty = ''
            actions = []
            for n in self.numsIterationsForDisplay:
                valuesPretty, qValuesPretty, actions, policyPretty = self.runAgent(moduleDict, n)
                handle.write(self.prettyValueSolutionString(f'values_k_{n}', valuesPretty))
                for action in actions:
                    handle.write(self.prettyValueSolutionString(f'q_values_k_{n}_action_{action}', qValuesPretty[action]))
            handle.write(self.prettyValueSolutionString('policy', policyPretty))
            handle.write(self.prettyValueSolutionString('actions', '\n'.join(actions) + '\n'))
        return True

    def runAgent(self, moduleDict: Dict[str, Any], numIterations: int) -> Tuple[str, Dict[str, str], List[str], str]:
        """Run value iteration agent for given number of iterations.
        
        Args:
            moduleDict: Dictionary containing student code modules
            numIterations: Number of iterations to run
            
        Returns:
            Tuple of (values string, Q-values dict, actions list, policy string)
        """
        agent = moduleDict['valueIterationAgents'].ValueIterationAgent(self.grid, discount=self.discount, iterations=numIterations)
        states = self.grid.getStates()
        actions = list(reduce(lambda a, b: set(a).union(b), [self.grid.getPossibleActions(state) for state in states]))
        values = {}
        qValues = {}
        policy = {}
        for state in states:
            values[state] = agent.getValue(state)
            policy[state] = agent.computeActionFromValues(state)
            possibleActions = self.grid.getPossibleActions(state)
            for action in actions:
                if action not in qValues:
                    qValues[action] = {}
                if action in possibleActions:
                    qValues[action][state] = agent.computeQValueFromValues(state, action)
                else:
                    qValues[action][state] = None
        valuesPretty = self.prettyValues(values)
        policyPretty = self.prettyPolicy(policy)
        qValuesPretty = {}
        for action in actions:
            qValuesPretty[action] = self.prettyValues(qValues[action])
        return (valuesPretty, qValuesPretty, actions, policyPretty)

    def prettyPrint(self, elements: Dict[Tuple[int, int], Any], formatString: str) -> str:
        """Format grid elements for display.
        
        Args:
            elements: Dictionary mapping (x,y) coordinates to values
            formatString: Format string for values
            
        Returns:
            Pretty-printed string representation
        """
        pretty = ''
        states = self.grid.getStates()
        for ybar in range(self.grid.grid.height):
            y = self.grid.grid.height-1-ybar
            row = []
            for x in range(self.grid.grid.width):
                if (x, y) in states:
                    value = elements[(x, y)]
                    if value is None:
                        row.append('   illegal')
                    else:
                        row.append(formatString.format(elements[(x,y)]))
                else:
                    row.append('_' * 10)
            pretty += f'        {("   ".join(row))}\n'
        pretty += '\n'
        return pretty

    def prettyValues(self, values: Dict[Tuple[int, int], float]) -> str:
        """Format state values for display.
        
        Args:
            values: Dictionary mapping states to values
            
        Returns:
            Pretty-printed string of values
        """
        return self.prettyPrint(values, '{0:10.4f}')

    def prettyPolicy(self, policy: Dict[Tuple[int, int], str]) -> str:
        """Format policy for display.
        
        Args:
            policy: Dictionary mapping states to actions
            
        Returns:
            Pretty-printed string of policy
        """
        return self.prettyPrint(policy, '{0:10s}')

    def prettyValueSolutionString(self, name: str, pretty: str) -> str:
        """Format value solution for output file.
        
        Args:
            name: Name of value set
            pretty: Pretty-printed string to format
            
        Returns:
            Formatted solution string
        """
        return f'{name}: """\n{pretty.rstrip()}\n"""\n\n'

    def comparePrettyValues(self, aPretty: str, bPretty: str, tolerance: float = 0.01) -> bool:
        """Compare two pretty-printed value strings.
        
        Args:
            aPretty: First pretty-printed string
            bPretty: Second pretty-printed string
            tolerance: Allowed numeric difference
            
        Returns:
            True if values match within tolerance
        """
        aList = self.parsePrettyValues(aPretty)
        bList = self.parsePrettyValues(bPretty)
        if len(aList) != len(bList):
            return False
        for a, b in zip(aList, bList):
            try:
                aNum = float(a)
                bNum = float(b)
                # error = abs((aNum - bNum) / ((aNum + bNum) / 2.0))
                error = abs(aNum - bNum)
                if error > tolerance:
                    return False
            except ValueError:
                if a.strip() != b.strip():
                    return False
        return True

    def parsePrettyValues(self, pretty: str) -> List[str]:
        """Parse pretty-printed value string into list.
        
        Args:
            pretty: Pretty-printed string to parse
            
        Returns:
            List of value strings
        """
        values = pretty.split()
        return values


class AsynchronousValueIterationTest(ValueIterationTest):
    def runAgent(self, moduleDict: Dict[str, Any], numIterations: int) -> Tuple[str, Dict[str, str], List[str], str]:
        """Run asynchronous value iteration agent and return formatted results.
        
        Args:
            moduleDict: Dictionary containing agent implementation modules
            numIterations: Number of value iteration iterations to run
            
        Returns:
            Tuple containing:
                - Pretty-printed state values string
                - Dictionary mapping actions to pretty-printed Q-values
                - List of possible actions
                - Pretty-printed policy string
        """
        agent = moduleDict['valueIterationAgents'].AsynchronousValueIterationAgent(self.grid, discount=self.discount, iterations=numIterations)
        states = self.grid.getStates()
        actions = list(reduce(lambda a, b: set(a).union(b), [self.grid.getPossibleActions(state) for state in states]))
        values = {}
        qValues = {}
        policy = {}
        for state in states:
            values[state] = agent.getValue(state)
            policy[state] = agent.computeActionFromValues(state)
            possibleActions = self.grid.getPossibleActions(state)
            for action in actions:
                if action not in qValues:
                    qValues[action] = {}
                if action in possibleActions:
                    qValues[action][state] = agent.computeQValueFromValues(state, action)
                else:
                    qValues[action][state] = None
        valuesPretty = self.prettyValues(values)
        policyPretty = self.prettyPolicy(policy)
        qValuesPretty = {}
        for action in actions:
            qValuesPretty[action] = self.prettyValues(qValues[action])
        return (valuesPretty, qValuesPretty, actions, policyPretty)

class PrioritizedSweepingValueIterationTest(ValueIterationTest):
    def runAgent(self, moduleDict: Dict[str, Any], numIterations: int) -> Tuple[str, Dict[str, str], List[str], str]:
        """Run prioritized sweeping value iteration agent and return formatted results.
        
        Args:
            moduleDict: Dictionary containing agent implementation modules
            numIterations: Number of value iteration iterations to run
            
        Returns:
            Tuple containing:
                - Pretty-printed state values string
                - Dictionary mapping actions to pretty-printed Q-values  
                - List of possible actions
                - Pretty-printed policy string
        """
        agent = moduleDict['valueIterationAgents'].PrioritizedSweepingValueIterationAgent(self.grid, discount=self.discount, iterations=numIterations)
        states = self.grid.getStates()
        actions = list(reduce(lambda a, b: set(a).union(b), [self.grid.getPossibleActions(state) for state in states]))
        values = {}
        qValues = {}
        policy = {}
        for state in states:
            values[state] = agent.getValue(state)
            policy[state] = agent.computeActionFromValues(state)
            possibleActions = self.grid.getPossibleActions(state)
            for action in actions:
                if action not in qValues:
                    qValues[action] = {}
                if action in possibleActions:
                    qValues[action][state] = agent.computeQValueFromValues(state, action)
                else:
                    qValues[action][state] = None
        valuesPretty = self.prettyValues(values)
        policyPretty = self.prettyPolicy(policy)
        qValuesPretty = {}
        for action in actions:
            qValuesPretty[action] = self.prettyValues(qValues[action])
        return (valuesPretty, qValuesPretty, actions, policyPretty)

class ApproximateQLearningTest(testClasses.TestCase):

    def __init__(self, question: Any, testDict: Dict[str, Any]) -> None:
        """Initialize approximate Q-learning test case.
        
        Args:
            question: Question object this test belongs to
            testDict: Dictionary containing test parameters
        """
        super(ApproximateQLearningTest, self).__init__(question, testDict)
        self.discount = float(testDict['discount'])
        self.grid = gridworld.Gridworld(parseGrid(testDict['grid']))
        if 'noise' in testDict: self.grid.setNoise(float(testDict['noise']))
        if 'livingReward' in testDict: self.grid.setLivingReward(float(testDict['livingReward']))
        self.grid = gridworld.Gridworld(parseGrid(testDict['grid']))
        self.env = gridworld.GridworldEnvironment(self.grid)
        self.epsilon = float(testDict['epsilon'])
        self.learningRate = float(testDict['learningRate'])
        self.extractor = 'IdentityExtractor'
        if 'extractor' in testDict:
            self.extractor = testDict['extractor']
        self.opts = {'actionFn': self.env.getPossibleActions, 'epsilon': self.epsilon, 'gamma': self.discount, 'alpha': self.learningRate}
        numExperiences = int(testDict['numExperiences'])
        maxPreExperiences = 10
        self.numsExperiencesForDisplay = list(range(min(numExperiences, maxPreExperiences)))
        self.testOutFile = testDict['test_out_file']
        if sys.platform == 'win32':
            _, question_name, test_name = testDict['test_out_file'].split('\\')
        else:
            _, question_name, test_name = testDict['test_out_file'].split('/')
        self.experiences = Experiences(test_name.split('.')[0])
        if maxPreExperiences < numExperiences:
            self.numsExperiencesForDisplay.append(numExperiences)

    def writeFailureFile(self, string: str) -> None:
        """Write failure output to file.
        
        Args:
            string: Failure output to write
        """
        with open(self.testOutFile, 'w') as handle:
            handle.write(string)

    def removeFailureFileIfExists(self) -> None:
        """Remove the failure output file if it exists."""
        if os.path.exists(self.testOutFile):
            os.remove(self.testOutFile)

    def execute(self, grades: Any, moduleDict: Dict[str, Any], solutionDict: Dict[str, Any]) -> bool:
        """Execute tests for all experience counts.
        
        Args:
            grades: Grading object to record results
            moduleDict: Dictionary containing agent implementation modules
            solutionDict: Dictionary containing correct solutions
            
        Returns:
            True if all tests pass, False otherwise
        """
        failureOutputFileString = ''
        failureOutputStdString = ''
        for n in self.numsExperiencesForDisplay:
            testPass, stdOutString, fileOutString = self.executeNExperiences(grades, moduleDict, solutionDict, n)
            failureOutputStdString += stdOutString
            failureOutputFileString += fileOutString
            if not testPass:
                self.addMessage(failureOutputStdString)
                self.addMessage(f'For more details to help you debug, see test output file {self.testOutFile}\n\n')
                self.writeFailureFile(failureOutputFileString)
                return self.testFail(grades)
        self.removeFailureFileIfExists()
        return self.testPass(grades)

    def executeNExperiences(self, grades: Any, moduleDict: Dict[str, Any], solutionDict: Dict[str, Any], n: int) -> Tuple[bool, str, str]:
        """Execute tests for a specific number of experiences.
        
        Args:
            grades: Grading object to record results
            moduleDict: Dictionary containing agent implementation modules
            solutionDict: Dictionary containing correct solutions
            n: Number of experiences to test
            
        Returns:
            Tuple containing:
                - Boolean indicating if test passed
                - Standard output string
                - File output string
        """
        testPass = True
        qValuesPretty, weights, actions, lastExperience = self.runAgent(moduleDict, n)
        stdOutString = ''
        fileOutString = f"==================== Iteration {n} ====================\n"
        if lastExperience is not None:
            fileOutString += f"Agent observed the transition (startState = {lastExperience[0]}, action = {lastExperience[1]}, endState = {lastExperience[2]}, reward = {lastExperience[3]})\n\n"
        weightsKey = f'weights_k_{n}'
        if weights == eval(solutionDict[weightsKey]):
            fileOutString += f"Weights at iteration {n} are correct."
            fileOutString += f"   Student/correct solution:\n\n{pp.pformat(weights)}\n\n"
        for action in actions:
            qValuesKey = f'q_values_k_{n}_action_{action}'
            qValues = qValuesPretty[action]
            if self.comparePrettyValues(qValues, solutionDict[qValuesKey]):
                fileOutString += f"Q-Values at iteration {n} for action '{action}' are correct."
                fileOutString += f"   Student/correct solution:\n\t{self.prettyValueSolutionString(qValuesKey, qValues)}"
            else:
                testPass = False
                outString = f"Q-Values at iteration {n} for action '{action}' are NOT correct."
                outString += f"   Student solution:\n\t{self.prettyValueSolutionString(qValuesKey, qValues)}"
                outString += f"   Correct solution:\n\t{self.prettyValueSolutionString(qValuesKey, solutionDict[qValuesKey])}"
                stdOutString += outString
                fileOutString += outString
        return testPass, stdOutString, fileOutString

    def writeSolution(self, moduleDict: Dict[str, Any], filePath: str) -> bool:
        """Write solution to file.
        
        Args:
            moduleDict: Dictionary containing agent implementation modules
            filePath: Path to write solution file
            
        Returns:
            True if solution was written successfully
        """
        with open(filePath, 'w') as handle:
            for n in self.numsExperiencesForDisplay:
                qValuesPretty, weights, actions, _ = self.runAgent(moduleDict, n)
                handle.write(self.prettyValueSolutionString(f'weights_k_{n}', pp.pformat(weights)))
                for action in actions:
                    handle.write(self.prettyValueSolutionString(f'q_values_k_{n}_action_{action}', qValuesPretty[action]))
        return True

    def runAgent(self, moduleDict: Dict[str, Any], numExperiences: int) -> Tuple[Dict[str, str], Any, List[str], Optional[Tuple]]:
        """Run approximate Q-learning agent and return results.
        
        Args:
            moduleDict: Dictionary containing agent implementation modules
            numExperiences: Number of experiences to run
            
        Returns:
            Tuple containing:
                - Dictionary mapping actions to pretty-printed Q-values
                - Agent weights
                - List of possible actions
                - Last experience tuple or None
        """
        agent = moduleDict['qlearningAgents'].ApproximateQAgent(extractor=self.extractor, **self.opts)
        states = [state for state in self.grid.getStates() if len(self.grid.getPossibleActions(state)) > 0]
        states.sort()
        lastExperience = None
        for i in range(numExperiences):
            lastExperience = self.experiences.get_experience()
            agent.update(*lastExperience)
        actions = list(reduce(lambda a, b: set(a).union(b), [self.grid.getPossibleActions(state) for state in states]))
        qValues = {}
        weights = agent.getWeights()
        for state in states:
            possibleActions = self.grid.getPossibleActions(state)
            for action in actions:
                if action not in qValues:
                    qValues[action] = {}
                if action in possibleActions:
                    qValues[action][state] = agent.getQValue(state, action)
                else:
                    qValues[action][state] = None
        qValuesPretty = {}
        for action in actions:
            qValuesPretty[action] = self.prettyValues(qValues[action])
        return (qValuesPretty, weights, actions, lastExperience)

    def prettyPrint(self, elements: Dict[Tuple[int, int], Any], formatString: str) -> str:
        """Pretty print grid elements.
        
        Args:
            elements: Dictionary mapping grid positions to values
            formatString: Format string for values
            
        Returns:
            Pretty-printed string representation
        """
        pretty = ''
        states = self.grid.getStates()
        for ybar in range(self.grid.grid.height):
            y = self.grid.grid.height-1-ybar
            row = []
            for x in range(self.grid.grid.width):
                if (x, y) in states:
                    value = elements[(x, y)]
                    if value is None:
                        row.append('   illegal')
                    else:
                        row.append(formatString.format(elements[(x,y)]))
                else:
                    row.append('_' * 10)
            pretty += f'        {("   ".join(row))}\n'
        pretty += '\n'
        return pretty

    def prettyValues(self, values: Dict[Tuple[int, int], float]) -> str:
        """Pretty print values with standard formatting.
        
        Args:
            values: Dictionary mapping positions to values
            
        Returns:
            Pretty-printed string representation
        """
        return self.prettyPrint(values, '{0:10.4f}')

    def prettyPolicy(self, policy: Dict[Tuple[int, int], str]) -> str:
        """Pretty print policy with standard formatting.
        
        Args:
            policy: Dictionary mapping positions to actions
            
        Returns:
            Pretty-printed string representation
        """
        return self.prettyPrint(policy, '{0:10s}')

    def prettyValueSolutionString(self, name: str, pretty: str) -> str:
        """Format pretty-printed values as solution string.
        
        Args:
            name: Name of value set
            pretty: Pretty-printed string to format
            
        Returns:
            Formatted solution string
        """
        return f'{name}: """\n{pretty.rstrip()}\n"""\n\n'

    def comparePrettyValues(self, aPretty: str, bPretty: str, tolerance: float = 0.01) -> bool:
        """Compare two sets of pretty-printed values.
        
        Args:
            aPretty: First set of pretty-printed values
            bPretty: Second set of pretty-printed values
            tolerance: Maximum allowed difference between values
            
        Returns:
            True if values match within tolerance
        """
        aList = self.parsePrettyValues(aPretty)
        bList = self.parsePrettyValues(bPretty)
        if len(aList) != len(bList):
            return False
        for a, b in zip(aList, bList):
            try:
                aNum = float(a)
                bNum = float(b)
                # error = abs((aNum - bNum) / ((aNum + bNum) / 2.0))
                error = abs(aNum - bNum)
                if error > tolerance:
                    return False
            except ValueError:
                if a.strip() != b.strip():
                    return False
        return True

    def parsePrettyValues(self, pretty: str) -> List[str]:
        """Parse pretty-printed values into list.
        
        Args:
            pretty: Pretty-printed string to parse
            
        Returns:
            List of value strings
        """
        values = pretty.split()
        return values


class QLearningTest(testClasses.TestCase):

    def __init__(self, question: Any, testDict: Dict[str, Any]) -> None:
        """Initialize Q-learning test case.
        
        Args:
            question: Question object this test belongs to
            testDict: Dictionary containing test parameters including:
                - discount: Discount factor gamma
                - grid: Grid layout specification
                - noise: Optional noise parameter
                - livingReward: Optional living reward
                - epsilon: Exploration rate
                - learningRate: Learning rate alpha
                - numExperiences: Number of training experiences
                - test_out_file: Output file path for test results
        """
        super(QLearningTest, self).__init__(question, testDict)
        self.discount = float(testDict['discount'])
        self.grid = gridworld.Gridworld(parseGrid(testDict['grid']))
        if 'noise' in testDict: self.grid.setNoise(float(testDict['noise']))
        if 'livingReward' in testDict: self.grid.setLivingReward(float(testDict['livingReward']))
        self.grid = gridworld.Gridworld(parseGrid(testDict['grid']))
        self.env = gridworld.GridworldEnvironment(self.grid)
        self.epsilon = float(testDict['epsilon'])
        self.learningRate = float(testDict['learningRate'])
        self.opts = {'actionFn': self.env.getPossibleActions, 'epsilon': self.epsilon, 'gamma': self.discount, 'alpha': self.learningRate}
        numExperiences = int(testDict['numExperiences'])
        maxPreExperiences = 10
        self.numsExperiencesForDisplay = list(range(min(numExperiences, maxPreExperiences)))
        self.testOutFile = testDict['test_out_file']
        if sys.platform == 'win32':
            _, question_name, test_name = testDict['test_out_file'].split('\\')
        else:
            _, question_name, test_name = testDict['test_out_file'].split('/')
        self.experiences = Experiences(test_name.split('.')[0])
        if maxPreExperiences < numExperiences:
            self.numsExperiencesForDisplay.append(numExperiences)

    def writeFailureFile(self, string: str) -> None:
        """Write failure output to file.
        
        Args:
            string: Failure output to write
        """
        with open(self.testOutFile, 'w') as handle:
            handle.write(string)

    def removeFailureFileIfExists(self) -> None:
        """Remove the failure output file if it exists."""
        if os.path.exists(self.testOutFile):
            os.remove(self.testOutFile)

    def execute(self, grades: Any, moduleDict: Dict[str, Any], solutionDict: Dict[str, Any]) -> bool:
        """Execute Q-learning tests and grade results.
        
        Args:
            grades: Grading object to record results
            moduleDict: Dictionary containing agent implementation modules
            solutionDict: Dictionary containing correct solutions
            
        Returns:
            True if tests pass, False otherwise
        """
        failureOutputFileString = ''
        failureOutputStdString = ''
        for n in self.numsExperiencesForDisplay:
            checkValuesAndPolicy = (n == self.numsExperiencesForDisplay[-1])
            testPass, stdOutString, fileOutString = self.executeNExperiences(grades, moduleDict, solutionDict, n, checkValuesAndPolicy)
            failureOutputStdString += stdOutString
            failureOutputFileString += fileOutString
            if not testPass:
                self.addMessage(failureOutputStdString)
                self.addMessage(f'For more details to help you debug, see test output file {self.testOutFile}\n\n')
                self.writeFailureFile(failureOutputFileString)
                return self.testFail(grades)
        self.removeFailureFileIfExists()
        return self.testPass(grades)

    def executeNExperiences(self, grades: Any, moduleDict: Dict[str, Any], solutionDict: Dict[str, Any], n: int, checkValuesAndPolicy: bool) -> Tuple[bool, str, str]:
        """Execute n experiences and check results.
        
        Args:
            grades: Grading object to record results
            moduleDict: Dictionary containing agent implementation modules
            solutionDict: Dictionary containing correct solutions
            n: Number of experiences to run
            checkValuesAndPolicy: Whether to check values and policy
            
        Returns:
            Tuple containing:
                - Whether tests passed
                - Standard output string
                - File output string
        """
        testPass = True
        valuesPretty, qValuesPretty, actions, policyPretty, lastExperience = self.runAgent(moduleDict, n)
        stdOutString = ''
        fileOutString = ''
        if lastExperience is not None:
            pass
        for action in actions:
            qValuesKey = f'q_values_k_{n}_action_{action}'
            qValues = qValuesPretty[action]

            if self.comparePrettyValues(qValues, solutionDict[qValuesKey]):
                pass
            else:
                testPass = False
                outString = f"Q-Values at iteration {n} for action '{action}' are NOT correct."
                outString += f"   Student solution:\n\t{self.prettyValueSolutionString(qValuesKey, qValues)}"
                outString += f"   Correct solution:\n\t{self.prettyValueSolutionString(qValuesKey, solutionDict[qValuesKey])}"
                stdOutString += outString
                fileOutString += outString
        if checkValuesAndPolicy:
            if not self.comparePrettyValues(valuesPretty, solutionDict['values']):
                testPass = False
                outString = "Values are NOT correct."
                outString += f"   Student solution:\n\t{self.prettyValueSolutionString('values', valuesPretty)}"
                outString += f"   Correct solution:\n\t{self.prettyValueSolutionString('values', solutionDict['values'])}"
                stdOutString += outString
                fileOutString += outString
            if not self.comparePrettyValues(policyPretty, solutionDict['policy']):
                testPass = False
                outString = "Policy is NOT correct."
                outString += f"   Student solution:\n\t{self.prettyValueSolutionString('policy', policyPretty)}"
                outString += f"   Correct solution:\n\t{self.prettyValueSolutionString('policy', solutionDict['policy'])}"
                stdOutString += outString
                fileOutString += outString
        return testPass, stdOutString, fileOutString

    def writeSolution(self, moduleDict: Dict[str, Any], filePath: str) -> bool:
        """Write solution to file.
        
        Args:
            moduleDict: Dictionary containing agent implementation modules
            filePath: Path to write solution file
            
        Returns:
            True if solution written successfully
        """
        with open(filePath, 'w') as handle:
            valuesPretty = ''
            policyPretty = ''
            for n in self.numsExperiencesForDisplay:
                valuesPretty, qValuesPretty, actions, policyPretty, _ = self.runAgent(moduleDict, n)
                for action in actions:
                    handle.write(self.prettyValueSolutionString(f'q_values_k_{n}_action_{action}', qValuesPretty[action]))
            handle.write(self.prettyValueSolutionString('values', valuesPretty))
            handle.write(self.prettyValueSolutionString('policy', policyPretty))
        return True

    def runAgent(self, moduleDict: Dict[str, Any], numExperiences: int) -> Tuple[str, Dict[str, str], List[str], str, Optional[Tuple]]:
        """Run Q-learning agent for specified number of experiences.
        
        Args:
            moduleDict: Dictionary containing agent implementation modules
            numExperiences: Number of experiences to run
            
        Returns:
            Tuple containing:
                - Pretty-printed values string
                - Dictionary mapping actions to pretty-printed Q-values
                - List of possible actions
                - Pretty-printed policy string
                - Last experience tuple or None
        """
        agent = moduleDict['qlearningAgents'].QLearningAgent(**self.opts)
        states = [state for state in self.grid.getStates() if len(self.grid.getPossibleActions(state)) > 0]
        states.sort()
        lastExperience = None
        for i in range(numExperiences):
            lastExperience = self.experiences.get_experience()
            agent.update(*lastExperience)
        actions = list(reduce(lambda a, b: set(a).union(b), [self.grid.getPossibleActions(state) for state in states]))
        values = {}
        qValues = {}
        policy = {}
        for state in states:
            values[state] = agent.computeValueFromQValues(state)
            policy[state] = agent.computeActionFromQValues(state)
            possibleActions = self.grid.getPossibleActions(state)
            for action in actions:
                if action not in qValues:
                    qValues[action] = {}
                if action in possibleActions:
                    qValues[action][state] = agent.getQValue(state, action)
                else:
                    qValues[action][state] = None
        valuesPretty = self.prettyValues(values)
        policyPretty = self.prettyPolicy(policy)
        qValuesPretty = {}
        for action in actions:
            qValuesPretty[action] = self.prettyValues(qValues[action])
        return (valuesPretty, qValuesPretty, actions, policyPretty, lastExperience)

    def prettyPrint(self, elements: Dict[Tuple[int, int], Any], formatString: str) -> str:
        """Pretty print grid elements.
        
        Args:
            elements: Dictionary mapping (x,y) coordinates to values
            formatString: Format string for printing values
            
        Returns:
            Pretty-printed string representation
        """
        pretty = ''
        states = self.grid.getStates()
        for ybar in range(self.grid.grid.height):
            y = self.grid.grid.height-1-ybar
            row = []
            for x in range(self.grid.grid.width):
                if (x, y) in states:
                    value = elements[(x, y)]
                    if value is None:
                        row.append('   illegal')
                    else:
                        row.append(formatString.format(elements[(x,y)]))
                else:
                    row.append('_' * 10)
            pretty += f'        {("   ".join(row))}\n'
        pretty += '\n'
        return pretty

    def prettyValues(self, values: Dict[Tuple[int, int], float]) -> str:
        """Pretty print values.
        
        Args:
            values: Dictionary mapping states to values
            
        Returns:
            Pretty-printed string representation
        """
        return self.prettyPrint(values, '{0:10.4f}')

    def prettyPolicy(self, policy: Dict[Tuple[int, int], str]) -> str:
        """Pretty print policy.
        
        Args:
            policy: Dictionary mapping states to actions
            
        Returns:
            Pretty-printed string representation
        """
        return self.prettyPrint(policy, '{0:10s}')

    def prettyValueSolutionString(self, name: str, pretty: str) -> str:
        """Format pretty-printed values as solution string.
        
        Args:
            name: Name of value set
            pretty: Pretty-printed string
            
        Returns:
            Formatted solution string
        """
        return f'{name}: """\n{pretty.rstrip()}\n"""\n\n'

    def comparePrettyValues(self, aPretty: str, bPretty: str, tolerance: float = 0.01) -> bool:
        """Compare two sets of pretty-printed values.
        
        Args:
            aPretty: First set of pretty-printed values
            bPretty: Second set of pretty-printed values
            tolerance: Maximum allowed difference between values
            
        Returns:
            True if values match within tolerance
        """
        aList = self.parsePrettyValues(aPretty)
        bList = self.parsePrettyValues(bPretty)
        if len(aList) != len(bList):
            return False
        for a, b in zip(aList, bList):
            try:
                aNum = float(a)
                bNum = float(b)
                # error = abs((aNum - bNum) / ((aNum + bNum) / 2.0))
                error = abs(aNum - bNum)
                if error > tolerance:
                    return False
            except ValueError:
                if a.strip() != b.strip():
                    return False
        return True

    def parsePrettyValues(self, pretty: str) -> List[str]:
        """Parse pretty-printed values into list.
        
        Args:
            pretty: Pretty-printed string to parse
            
        Returns:
            List of value strings
        """
        values = pretty.split()
        return values


class EpsilonGreedyTest(testClasses.TestCase):
    """Test case for evaluating epsilon-greedy action selection in Q-learning.
    
    Tests if the agent's epsilon-greedy action selection matches the expected 
    exploration/exploitation ratio given by epsilon.
    """

    def __init__(self, question: Any, testDict: Dict[str, Any]) -> None:
        """Initialize epsilon-greedy test case.
        
        Args:
            question: Question object this test belongs to
            testDict: Dictionary containing test parameters including:
                - discount: Discount factor gamma
                - grid: Grid layout specification
                - noise: Optional noise parameter
                - livingReward: Optional living reward
                - epsilon: Exploration rate
                - learningRate: Learning rate alpha
                - numExperiences: Number of training experiences
                - iterations: Number of test iterations
        """
        super(EpsilonGreedyTest, self).__init__(question, testDict)
        self.discount = float(testDict['discount'])
        self.grid = gridworld.Gridworld(parseGrid(testDict['grid']))
        if 'noise' in testDict: self.grid.setNoise(float(testDict['noise']))
        if 'livingReward' in testDict: self.grid.setLivingReward(float(testDict['livingReward']))

        self.grid = gridworld.Gridworld(parseGrid(testDict['grid']))
        self.env = gridworld.GridworldEnvironment(self.grid)
        self.epsilon = float(testDict['epsilon'])
        self.learningRate = float(testDict['learningRate'])
        self.numExperiences = int(testDict['numExperiences'])
        self.numIterations = int(testDict['iterations'])
        self.opts = {'actionFn': self.env.getPossibleActions, 'epsilon': self.epsilon, 'gamma': self.discount, 'alpha': self.learningRate}
        if sys.platform == 'win32':
            _, question_name, test_name = testDict['test_out_file'].split('\\')
        else:
            _, question_name, test_name = testDict['test_out_file'].split('/')
        self.experiences = Experiences(test_name.split('.')[0])

    def execute(self, grades: Any, moduleDict: Dict[str, Any], solutionDict: Dict[str, Any]) -> bool:
        """Execute the test case.
        
        Args:
            grades: Grading object to record results
            moduleDict: Dictionary containing student code modules
            solutionDict: Dictionary containing solution data
            
        Returns:
            True if test passes, False otherwise
        """
        if self.testEpsilonGreedy(moduleDict):
            return self.testPass(grades)
        else:
            return self.testFail(grades)

    def writeSolution(self, moduleDict: Dict[str, Any], filePath: str) -> bool:
        """Write solution file.
        
        Args:
            moduleDict: Dictionary containing student code modules
            filePath: Path to write solution file
            
        Returns:
            True if solution written successfully
        """
        with open(filePath, 'w') as handle:
            handle.write(f'# This is the solution file for {self.path}.\n')
            handle.write('# File intentionally blank.\n')
        return True

    def runAgent(self, moduleDict: Dict[str, Any]) -> Any:
        """Run Q-learning agent on test experiences.
        
        Args:
            moduleDict: Dictionary containing student code modules
            
        Returns:
            Trained Q-learning agent
        """
        agent = moduleDict['qlearningAgents'].QLearningAgent(**self.opts)
        states = [state for state in self.grid.getStates() if len(self.grid.getPossibleActions(state)) > 0]
        states.sort()
        for i in range(self.numExperiences):
            lastExperience = self.experiences.get_experience()
            agent.update(*lastExperience)
        return agent

    def testEpsilonGreedy(self, moduleDict: Dict[str, Any], tolerance: float = 0.025) -> bool:
        """Test if agent follows epsilon-greedy action selection.
        
        Args:
            moduleDict: Dictionary containing student code modules
            tolerance: Maximum allowed deviation from expected epsilon
            
        Returns:
            True if epsilon-greedy behavior matches expected, False otherwise
        """
        agent = self.runAgent(moduleDict)
        for state in self.grid.getStates():
            numLegalActions = len(agent.getLegalActions(state))
            if numLegalActions <= 1:
                continue
            numGreedyChoices = 0
            optimalAction = agent.computeActionFromQValues(state)
            for iteration in range(self.numIterations):
                # assume that their computeActionFromQValues implementation is correct (q4 tests this)
                if agent.getAction(state) == optimalAction:
                    numGreedyChoices += 1
            # e = epsilon, g = # greedy actions, n = numIterations, k = numLegalActions
            # g = n * [(1-e) + e/k] -> e = (n - g) / (n - n/k)
            empiricalEpsilonNumerator = self.numIterations - numGreedyChoices
            empiricalEpsilonDenominator = self.numIterations - self.numIterations / float(numLegalActions)
            empiricalEpsilon = empiricalEpsilonNumerator / empiricalEpsilonDenominator
            error = abs(empiricalEpsilon - self.epsilon)
            if error > tolerance:
                self.addMessage("Epsilon-greedy action selection is not correct.")
                self.addMessage(f"Actual epsilon = {self.epsilon}; student empirical epsilon = {empiricalEpsilon}; error = {error} > tolerance = {tolerance}")
                return False
        return True


### q8
class Question8Test(testClasses.TestCase):
    """Test case for question 8."""

    def __init__(self, question: Any, testDict: Dict[str, Any]) -> None:
        """Initialize question 8 test case.
        
        Args:
            question: Question object this test belongs to
            testDict: Dictionary containing test parameters
        """
        super(Question8Test, self).__init__(question, testDict)

    def execute(self, grades: Any, moduleDict: Dict[str, Any], solutionDict: Dict[str, Any]) -> bool:
        """Execute the test case.
        
        Args:
            grades: Grading object to record results
            moduleDict: Dictionary containing student code modules
            solutionDict: Dictionary containing solution data
            
        Returns:
            True if test passes, False otherwise
        """
        studentSolution = moduleDict['analysis'].question8()
        studentSolution = str(studentSolution).strip().lower()
        hashedSolution = sha1(studentSolution.encode('utf-8')).hexdigest()
        if hashedSolution == '46729c96bb1e4081fdc81a8ff74b3e5db8fba415':
            return self.testPass(grades)
        else:
            self.addMessage("Solution is not correct.")
            self.addMessage(f"   Student solution: {studentSolution}")
            return self.testFail(grades)

    def writeSolution(self, moduleDict: Dict[str, Any], filePath: str) -> bool:
        """Write solution file.
        
        Args:
            moduleDict: Dictionary containing student code modules
            filePath: Path to write solution file
            
        Returns:
            True if solution written successfully
        """
        handle = open(filePath, 'w')
        handle.write(f'# This is the solution file for {self.path}.\n')
        handle.write('# File intentionally blank.\n')
        handle.close()
        return True


### q7/q8
### =====
## Average wins of a pacman agent

class EvalAgentTest(testClasses.TestCase):
    """Test case for evaluating a Pacman agent's performance."""

    def __init__(self, question: Any, testDict: Dict[str, Any]) -> None:
        """Initialize evaluation test case.
        
        Args:
            question: Question object this test belongs to
            testDict: Dictionary containing test parameters including:
                - pacmanParams: Parameters for running Pacman
                - scoreMinimum: Minimum required score
                - nonTimeoutMinimum: Minimum games without timeout
                - winsMinimum: Minimum required wins
                - scoreThresholds: Score thresholds for points
                - nonTimeoutThresholds: Non-timeout thresholds for points
                - winsThresholds: Win thresholds for points
        """
        super(EvalAgentTest, self).__init__(question, testDict)
        self.pacmanParams = testDict['pacmanParams']

        self.scoreMinimum = int(testDict['scoreMinimum']) if 'scoreMinimum' in testDict else None
        self.nonTimeoutMinimum = int(testDict['nonTimeoutMinimum']) if 'nonTimeoutMinimum' in testDict else None
        self.winsMinimum = int(testDict['winsMinimum']) if 'winsMinimum' in testDict else None

        self.scoreThresholds = [int(s) for s in testDict.get('scoreThresholds','').split()]
        self.nonTimeoutThresholds = [int(s) for s in testDict.get('nonTimeoutThresholds','').split()]
        self.winsThresholds = [int(s) for s in testDict.get('winsThresholds','').split()]

        self.maxPoints = sum([len(t) for t in [self.scoreThresholds, self.nonTimeoutThresholds, self.winsThresholds]])


    def execute(self, grades: Any, moduleDict: Dict[str, Any], solutionDict: Dict[str, Any]) -> bool:
        """Execute the test case.
        
        Args:
            grades: Grading object to record results
            moduleDict: Dictionary containing student code modules
            solutionDict: Dictionary containing solution data
            
        Returns:
            True if test passes, False otherwise
        """
        self.addMessage(f'Grading agent using command:  python pacman.py {self.pacmanParams}')

        startTime = time.time()
        games = pacman.runGames(** pacman.readCommand(self.pacmanParams.split(' ')))
        totalTime = time.time() - startTime
        numGames = len(games)

        stats = {'time': totalTime, 'wins': [g.state.isWin() for g in games].count(True),
                 'games': games, 'scores': [g.state.getScore() for g in games],
                 'timeouts': [g.agentTimeout for g in games].count(True), 'crashes': [g.agentCrashed for g in games].count(True)}

        averageScore = sum(stats['scores']) / float(len(stats['scores']))
        nonTimeouts = numGames - stats['timeouts']
        wins = stats['wins']

        def gradeThreshold(value: float, minimum: Optional[float], thresholds: List[float], name: str) -> Tuple[bool, int, float, Optional[float], List[float], str]:
            points = 0
            passed = (minimum == None) or (value >= minimum)
            if passed:
                for t in thresholds:
                    if value >= t:
                        points += 1
            return (passed, points, value, minimum, thresholds, name)

        results = [gradeThreshold(averageScore, self.scoreMinimum, self.scoreThresholds, "average score"),
                   gradeThreshold(nonTimeouts, self.nonTimeoutMinimum, self.nonTimeoutThresholds, "games not timed out"),
                   gradeThreshold(wins, self.winsMinimum, self.winsThresholds, "wins")]

        totalPoints = 0
        for passed, points, value, minimum, thresholds, name in results:
            if minimum == None and len(thresholds)==0:
                continue

            # print passed, points, value, minimum, thresholds, name
            totalPoints += points
            if not passed:
                assert points == 0
                self.addMessage(f"{value} {name} (fail: below minimum value {minimum})")
            else:
                self.addMessage(f"{value} {name} ({points} of {len(thresholds)} points)")

            if minimum != None:
                self.addMessage("    Grading scheme:")
                self.addMessage(f"     < {minimum}:  fail")
                if len(thresholds)==0 or minimum != thresholds[0]:
                    self.addMessage(f"    >= {minimum}:  0 points")
                for idx, threshold in enumerate(thresholds):
                    self.addMessage(f"    >= {threshold}:  {idx+1} points")
            elif len(thresholds) > 0:
                self.addMessage("    Grading scheme:")
                self.addMessage(f"     < {thresholds[0]}:  0 points")
                for idx, threshold in enumerate(thresholds):
                    self.addMessage(f"    >= {threshold}:  {idx+1} points")

        if any([not passed for passed, _, _, _, _, _ in results]):
            totalPoints = 0

        return self.testPartial(grades, totalPoints, self.maxPoints)

    def writeSolution(self, moduleDict: Dict[str, Any], filePath: str) -> bool:
        """Write solution file.
        
        Args:
            moduleDict: Dictionary containing student code modules
            filePath: Path to write solution file
            
        Returns:
            True if solution written successfully
        """
        with open(filePath, 'w') as handle:
            handle.write(f'# This is the solution file for {self.path}.\n')
            handle.write('# File intentionally blank.\n')
        return True


### q2/q3
### =====
## For each parameter setting, compute the optimal policy, see if it satisfies some properties

def followPath(policy: dict, start: tuple, numSteps: int = 100) -> list:
    """Follow a policy from a start state for a given number of steps.
    
    Args:
        policy: Dictionary mapping states to actions
        start: Initial state tuple (x,y)
        numSteps: Maximum number of steps to follow policy
        
    Returns:
        List of states visited along the path
    """
    state = start
    path = []
    for i in range(numSteps):
        if state not in policy:
            break
        action = policy[state]
        path.append(f"({state[0]},{state[1]})")
        if action == 'north': nextState = state[0],state[1]+1
        if action == 'south': nextState = state[0],state[1]-1
        if action == 'east': nextState = state[0]+1,state[1]
        if action == 'west': nextState = state[0]-1,state[1]
        if action == 'exit' or action == None:
            path.append('TERMINAL_STATE')
            break
        state = nextState

    return path

def parseGrid(string: str) -> "Grid":
    """Parse a string representation of a grid into a Grid object.
    
    Args:
        string: Multi-line string defining the grid layout
        
    Returns:
        Grid object representing the parsed grid
    """
    grid = [[entry.strip() for entry in line.split()] for line in string.split('\n')]
    for row in grid:
        for x, col in enumerate(row):
            try:
                col = int(col)
            except:
                pass
            if col == "_":
                col = ' '
            row[x] = col
    return gridworld.makeGrid(grid)


def computePolicy(moduleDict: dict, grid: "Grid", discount: float) -> dict:
    """Compute optimal policy for a grid using value iteration.
    
    Args:
        moduleDict: Dictionary containing student code modules
        grid: Grid environment to compute policy for
        discount: Discount factor for value iteration
        
    Returns:
        Dictionary mapping states to optimal actions
    """
    valueIterator = moduleDict['valueIterationAgents'].ValueIterationAgent(grid, discount=discount)
    policy = {}
    for state in grid.getStates():
        policy[state] = valueIterator.computeActionFromValues(state)
    return policy



class GridPolicyTest(testClasses.TestCase):

    def __init__(self, question: "Question", testDict: dict) -> None:
        """Initialize a grid policy test case.
        
        Args:
            question: Question object this test belongs to
            testDict: Dictionary containing test parameters
        """
        super(GridPolicyTest, self).__init__(question, testDict)

        # Function in module in analysis that returns (discount, noise)
        self.parameterFn = testDict['parameterFn']
        self.question2 = testDict.get('question2', 'false').lower() == 'true'

        # GridWorld specification
        #    _ is empty space
        #    numbers are terminal states with that value
        #    # is a wall
        #    S is a start state
        #
        self.gridText = testDict['grid']
        self.grid = gridworld.Gridworld(parseGrid(testDict['grid']))
        self.gridName = testDict['gridName']

        # Policy specification
        #    _                  policy choice not checked
        #    N, E, S, W policy action must be north, east, south, west
        #
        self.policy = parseGrid(testDict['policy'])

        # State the most probable path must visit
        #    (x,y) for a particular location; (0,0) is bottom left
        #    terminal for the terminal state
        self.pathVisits = testDict.get('pathVisits', None)

        # State the most probable path must not visit
        #    (x,y) for a particular location; (0,0) is bottom left
        #    terminal for the terminal state
        self.pathNotVisits = testDict.get('pathNotVisits', None)


    def execute(self, grades: "Grades", moduleDict: dict, solutionDict: dict) -> bool:
        """Execute the test case.
        
        Args:
            grades: Grading object to record results
            moduleDict: Dictionary containing student code modules
            solutionDict: Dictionary containing solution data
            
        Returns:
            True if test passes, False otherwise
        """
        if not hasattr(moduleDict['analysis'], self.parameterFn):
            self.addMessage(f'Method not implemented: analysis.{self.parameterFn}')
            return self.testFail(grades)

        result = getattr(moduleDict['analysis'], self.parameterFn)()

        if type(result) == str and result.lower()[0:3] == "not":
            self.addMessage('Actually, it is possible!')
            return self.testFail(grades)

        if self.question2:
            livingReward = None
            try:
                discount, noise = result
                discount = float(discount)
                noise = float(noise)
            except:
                self.addMessage(f'Did not return a (discount, noise) pair; instead analysis.{self.parameterFn} returned: {result}')
                return self.testFail(grades)
            if discount != 0.9 and noise != 0.2:
                self.addMessage(f'Must change either the discount or the noise, not both. Returned (discount, noise) = {result}')
                return self.testFail(grades)
        else:
            try:
                discount, noise, livingReward = result
                discount = float(discount)
                noise = float(noise)
                livingReward = float(livingReward)
            except:
                self.addMessage(f'Did not return a (discount, noise, living reward) triple; instead analysis.{self.parameterFn} returned: {result}')
                return self.testFail(grades)

        self.grid.setNoise(noise)
        if livingReward != None:
            self.grid.setLivingReward(livingReward)

        start = self.grid.getStartState()
        policy = computePolicy(moduleDict, self.grid, discount)

        ## check policy
        actionMap = {'N': 'north', 'E': 'east', 'S': 'south', 'W': 'west', 'X': 'exit'}
        width, height = self.policy.width, self.policy.height
        policyPassed = True
        for x in range(width):
            for y in range(height):
                if self.policy[x][y] in actionMap and policy[(x,y)] != actionMap[self.policy[x][y]]:
                    differPoint = (x,y)
                    policyPassed = False

        if not policyPassed:
            self.addMessage('Policy not correct.')
            self.addMessage(f'    Student policy at {differPoint}: {policy[differPoint]}')
            self.addMessage(f'    Correct policy at {differPoint}: {actionMap[self.policy[differPoint[0]][differPoint[1]]]}')
            self.addMessage('    Student policy:')
            self.printPolicy(policy, False)
            self.addMessage("        Legend:  N,S,E,W at states which move north etc, X at states which exit,")
            self.addMessage("                 . at states where the policy is not defined (e.g. walls)")
            self.addMessage('    Correct policy specification:')
            self.printPolicy(self.policy, True)
            self.addMessage("        Legend:  N,S,E,W for states in which the student policy must move north etc,")
            self.addMessage("                 _ for states where it doesn't matter what the student policy does.")
            self.printGridworld()
            return self.testFail(grades)

        ## check path
        path = followPath(policy, self.grid.getStartState())

        if self.pathVisits != None and self.pathVisits not in path:
            self.addMessage(f'Policy does not visit state {self.pathVisits} when moving without noise.')
            self.addMessage(f'    States visited: {path}')
            self.addMessage('    Student policy:')
            self.printPolicy(policy, False)
            self.addMessage("        Legend:  N,S,E,W at states which move north etc, X at states which exit,")
            self.addMessage("                 . at states where policy not defined")
            self.printGridworld()
            return self.testFail(grades)

        if self.pathNotVisits != None and self.pathNotVisits in path:
            self.addMessage(f'Policy visits state {self.pathNotVisits} when moving without noise.')
            self.addMessage(f'    States visited: {path}')
            self.addMessage('    Student policy:')
            self.printPolicy(policy, False)
            self.addMessage("        Legend:  N,S,E,W at states which move north etc, X at states which exit,")
            self.addMessage("                 . at states where policy not defined")
            self.printGridworld()
            return self.testFail(grades)

        return self.testPass(grades)

    def printGridworld(self) -> None:
        """Print a text representation of the gridworld."""
        self.addMessage('    Gridworld:')
        for line in self.gridText.split('\n'):
            self.addMessage('     ' + line)
        self.addMessage('        Legend: # wall, _ empty, S start, numbers terminal states with that reward.')

    def printPolicy(self, policy: dict, policyTypeIsGrid: bool) -> None:
        """Print a text representation of a policy.
        
        Args:
            policy: Policy to print
            policyTypeIsGrid: Whether policy is grid-based (True) or dict-based (False)
        """
        if policyTypeIsGrid:
            legend = {'N': 'N', 'E': 'E', 'S': 'S', 'W': 'W', ' ': '_', 'X': 'X', '.': '.'}
        else:
            legend = {'north': 'N', 'east': 'E', 'south': 'S', 'west': 'W', 'exit': 'X', '.': '.', ' ': '_'}

        for ybar in range(self.grid.grid.height):
            y = self.grid.grid.height-1-ybar
            if policyTypeIsGrid:
                self.addMessage("        %s" % ("    ".join([legend[policy[x][y]] for x in range(self.grid.grid.width)]),))
            else:
                self.addMessage("        %s" % ("    ".join([legend[policy.get((x,y), '.')]  for x in range(self.grid.grid.width)]),))
        # for state in sorted(self.grid.getStates()):
        #     if state != 'TERMINAL_STATE':
        #         self.addMessage('      (%s,%s) %s' % (state[0], state[1], policy[state]))


    def writeSolution(self, moduleDict: dict, filePath: str) -> bool:
        """Write solution to file.
        
        Args:
            moduleDict: Dictionary containing student code modules
            filePath: Path to write solution file
            
        Returns:
            True if solution written successfully
        """
        with open(filePath, 'w') as handle:
            handle.write(f'# This is the solution file for {self.path}.\n')
            handle.write('# File intentionally blank.\n')
        return True

