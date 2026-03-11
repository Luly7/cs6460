"""Test classes for evaluating multi-agent search algorithms.

Modified by George Rudolph, 12 Nov 2024
Changes:
1. Added type hints
2. Improved docstrings
3. Improved code organization

This module provides test infrastructure for evaluating student implementations of
multi-agent search algorithms like minimax, alpha-beta pruning, and expectimax.

The module includes test classes that:
- Create game tree structures for testing search algorithms
- Run student agents on small test cases with known solutions 
- Evaluate agent performance in full Pacman games
- Check for common implementation bugs and failure modes
- Support automated grading by comparing against reference solutions

Classes:
    MultiagentTreeState: A wrapper around game states that implements a simple tree
        structure for testing purposes
    MultiagentTreeProblem: A test problem that uses a tree of states/actions
    GraphGameTreeTest: Tests student agents on small game trees with known solutions
    PacmanGameTreeTest: Tests student agents by running them in Pacman games
    EvalAgentTest: Tests student agents by evaluating their performance metrics
    GradingAgent: Agent that grades student implementations
    PolyAgent: Composite agent that runs multiple test variations

Functions:
    parseTreeProblem: Parses a game tree problem from a test dictionary
    run: Runs multiple games and returns statistics

Usage:
    This module is used by the autograder to test student implementations of
    multi-agent search algorithms. It is not meant to be used directly.

Licensing Information: You are free to use or extend these projects for
educational purposes provided that (1) you do not distribute or publish
solutions, (2) you retain this notice, and (3) you provide clear
attribution to UC Berkeley, including a link to http://ai.berkeley.edu.

Attribution Information: The Pacman AI projects were developed at UC Berkeley.
The core projects and autograders were primarily created by John DeNero
(denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
Student side autograding was added by Brad Miller, Nick Hay, and
Pieter Abbeel (pabbeel@cs.berkeley.edu).
"""
import json
import math
import os
import random
import sys
import time
import traceback
from collections import defaultdict
from pprint import PrettyPrinter
from typing import Dict, List, Optional, Tuple, Union, Any


import autograder
import layout
import pacman
import testClasses
from game import Agent
from ghostAgents import DirectionalGhost, RandomGhost
from pacman import GameState
from util import TimeoutFunction

pp = PrettyPrinter()

VERBOSE = False


class MultiagentTreeState:
    """A wrapper around game states for testing multiagent search algorithms.
    
    This class provides an interface similar to GameState but implements a simple
    tree structure for testing purposes. It tracks the underlying problem and state
    and delegates operations to the problem.
    
    Attributes:
        problem: The MultiagentTreeProblem this state belongs to
        state: The underlying state representation
    """

    def __init__(self, problem: 'MultiagentTreeProblem', state: str) -> None:
        """Initialize a new MultiagentTreeState.
        
        Args:
            problem: The MultiagentTreeProblem this state belongs to
            state: The underlying state representation
        """
        self.problem = problem
        self.state = state

    def generateSuccessor(self, agentIndex: int, action: str) -> 'MultiagentTreeState':
        """Generate the successor state after an agent takes an action.
        
        Args:
            agentIndex: Index of the agent taking the action
            action: The action being taken
            
        Returns:
            The successor MultiagentTreeState
        """
        if VERBOSE:
            print(f"generateSuccessor({self.state}, {agentIndex}, {action}) -> {self.problem.stateToSuccessorMap[self.state][action]}")
        successor = self.problem.stateToSuccessorMap[self.state][action]
        self.problem.generatedStates.add(successor)
        return MultiagentTreeState(self.problem, successor)

    def getScore(self) -> float:
        """Get the score/evaluation of this state.
        
        Returns:
            The numerical score for this state
            
        Raises:
            Exception: If called on a non-terminal state or before max depth
        """
        if VERBOSE:
            print(f"getScore({self.state}) -> {self.problem.evaluation[self.state]}")
        if self.state not in self.problem.evaluation:
            raise Exception('getScore() called on non-terminal state or before maximum depth achieved.')
        return float(self.problem.evaluation[self.state])

    def getLegalActions(self, agentIndex: int = 0) -> list[str]:
        """Get the legal actions available to an agent in this state.
        
        Args:
            agentIndex: Index of the agent to get actions for (default 0)
            
        Returns:
            List of legal action strings
        """
        if VERBOSE:
            print(f"getLegalActions({self.state}) -> {self.problem.stateToActions[self.state]}")
        return list(self.problem.stateToActions[self.state])

    def isWin(self) -> bool:
        """Check if this is a winning state.
        
        Returns:
            True if this is a winning state, False otherwise
        """
        if VERBOSE:
            print(f"isWin({self.state}) -> {self.state in self.problem.winStates}")
        return self.state in self.problem.winStates

    def isLose(self) -> bool:
        """Check if this is a losing state.
        
        Returns:
            True if this is a losing state, False otherwise
        """
        if VERBOSE:
            print(f"isLose({self.state}) -> {self.state in self.problem.loseStates}")
        return self.state in self.problem.loseStates

    def getNumAgents(self) -> int:
        """Get the number of agents in the game.
        
        Returns:
            The total number of agents
        """
        if VERBOSE:
            print(f"getNumAgents({self.state}) -> {self.problem.numAgents}")
        return self.problem.numAgents

class MultiagentTreeProblem:
    """A tree-structured multiagent game problem for testing.
    
    This class represents a game tree where states transition to other states through
    actions taken by multiple agents. Used for testing multiagent search algorithms.
    
    Attributes:
        startState (MultiagentTreeState): The initial game state
        numAgents (int): Number of agents in the game
        winStates (set[str]): Set of winning state strings
        loseStates (set[str]): Set of losing state strings 
        evaluation (dict[str, float]): Maps states to their evaluation scores
        successors (list[tuple[str, str, str]]): List of (state, action, nextState) transitions
        generatedStates (set[str]): Set tracking visited states
        stateToSuccessorMap (dict[str, dict[str, str]]): Maps states to {action: nextState} dicts
        stateToActions (dict[str, list[str]]): Maps states to lists of legal actions
    """
    def __init__(self, numAgents: int, startState: str, winStates: set[str], 
                 loseStates: set[str], successors: list[tuple[str, str, str]], 
                 evaluation: dict[str, float]) -> None:
        self.startState = MultiagentTreeState(self, startState)
        self.numAgents = numAgents
        self.winStates = winStates
        self.loseStates = loseStates
        self.evaluation = evaluation
        self.successors = successors

        self.reset()

        self.stateToSuccessorMap = defaultdict(dict)
        self.stateToActions = defaultdict(list)
        for state, action, nextState in successors:
            self.stateToActions[state].append(action)
            self.stateToSuccessorMap[state][action] = nextState

    def reset(self) -> None:
        """Reset the set of generated states to just the start state."""
        self.generatedStates = set([self.startState.state])


def parseTreeProblem(testDict: dict[str, str]) -> MultiagentTreeProblem:
    """Parse a multiagent game tree problem from a test dictionary.
    
    Args:
        testDict: Dictionary containing the problem specification with keys:
            num_agents: Number of agents
            start_state: Initial state string
            win_states: Space-separated winning states
            lose_states: Space-separated losing states
            evaluation: Newline-separated "state value" pairs
            successors: Newline-separated "state action nextState" triples
            
    Returns:
        MultiagentTreeProblem instance representing the game
        
    Raises:
        Exception: If evaluation or successor lines are malformed
    """
    numAgents = int(testDict["num_agents"])
    startState = testDict["start_state"]
    winStates = set(testDict["win_states"].split(" "))
    loseStates = set(testDict["lose_states"].split(" "))
    successors = []

    evaluation = {}
    for line in testDict["evaluation"].split('\n'):
        tokens = line.split()
        if len(tokens) == 2:
            state, value = tokens
            evaluation[state] = float(value)
        else:
            raise Exception(f"[parseTree] Bad evaluation line: |{line}|")

    for line in testDict["successors"].split('\n'):
        tokens = line.split()
        if len(tokens) == 3:
            state, action, nextState = tokens
            successors.append((state, action, nextState))
        else:
            raise Exception(f"[parseTree] Bad successor line: |{line}|")

    return MultiagentTreeProblem(numAgents, startState, winStates, loseStates, successors, evaluation)


def run(lay: Any, layName: str, pac: Any, ghosts: list, disp: Any, nGames: int = 1, name: str = 'games') -> dict:
    """Run multiple games and return statistics.
    
    Args:
        lay: Game layout
        layName: Name of the layout
        pac: Pacman agent
        ghosts: List of ghost agents
        disp: Display interface
        nGames: Number of games to run
        name: Name for this set of games
        
    Returns:
        Dictionary containing game statistics:
            time: Total time elapsed
            wins: Number of games won
            games: List of completed games
            scores: List of game scores
            timeouts: Number of timeouts
            crashes: Number of crashes
    """
    starttime = time.time()
    print(f'*** Running {name} on {layName} {nGames} time(s).')
    games = pacman.runGames(lay, pac, ghosts, disp,
                            nGames, False, catchExceptions=True, timeout=120)
    print(f'*** Finished running {name} on {layName} after {time.time() - starttime} seconds.')
    stats = {'time': time.time() - starttime, 
             'wins': [g.state.isWin() for g in games].count(True), 
             'games': games, 
             'scores': [g.state.getScore() for g in games],
             'timeouts': [g.agentTimeout for g in games].count(True), 
             'crashes': [g.agentCrashed for g in games].count(True)}
    print(f'*** Won {stats["wins"]} out of {len(games)} games. Average score: {sum(stats["scores"]) * 1.0 / len(games)} ***')
    return stats


class GradingAgent(Agent):
    def __init__(self, seed: int, studentAgent: Agent, optimalActions: list, altDepthActions: list, partialPlyBugActions: list) -> None:
        """Initialize a grading agent to evaluate a student's agent.
        
        Args:
            seed: Random seed for reproducibility
            studentAgent: The student's agent implementation to evaluate
            optimalActions: List of optimal actions for each game state
            altDepthActions: List of actions from alternative search depths
            partialPlyBugActions: List of actions with partial ply bug
        """
        # save student agent and actions of reference agents
        self.studentAgent = studentAgent
        self.optimalActions = optimalActions
        self.altDepthActions = altDepthActions
        self.partialPlyBugActions = partialPlyBugActions
        # create fields for storing specific wrong actions
        self.suboptimalMoves: list = []
        self.wrongStatesExplored: int = -1
        # boolean vectors represent types of implementation the student could have
        self.actionsConsistentWithOptimal: list = [
            True for i in range(len(optimalActions[0]))]
        self.actionsConsistentWithAlternativeDepth: list = [
            True for i in range(len(altDepthActions[0]))]
        self.actionsConsistentWithPartialPlyBug: list = [
            True for i in range(len(partialPlyBugActions[0]))]
        # keep track of elapsed moves
        self.stepCount: int = 0
        self.seed = seed

    def registerInitialState(self, state: GameState) -> None:
        """Register initial game state and seed RNG.
        
        Args:
            state: Initial game state
        """
        if 'registerInitialState' in dir(self.studentAgent):
            self.studentAgent.registerInitialState(state)
        random.seed(self.seed)

    def getAction(self, state: GameState) -> str:
        """Get an action from the student agent and evaluate it.
        
        Args:
            state: Current game state
            
        Returns:
            The optimal action for this state
        """
        GameState.getAndResetExplored()
        studentAction = (self.studentAgent.getAction(state),
                         len(GameState.getAndResetExplored()))
        optimalActions = self.optimalActions[self.stepCount]
        altDepthActions = self.altDepthActions[self.stepCount]
        partialPlyBugActions = self.partialPlyBugActions[self.stepCount]
        studentOptimalAction = False
        curRightStatesExplored = False
        for i in range(len(optimalActions)):
            if studentAction[0] in optimalActions[i][0]:
                studentOptimalAction = True
            else:
                self.actionsConsistentWithOptimal[i] = False
            if studentAction[1] == int(optimalActions[i][1]):
                curRightStatesExplored = True
        if not curRightStatesExplored and self.wrongStatesExplored < 0:
            self.wrongStatesExplored = 1
        for i in range(len(altDepthActions)):
            if studentAction[0] not in altDepthActions[i]:
                self.actionsConsistentWithAlternativeDepth[i] = False
        for i in range(len(partialPlyBugActions)):
            if studentAction[0] not in partialPlyBugActions[i]:
                self.actionsConsistentWithPartialPlyBug[i] = False
        if not studentOptimalAction:
            self.suboptimalMoves.append(
                (state, studentAction[0], optimalActions[0][0][0]))
        self.stepCount += 1
        random.seed(self.seed + self.stepCount)
        return optimalActions[0][0][0]

    def getSuboptimalMoves(self) -> list:
        """Get list of suboptimal moves made by student agent.
        
        Returns:
            List of (state, student_action, optimal_action) tuples
        """
        return self.suboptimalMoves

    def getWrongStatesExplored(self) -> int:
        """Get number of incorrectly explored states.
        
        Returns:
            Number of wrong states explored, or -1 if correct
        """
        return self.wrongStatesExplored

    def checkFailure(self) -> int:
        """Check what type of failure occurred, if any.
        
        Returns:
            +n: n suboptimal moves made
            -1: only off by one depth moves
            -2: partial ply bug detected
            -3: wrong states explored
            0: correct implementation
        """
        if self.wrongStatesExplored > 0:
            return -3
        if self.actionsConsistentWithOptimal.count(True) > 0:
            return 0
        elif self.actionsConsistentWithPartialPlyBug.count(True) > 0:
            return -2
        elif self.actionsConsistentWithAlternativeDepth.count(True) > 0:
            return -1
        else:
            return len(self.suboptimalMoves)
class PolyAgent(Agent):
    """A composite agent that runs multiple variations of search agents for testing.
    
    This agent runs several versions of multiagent search agents with different parameters
    to help identify potential bugs in student implementations.
    
    Attributes:
        solutionAgents (list): Reference search agents with correct implementation
        alternativeDepthAgents (list): Agents searching at different depths
        partialPlyBugAgents (list): Agents with partial ply bug implementation
        optimalActionLists (list): Recorded actions from solution agents
        alternativeDepthLists (list): Recorded actions from alternative depth agents  
        partialPlyBugLists (list): Recorded actions from partial ply bug agents
        seed (int): Random seed for reproducibility
        stepCount (int): Number of steps taken
    """
    def __init__(self, seed: int, multiAgents: Any, ourPacOptions: dict, depth: int) -> None:
        # prepare our pacman agents
        solutionAgents, alternativeDepthAgents, partialPlyBugAgents = self.construct_our_pacs(
            multiAgents, ourPacOptions)
        for p in solutionAgents:
            p.depth = depth
        for p in partialPlyBugAgents:
            p.depth = depth
        for p in alternativeDepthAgents[:2]:
            p.depth = max(1, depth - 1)
        for p in alternativeDepthAgents[2:]:
            p.depth = depth + 1
        self.solutionAgents = solutionAgents
        self.alternativeDepthAgents = alternativeDepthAgents
        self.partialPlyBugAgents = partialPlyBugAgents
        # prepare fields for storing the results
        self.optimalActionLists = []
        self.alternativeDepthLists = []
        self.partialPlyBugLists = []
        self.seed = seed
        self.stepCount = 0

    def select(self, list: list, indices: list[int]) -> list:
        """Return a sublist of elements given by indices in list.
        
        Args:
            list: Input list to select from
            indices: List of indices to select
            
        Returns:
            List containing elements at the specified indices
        """
        return [list[i] for i in indices]

    def construct_our_pacs(self, multiAgents: Any, keyword_dict: dict) -> tuple[list, list, list]:
        """Construct the different types of agents for testing.
        
        Args:
            multiAgents: Module containing agent implementations
            keyword_dict: Dictionary of keyword arguments for agent construction
            
        Returns:
            Tuple of (solution_agents, alternative_depth_agents, partial_ply_bug_agents)
        """
        pacs_without_stop = [multiAgents.StaffMultiAgentSearchAgent(
            **keyword_dict) for i in range(3)]
        keyword_dict['keepStop'] = 'True'
        pacs_with_stop = [multiAgents.StaffMultiAgentSearchAgent(
            **keyword_dict) for i in range(3)]
        keyword_dict['usePartialPlyBug'] = 'True'
        partial_ply_bug_pacs = [
            multiAgents.StaffMultiAgentSearchAgent(**keyword_dict)]
        keyword_dict['keepStop'] = 'False'
        partial_ply_bug_pacs = partial_ply_bug_pacs + \
            [multiAgents.StaffMultiAgentSearchAgent(**keyword_dict)]
        for pac in pacs_with_stop + pacs_without_stop + partial_ply_bug_pacs:
            pac.verbose = False
        ourpac = [pacs_with_stop[0], pacs_without_stop[0]]
        alternative_depth_pacs = self.select(
            pacs_with_stop + pacs_without_stop, [1, 4, 2, 5])
        return (ourpac, alternative_depth_pacs, partial_ply_bug_pacs)

    def registerInitialState(self, state: GameState) -> None:
        """Register the initial game state with all agents.
        
        Args:
            state: Initial game state
        """
        for agent in self.solutionAgents + self.alternativeDepthAgents:
            if 'registerInitialState' in dir(agent):
                agent.registerInitialState(state)
        random.seed(self.seed)

    def getAction(self, state: GameState) -> str:
        """Get the next action by surveying all test agents.
        
        Args:
            state: Current game state
            
        Returns:
            Action string selected by the primary solution agent
        """
        # survey agents
        GameState.getAndResetExplored()
        optimalActionLists = []
        for agent in self.solutionAgents:
            optimalActionLists.append((agent.getBestPacmanActions(
                state)[0], len(GameState.getAndResetExplored())))
        alternativeDepthLists = [agent.getBestPacmanActions(
            state)[0] for agent in self.alternativeDepthAgents]
        partialPlyBugLists = [agent.getBestPacmanActions(
            state)[0] for agent in self.partialPlyBugAgents]
        # record responses
        self.optimalActionLists.append(optimalActionLists)
        self.alternativeDepthLists.append(alternativeDepthLists)
        self.partialPlyBugLists.append(partialPlyBugLists)
        self.stepCount += 1
        random.seed(self.seed + self.stepCount)
        return optimalActionLists[0][0][0]

    def getTraces(self) -> tuple[list, list, list]:
        """Get the recorded action traces from all agents.
        
        Returns:
            Tuple of (optimal_actions, alternative_depth_actions, partial_ply_bug_actions)
        """
        return (self.optimalActionLists, self.alternativeDepthLists, self.partialPlyBugLists)

class PacmanGameTreeTest(testClasses.TestCase):

    def __init__(self, question: Any, testDict: dict) -> None:
        """Initialize a Pacman game tree test case.
        
        Args:
            question: The test question object
            testDict: Dictionary containing test parameters including:
                seed: Random seed for reproducibility
                alg: Name of algorithm to test
                layout: Layout text representation
                layoutName: Name of the layout
                depth: Search depth
                max_points: Maximum points for this test
        """
        super(PacmanGameTreeTest, self).__init__(question, testDict)
        self.seed = int(self.testDict['seed'])
        self.alg = self.testDict['alg']
        self.layout_text = self.testDict['layout']
        self.layout_name = self.testDict['layoutName']
        self.depth = int(self.testDict['depth'])
        self.max_points = int(self.testDict['max_points'])

    def execute(self, grades: Any, moduleDict: dict, solutionDict: dict) -> str:
        """Execute the test case and return grade.
        
        Args:
            grades: The grading object
            moduleDict: Dictionary containing student code modules
            solutionDict: Dictionary containing solution data
            
        Returns:
            Test result string ('pass' or 'fail')
        """
        # load student code and staff code solutions
        multiAgents = moduleDict['multiAgents']
        studentAgent = getattr(multiAgents, self.alg)(depth=self.depth)
        allActions = [json.loads(x)
                      for x in solutionDict['optimalActions'].split('\n')]
        altDepthActions = [json.loads(
            x) for x in solutionDict['altDepthActions'].split('\n')]
        partialPlyBugActions = [json.loads(
            x) for x in solutionDict['partialPlyBugActions'].split('\n')]
        # set up game state and play a game
        random.seed(self.seed)
        lay = layout.Layout([l.strip() for l in self.layout_text.split('\n')])
        pac = GradingAgent(self.seed, studentAgent, allActions,
                           altDepthActions, partialPlyBugActions)
        # check return codes and assign grades
        disp = self.question.getDisplay()
        stats = run(lay, self.layout_name, pac, [DirectionalGhost(
            i + 1) for i in range(2)], disp, name=self.alg)
        if stats['timeouts'] > 0:
            self.addMessage('Agent timed out on smallClassic.  No credit')
            return self.testFail(grades)
        if stats['crashes'] > 0:
            self.addMessage('Agent crashed on smallClassic.  No credit')
            return self.testFail(grades)
        code = pac.checkFailure()
        if code == 0:
            return self.testPass(grades)
        elif code == -3:
            if pac.getWrongStatesExplored() >= 0:
                self.addMessage('Bug: Wrong number of states expanded.')
                return self.testFail(grades)
            else:
                return self.testPass(grades)
        elif code == -2:
            self.addMessage('Bug: Partial Ply Bug')
            return self.testFail(grades)
        elif code == -1:
            self.addMessage('Bug: Search depth off by 1')
            return self.testFail(grades)
        elif code > 0:
            moves = pac.getSuboptimalMoves()
            state, studentMove, optMove = random.choice(moves)
            self.addMessage('Bug: Suboptimal moves')
            self.addMessage(f'State:{state}\nStudent Move:{studentMove}\nOptimal Move:{optMove}')
            return self.testFail(grades)

    def writeList(self, handle: Any, name: str, lst: list) -> None:
        """Write a list to a file handle in JSON format.
        
        Args:
            handle: File handle to write to
            name: Name of the list
            lst: List to write
        """
        handle.write(f'{name}: """\n')
        for l in lst:
            handle.write(f'{json.dumps(l)}\n')
        handle.write('"""\n')

    def writeSolution(self, moduleDict: dict, filePath: str) -> None:
        """Write solution data to a file.
        
        Args:
            moduleDict: Dictionary containing student code modules
            filePath: Path to write solution file to
        """
        # load module, set seed, create ghosts and macman, run game
        multiAgents = moduleDict['multiAgents']
        random.seed(self.seed)
        lay = layout.Layout([l.strip() for l in self.layout_text.split('\n')])
        if self.alg == 'ExpectimaxAgent':
            ourPacOptions = {'expectimax': 'True'}
        elif self.alg == 'AlphaBetaAgent':
            ourPacOptions = {'alphabeta': 'True'}
        else:
            ourPacOptions = {}
        pac = PolyAgent(self.seed, multiAgents, ourPacOptions, self.depth)
        disp = self.question.getDisplay()
        run(lay, self.layout_name, pac, [DirectionalGhost(
            i + 1) for i in range(2)], disp, name=self.alg)
        (optimalActions, altDepthActions, partialPlyBugActions) = pac.getTraces()
        # recover traces and record to file
        handle = open(filePath, 'w')
        self.writeList(handle, 'optimalActions', optimalActions)
        self.writeList(handle, 'altDepthActions', altDepthActions)
        self.writeList(handle, 'partialPlyBugActions', partialPlyBugActions)
        handle.close()

class GraphGameTreeTest(testClasses.TestCase):

    def __init__(self, question: Any, testDict: dict) -> None:
        """Initialize a graph game tree test case.
        
        Args:
            question: The test question object
            testDict: Dictionary containing test parameters:
                alg: Name of algorithm to test
                diagram: ASCII diagram of game tree
                depth: Search depth to use
        """
        super(GraphGameTreeTest, self).__init__(question, testDict)
        self.problem = parseTreeProblem(testDict)
        self.alg = self.testDict['alg']
        self.diagram = self.testDict['diagram'].split('\n')
        self.depth = int(self.testDict['depth'])

    def solveProblem(self, multiAgents: Any) -> tuple[str, str]:
        """Solve the test problem using the student's agent.
        
        Args:
            multiAgents: Module containing student's agent implementations
            
        Returns:
            Tuple of (selected action, space-separated string of generated states)
        """
        self.problem.reset()
        studentAgent = getattr(multiAgents, self.alg)(depth=self.depth)
        action = studentAgent.getAction(self.problem.startState)
        generated = self.problem.generatedStates
        return action, " ".join([str(s) for s in sorted(generated)])

    def addDiagram(self) -> None:
        """Add the game tree diagram to test output."""
        self.addMessage('Tree:')
        for line in self.diagram:
            self.addMessage(line)

    def execute(self, grades: Any, moduleDict: dict, solutionDict: dict) -> str:
        """Execute the test case.
        
        Args:
            grades: Grading object
            moduleDict: Dictionary containing student's code modules
            solutionDict: Dictionary containing correct solutions
            
        Returns:
            Result of test pass/fail
        """
        multiAgents = moduleDict['multiAgents']
        goldAction = solutionDict['action']
        goldGenerated = solutionDict['generated']
        action, generated = self.solveProblem(multiAgents)

        fail = False
        if action != goldAction:
            self.addMessage(f'Incorrect move for depth={self.depth}')
            self.addMessage(
                f'    Student move: {action}\n    Optimal move: {goldAction}')
            fail = True

        if generated != goldGenerated:
            self.addMessage(
                f'Incorrect generated nodes for depth={self.depth}')
            self.addMessage(f'    Student generated nodes: {generated}\n    Correct generated nodes: {goldGenerated}')
            fail = True

        if fail:
            self.addDiagram()
            return self.testFail(grades)
        else:
            return self.testPass(grades)

    def writeSolution(self, moduleDict: dict, filePath: str) -> bool:
        """Write solution for test case to file.
        
        Args:
            moduleDict: Dictionary containing student's code modules
            filePath: Path to write solution file
            
        Returns:
            True if solution was written successfully
        """
        multiAgents = moduleDict['multiAgents']
        action, generated = self.solveProblem(multiAgents)
        with open(filePath, 'w') as handle:
            handle.write(f'# This is the solution file for {self.path}.\n')
            handle.write(f'action: "{action}"\n')
            handle.write(f'generated: "{generated}"\n')
        return True


class EvalAgentTest(testClasses.TestCase):

    def __init__(self, question: Any, testDict: dict) -> None:
        """Initialize evaluation test for a Pacman agent.
        
        Args:
            question: The test question object
            testDict: Dictionary containing test parameters including:
                layoutName: Name of layout to test on
                agentName: Name of agent class to test
                ghosts: Ghost agent specifications
                maxTime: Maximum time allowed per game
                randomSeed: Random seed for reproducibility
                numGames: Number of games to run
                scoreMinimum: Minimum required average score (optional)
                nonTimeoutMinimum: Minimum required non-timeout games (optional)
                winsMinimum: Minimum required wins (optional)
                scoreThresholds: Score thresholds for partial credit
                nonTimeoutThresholds: Non-timeout thresholds for partial credit
                winsThresholds: Win thresholds for partial credit
                agentArgs: Arguments to pass to agent constructor (optional)
        """
        super(EvalAgentTest, self).__init__(question, testDict)
        self.layoutName = testDict['layoutName']
        self.agentName = testDict['agentName']
        self.ghosts = eval(testDict['ghosts'])
        self.maxTime = int(testDict['maxTime'])
        self.seed = int(testDict['randomSeed'])
        self.numGames = int(testDict['numGames'])

        self.scoreMinimum = int(
            testDict['scoreMinimum']) if 'scoreMinimum' in testDict else None
        self.nonTimeoutMinimum = int(
            testDict['nonTimeoutMinimum']) if 'nonTimeoutMinimum' in testDict else None
        self.winsMinimum = int(
            testDict['winsMinimum']) if 'winsMinimum' in testDict else None

        self.scoreThresholds = [int(s) for s in testDict.get(
            'scoreThresholds', '').split()]
        self.nonTimeoutThresholds = [int(s) for s in testDict.get(
            'nonTimeoutThresholds', '').split()]
        self.winsThresholds = [int(s) for s in testDict.get(
            'winsThresholds', '').split()]

        self.maxPoints = sum([len(t) for t in [
                             self.scoreThresholds, self.nonTimeoutThresholds, self.winsThresholds]])
        self.agentArgs = testDict.get('agentArgs', '')

    def execute(self, grades: Any, moduleDict: dict, solutionDict: dict) -> str:
        """Execute the test case and return grade.
        
        Args:
            grades: The grading object
            moduleDict: Dictionary containing student code modules
            solutionDict: Dictionary containing solution data
            
        Returns:
            Test result string with partial credit score
        """
        startTime = time.time()

        agentType = getattr(moduleDict['multiAgents'], self.agentName)
        agentOpts = pacman.parseAgentArgs(
            self.agentArgs) if self.agentArgs != '' else {}
        agent = agentType(**agentOpts)

        lay = layout.getLayout(self.layoutName, 3)

        disp = self.question.getDisplay()

        random.seed(self.seed)
        games = pacman.runGames(lay, agent, self.ghosts, disp, self.numGames,
                                False, catchExceptions=True, timeout=self.maxTime)
        totalTime = time.time() - startTime

        stats = {'time': totalTime, 'wins': [g.state.isWin() for g in games].count(True),
                 'games': games, 'scores': [g.state.getScore() for g in games],
                 'timeouts': [g.agentTimeout for g in games].count(True), 'crashes': [g.agentCrashed for g in games].count(True)}

        averageScore = sum(stats['scores']) / float(len(stats['scores']))
        nonTimeouts = self.numGames - stats['timeouts']
        wins = stats['wins']

        def gradeThreshold(value: float, minimum: Optional[float], thresholds: list[float], name: str) -> tuple[bool, int, float, Optional[float], list[float], str]:
            """Grade a value against thresholds for partial credit.
            
            Args:
                value: Value to grade
                minimum: Minimum required value (or None)
                thresholds: List of thresholds for partial credit
                name: Name of metric being graded
                
            Returns:
                Tuple of (passed, points, value, minimum, thresholds, name)
            """
            points = 0
            passed = (minimum == None) or (value >= minimum)
            if passed:
                for t in thresholds:
                    if value >= t:
                        points += 1
            return (passed, points, value, minimum, thresholds, name)

        results = [gradeThreshold(averageScore, self.scoreMinimum, self.scoreThresholds, "average score"),
                   gradeThreshold(nonTimeouts, self.nonTimeoutMinimum,
                                  self.nonTimeoutThresholds, "games not timed out"),
                   gradeThreshold(wins, self.winsMinimum, self.winsThresholds, "wins")]

        totalPoints = 0
        for passed, points, value, minimum, thresholds, name in results:
            if minimum == None and len(thresholds) == 0:
                continue

            totalPoints += points
            if not passed:
                assert points == 0
                self.addMessage(
                    f"{value} {name} (fail: below minimum value {minimum})")
            else:
                self.addMessage(f"{value} {name} ({points} of {len(thresholds)} points)")

            if minimum != None:
                self.addMessage("    Grading scheme:")
                self.addMessage(f"     < {minimum}:  fail")
                if len(thresholds) == 0 or minimum != thresholds[0]:
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

    def writeSolution(self, moduleDict: dict, filePath: str) -> bool:
        """Write solution for test case to file.
        
        Args:
            moduleDict: Dictionary containing student code modules
            filePath: Path to write solution file
            
        Returns:
            True if solution was written successfully
        """
        with open(filePath, 'w') as handle:
            handle.write(f'# This is the solution file for {self.path}.\n')
            handle.write('# File intentionally blank.\n')
        return True
