"""Test classes for grading search algorithms in Pacman.

This module contains test case classes for evaluating student search algorithm 
implementations in the Pacman AI project. Test cases verify properties like 
path optimality, nodes expanded, and heuristic admissibility.

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
    - Added type hints
    - Improved docstrings and documentation

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

import sys
import re
import testClasses
import textwrap

# import project specific code
import layout
import pacman
from game import Actions
from search import SearchProblem
from typing import List, Any, Optional, Union, Dict, Tuple, Callable

def wrap_solution(solution: Union[List[str], Any]) -> str:
    """Format a solution for printing in solution files.
    
    Args:
        solution: Either a list of actions or another solution type
        
    Returns:
        str: Formatted solution string with actions joined and wrapped
    """
    if isinstance(solution, list):
        return '\n'.join(textwrap.wrap(' '.join(solution)))
    else:
        return str(solution)

def followAction(state: Any, action: str, problem: SearchProblem) -> Optional[Any]:
    """Get resulting state from taking an action in given state.
    
    Args:
        state: Current state
        action: Action to take
        problem: Search problem instance
        
    Returns:
        Next state after taking action, or None if invalid action
    """
    for successor1, action1, cost1 in problem.getSuccessors(state):
        if action == action1:
            return successor1
    return None

def followPath(path: List[str], problem: SearchProblem) -> List[Any]:
    """Get sequence of states from following a path.
    
    Args:
        path: List of actions defining the path
        problem: Search problem instance
        
    Returns:
        List of states encountered along the path
    """
    state = problem.getStartState()
    states = [state]
    for action in path:
        state = followAction(state, action, problem)
        states.append(state)
    return states

def checkSolution(problem: SearchProblem, path: List[str]) -> bool:
    """Check if a path leads to a goal state.
    
    Args:
        problem: Search problem instance
        path: List of actions to check
        
    Returns:
        bool: True if path leads to goal state, False otherwise
    """
    state = problem.getStartState()
    for action in path:
        state = followAction(state, action, problem)
    return problem.isGoalState(state)

# Search problem on a plain graph
class GraphSearch(SearchProblem):
    """A search problem defined by a graph with states, actions, and costs.
    
    Attributes:
        expanded_states (List[str]): States visited during search
        start_state (str): Initial state
        goals (List[str]): List of goal states
        successors (Dict[str, List[Tuple[str, str, float]]]): State transitions
        orderedSuccessorTuples (List[Tuple[str, str, str, float]]): Edge tuples
    """

    def __init__(self, graph_text: str) -> None:
        """Initialize graph from text specification.
        
        Args:
            graph_text: String containing graph definition with format:
                start_state: <state>
                goal_states: <state1> <state2> ...
                <from_state> <action> <to_state> [cost]
                ...
                
        Raises:
            Exception: If graph specification is invalid
        """
        self.expanded_states: List[str] = []
        lines = graph_text.split('\n')
        
        r = re.match('start_state:(.*)', lines[0])
        if r is None:
            print("Broken graph:")
            print(f'"""{graph_text}"""')
            raise Exception("GraphSearch graph specification start_state not found or incorrect on line 0")
        self.start_state = r.group(1).strip()
        
        r = re.match('goal_states:(.*)', lines[1])
        if r is None:
            print("Broken graph:")
            print(f'"""{graph_text}"""')
            raise Exception("GraphSearch graph specification goal_states not found or incorrect on line 1")
        goals = r.group(1).split()
        self.goals = [str.strip(g) for g in goals]
        
        self.successors: Dict[str, List[Tuple[str, str, float]]] = {}
        all_states = set()
        self.orderedSuccessorTuples: List[Tuple[str, str, str, float]] = []
        
        for l in lines[2:]:
            if len(l.split()) == 3:
                start, action, next_state = l.split()
                cost = 1.0
            elif len(l.split()) == 4:
                start, action, next_state, cost = l.split()
            else:
                print("Broken graph:")
                print(f'"""{graph_text}"""')
                raise Exception(f"Invalid line in GraphSearch graph specification on line: {l}")
            cost = float(cost)
            self.orderedSuccessorTuples.append((start, action, next_state, cost))
            all_states.add(start)
            all_states.add(next_state)
            if start not in self.successors:
                self.successors[start] = []
            self.successors[start].append((next_state, action, cost))
        
        for s in all_states:
            if s not in self.successors:
                self.successors[s] = []

    def getStartState(self) -> str:
        """Get the initial state.
        
        Returns:
            Initial state string
        """
        return self.start_state

    def isGoalState(self, state: str) -> bool:
        """Check if state is a goal state.
        
        Args:
            state: State to check
            
        Returns:
            True if state is a goal state, False otherwise
        """
        return state in self.goals

    def getSuccessors(self, state: str) -> List[Tuple[str, str, float]]:
        """Get all successor states and actions from a state.
        
        Args:
            state: Current state
            
        Returns:
            List of (next_state, action, cost) tuples
        """
        self.expanded_states.append(state)
        return list(self.successors[state])

    def getCostOfActions(self, actions: List[str]) -> float:
        """Calculate total cost of a sequence of actions.
        
        Args:
            actions: List of actions
            
        Returns:
            Total cost of taking actions
            
        Raises:
            SystemExit: If action sequence is invalid
        """
        total_cost = 0.0
        state = self.start_state
        for a in actions:
            successors = self.successors[state]
            match = False
            for (next_state, action, cost) in successors:
                if a == action:
                    state = next_state
                    total_cost += cost
                    match = True
            if not match:
                print('invalid action sequence')
                sys.exit(1)
        return total_cost

    def getExpandedStates(self) -> List[str]:
        """Get states visited during search.
        
        Returns:
            List of expanded state strings
        """
        return self.expanded_states

    def __str__(self) -> str:
        """Get string representation of graph.
        
        Returns:
            Graph specification string
        """
        print(self.successors)
        edges = [f"{t[0]} {t[1]} {t[2]} {t[3]}" for t in self.orderedSuccessorTuples]
        return f"""start_state: {self.start_state}
goal_states: {" ".join(self.goals)}
{chr(10).join(edges)}"""


def parseHeuristic(heuristicText: str) -> Callable[[str, Any], float]:
    """Parse heuristic specification text into a heuristic function.
    
    Args:
        heuristicText: String containing heuristic values in format "state value"
            
    Returns:
        A heuristic function that takes a state and optional problem and returns
        the heuristic value for that state
        
    Raises:
        Exception: If heuristic text is malformed or state is invalid
    """
    heuristic = {}
    for line in heuristicText.split('\n'):
        tokens = line.split()
        if len(tokens) != 2:
            print("Broken heuristic:")
            print(f'"""{heuristicText}"""')
            raise Exception(f"GraphSearch heuristic specification broken at tokens: {tokens}")
        state, h = tokens
        heuristic[state] = float(h)

    def graphHeuristic(state: str, problem: Any = None) -> float:
        """Get heuristic value for a state.
        
        Args:
            state: State to get heuristic value for
            problem: Optional search problem instance
            
        Returns:
            Heuristic value for the state
            
        Raises:
            Exception: If state is not found in heuristic
        """
        if state in heuristic:
            return heuristic[state]
        else:
            import pprint
            pp = pprint.PrettyPrinter(indent=4)
            print("Heuristic:")
            pp.pprint(heuristic)
            raise Exception(f"Graph heuristic called with invalid state: {state}")

    return graphHeuristic

class GraphSearchTest(testClasses.TestCase):
    """Test case for graph search algorithms.
    
    Tests student implementations of graph search algorithms against provided
    test cases with known solutions.
    
    Attributes:
        graph_text (str): Text representation of graph to search
        alg (str): Name of search algorithm to test
        diagram (str): ASCII diagram of graph for display
        exactExpansionOrder (bool): Whether expansion order must match exactly
        heuristic (Optional[Callable]): Optional heuristic function for informed search
    """

    def __init__(self, question: 'Question', testDict: Dict[str, Any]) -> None:
        """Initialize GraphSearchTest.
        
        Args:
            question: Question this test belongs to
            testDict: Dictionary containing test parameters
        """
        super(GraphSearchTest, self).__init__(question, testDict)
        self.graph_text = testDict['graph']
        self.alg = testDict['algorithm']
        self.diagram = testDict['diagram']
        self.exactExpansionOrder = testDict.get('exactExpansionOrder', 'True').lower() == "true"
        if 'heuristic' in testDict:
            self.heuristic = parseHeuristic(testDict['heuristic'])
        else:
            self.heuristic = None

    def getSolInfo(self, search: Any) -> Tuple[Optional[List[str]], Optional[List[str]], Optional[str]]:
        """Get solution information by running search algorithm.
        
        Args:
            search: Search module containing algorithm implementations
            
        Returns:
            Tuple containing:
            - List of actions in solution path (or None if error)
            - List of expanded states (or None if error) 
            - Error message string (or None if successful)
        """
        alg = getattr(search, self.alg)
        problem = GraphSearch(self.graph_text)
        if self.heuristic is not None:
            solution = alg(problem, self.heuristic)
        else:
            solution = alg(problem)

        if not isinstance(solution, list):
            return None, None, f'The result of {self.alg} must be a list. (Instead, it is {type(solution)})'

        return solution, problem.getExpandedStates(), None

    def execute(self, grades: 'Grades', moduleDict: Dict[str, Any], solutionDict: Dict[str, Any]) -> bool:
        """Execute the test case.
        
        Args:
            grades: Grading object to track scores
            moduleDict: Dictionary containing student code modules
            solutionDict: Dictionary containing solution code
            
        Returns:
            bool: True if test passes, False otherwise
        """
        search = moduleDict['search']
        searchAgents = moduleDict['searchAgents']
        gold_solution = [str.split(solutionDict['solution']), str.split(solutionDict['rev_solution'])]
        gold_expanded_states = [str.split(solutionDict['expanded_states']), str.split(solutionDict['rev_expanded_states'])]

        solution, expanded_states, error = self.getSolInfo(search)
        if error is not None:
            grades.addMessage(f'FAIL: {self.path}')
            grades.addMessage(f'\t{error}')
            return False

        if solution in gold_solution and (not self.exactExpansionOrder or expanded_states in gold_expanded_states):
            grades.addMessage(f'PASS: {self.path}')
            grades.addMessage(f'\tsolution:\t\t{solution}')
            grades.addMessage(f'\texpanded_states:\t{expanded_states}')
            return True
        else:
            grades.addMessage(f'FAIL: {self.path}')
            grades.addMessage('\tgraph:')
            for line in self.diagram.split('\n'):
                grades.addMessage(f'\t    {line}')
            grades.addMessage(f'\tstudent solution:\t\t{solution}')
            grades.addMessage(f'\tstudent expanded_states:\t{expanded_states}')
            grades.addMessage('')
            grades.addMessage(f'\tcorrect solution:\t\t{gold_solution[0]}')
            grades.addMessage(f'\tcorrect expanded_states:\t{gold_expanded_states[0]}')
            grades.addMessage(f'\tcorrect rev_solution:\t\t{gold_solution[1]}')
            grades.addMessage(f'\tcorrect rev_expanded_states:\t{gold_expanded_states[1]}')
            return False

    def writeSolution(self, moduleDict: Dict[str, Any], filePath: str) -> bool:
        """Write solution for test to file.
        
        Args:
            moduleDict: Dictionary containing student code modules
            filePath: Path to write solution file
            
        Returns:
            bool: True if solution written successfully
            
        Raises:
            Exception: If error occurs in solution code
        """
        search = moduleDict['search']
        searchAgents = moduleDict['searchAgents']
        
        # open file and write comments
        with open(filePath, 'w') as handle:
            handle.write(f'# This is the solution file for {self.path}.\n')
            handle.write('# This solution is designed to support both right-to-left\n')
            handle.write('# and left-to-right implementations.\n')

            # write forward solution
            solution, expanded_states, error = self.getSolInfo(search)
            if error is not None:
                raise Exception(f"Error in solution code: {error}")
            handle.write(f'solution: "{" ".join(solution)}"\n')
            handle.write(f'expanded_states: "{" ".join(expanded_states)}"\n')

            # reverse and write backwards solution
            search.REVERSE_PUSH = not search.REVERSE_PUSH
            solution, expanded_states, error = self.getSolInfo(search)
            if error is not None:
                raise Exception(f"Error in solution code: {error}")
            handle.write(f'rev_solution: "{" ".join(solution)}"\n')
            handle.write(f'rev_expanded_states: "{" ".join(expanded_states)}"\n')

            # clean up
            search.REVERSE_PUSH = not search.REVERSE_PUSH
            
        return True

class PacmanSearchTest(testClasses.TestCase):
    """Test case for Pacman search algorithms.
    
    Tests search algorithm implementations by running them on Pacman layouts
    and comparing solutions and nodes expanded against reference values.
    
    Attributes:
        layout_text (str): Text representation of Pacman layout
        alg (str): Name of search algorithm to test
        layoutName (str): Name of layout being tested
        leewayFactor (float): Factor by which expanded nodes can exceed reference
        costFn (Optional[Callable]): Custom cost function for search problem
        searchProblemClassName (str): Name of search problem class to use
        heuristicName (Optional[str]): Name of heuristic function to use
    """

    def __init__(self, question: 'Question', testDict: Dict[str, Any]) -> None:
        """Initialize PacmanSearchTest.
        
        Args:
            question: Question object this test belongs to
            testDict: Dictionary containing test parameters
        """
        super(PacmanSearchTest, self).__init__(question, testDict)
        self.layout_text = testDict['layout']
        self.alg = testDict['algorithm']
        self.layoutName = testDict['layoutName']

        # Optional parameters with defaults
        self.leewayFactor = float(testDict.get('leewayFactor', '1'))
        self.costFn = eval(testDict.get('costFn', 'None'))
        self.searchProblemClassName = testDict.get('searchProblemClass', 'PositionSearchProblem')
        self.heuristicName = testDict.get('heuristic', None)

    def getSolInfo(self, search: Any, searchAgents: Any) -> Tuple[Optional[List[str]], Optional[int], Optional[str]]:
        """Get solution information by running search algorithm.
        
        Args:
            search: Search algorithm module
            searchAgents: Search agents module
            
        Returns:
            Tuple containing:
            - List of actions in solution, or None if error
            - Number of nodes expanded, or None if error  
            - Error message string, or None if successful
        """
        alg = getattr(search, self.alg)
        lay = layout.Layout([l.strip() for l in self.layout_text.split('\n')])
        start_state = pacman.GameState()
        start_state.initialize(lay, 0)

        problemClass = getattr(searchAgents, self.searchProblemClassName)
        problemOptions = {}
        if self.costFn is not None:
            problemOptions['costFn'] = self.costFn
        problem = problemClass(start_state, **problemOptions)
        heuristic = getattr(searchAgents, self.heuristicName) if self.heuristicName is not None else None

        if heuristic is not None:
            solution = alg(problem, heuristic)
        else:
            solution = alg(problem)

        if not isinstance(solution, list):
            return None, None, f'The result of {self.alg} must be a list. (Instead, it is {type(solution)})'

        from game import Directions
        dirs = Directions.LEFT.keys()
        if [el in dirs for el in solution].count(False) != 0:
            return None, None, f'Output of {self.alg} must be a list of actions from game.Directions'

        expanded = problem._expanded
        return solution, expanded, None

    def execute(self, grades: 'Grades', moduleDict: Dict[str, Any], solutionDict: Dict[str, Any]) -> bool:
        """Execute the test case.
        
        Args:
            grades: Grading object to track scores
            moduleDict: Dictionary containing student code modules
            solutionDict: Dictionary containing solution data
            
        Returns:
            bool: True if test passes, False otherwise
        """
        search = moduleDict['search']
        searchAgents = moduleDict['searchAgents']
        gold_solution = [str.split(solutionDict['solution']), str.split(solutionDict['rev_solution'])]
        gold_expanded = max(int(solutionDict['expanded_nodes']), int(solutionDict['rev_expanded_nodes']))

        solution, expanded, error = self.getSolInfo(search, searchAgents)
        if error is not None:
            grades.addMessage(f'FAIL: {self.path}')
            grades.addMessage(f'{error}')
            return False

        if solution not in gold_solution:
            grades.addMessage(f'FAIL: {self.path}')
            grades.addMessage('Solution not correct.')
            grades.addMessage(f'\tstudent solution length: {len(solution)}')
            grades.addMessage(f'\tstudent solution:\n{wrap_solution(solution)}')
            grades.addMessage('')
            grades.addMessage(f'\tcorrect solution length: {len(gold_solution[0])}')
            grades.addMessage(f'\tcorrect (reversed) solution length: {len(gold_solution[1])}')
            grades.addMessage(f'\tcorrect solution:\n{wrap_solution(gold_solution[0])}')
            grades.addMessage(f'\tcorrect (reversed) solution:\n{wrap_solution(gold_solution[1])}')
            return False

        if expanded > self.leewayFactor * gold_expanded and expanded > gold_expanded + 1:
            grades.addMessage(f'FAIL: {self.path}')
            grades.addMessage('Too many node expanded; are you expanding nodes twice?')
            grades.addMessage(f'\tstudent nodes expanded: {expanded}')
            grades.addMessage('')
            grades.addMessage(f'\tcorrect nodes expanded: {gold_expanded} (leewayFactor {self.leewayFactor})')
            return False

        grades.addMessage(f'PASS: {self.path}')
        grades.addMessage(f'\tpacman layout:\t\t{self.layoutName}')
        grades.addMessage(f'\tsolution length: {len(solution)}')
        grades.addMessage(f'\tnodes expanded:\t\t{expanded}')
        return True

    def writeSolution(self, moduleDict: Dict[str, Any], filePath: str) -> bool:
        """Write solution for test to file.
        
        Args:
            moduleDict: Dictionary containing student code modules
            filePath: Path to write solution file
            
        Returns:
            bool: True if solution written successfully
            
        Raises:
            Exception: If error occurs in solution code
        """
        search = moduleDict['search']
        searchAgents = moduleDict['searchAgents']
        
        with open(filePath, 'w') as handle:
            handle.write(f'# This is the solution file for {self.path}.\n')
            handle.write('# This solution is designed to support both right-to-left\n')
            handle.write('# and left-to-right implementations.\n')
            handle.write(f'# Number of nodes expanded must be with a factor of {self.leewayFactor} of the numbers below.\n')

            # Write forward solution
            solution, expanded, error = self.getSolInfo(search, searchAgents)
            if error is not None:
                raise Exception(f"Error in solution code: {error}")
            handle.write(f'solution: """\n{wrap_solution(solution)}\n"""\n')
            handle.write(f'expanded_nodes: "{expanded}"\n')

            # Write backward solution
            search.REVERSE_PUSH = not search.REVERSE_PUSH
            solution, expanded, error = self.getSolInfo(search, searchAgents)
            if error is not None:
                raise Exception(f"Error in solution code: {error}")
            handle.write(f'rev_solution: """\n{wrap_solution(solution)}\n"""\n')
            handle.write(f'rev_expanded_nodes: "{expanded}"\n')

            # Clean up
            search.REVERSE_PUSH = not search.REVERSE_PUSH

        return True


def getStatesFromPath(start: Tuple[int, int], path: List[str]) -> List[Tuple[int, int]]:
    """Returns the list of states visited along the path.
    
    Args:
        start: Initial (x,y) position
        path: List of actions/directions to follow
        
    Returns:
        List of (x,y) positions visited along the path
    """
    vis = [start]
    curr = start
    for a in path:
        x, y = curr
        dx, dy = Actions.directionToVector(a)
        curr = (int(x + dx), int(y + dy))
        vis.append(curr)
    return vis

class CornerProblemTest(testClasses.TestCase):
    """Test case for finding path to visit all corners.
    
    Tests that search algorithms can find valid paths visiting all corner 
    positions in a Pacman maze layout.
    
    Attributes:
        layoutText (str): Text representation of maze layout
        layoutName (str): Name of layout being tested
    """

    def __init__(self, question: 'Question', testDict: Dict[str, Any]) -> None:
        """Initialize CornerProblemTest.
        
        Args:
            question: Question object this test belongs to
            testDict: Dictionary containing test parameters
        """
        super(CornerProblemTest, self).__init__(question, testDict)
        self.layoutText = testDict['layout']
        self.layoutName = testDict['layoutName']

    def solution(self, search: Any, searchAgents: Any) -> Tuple[List[str], List[Tuple[int, int]]]:
        """Find solution path and check corners visited.
        
        Args:
            search: Search algorithm module
            searchAgents: Search agents module
            
        Returns:
            Tuple containing:
            - List of actions in solution path
            - List of corner positions that were not visited
        """
        lay = layout.Layout([l.strip() for l in self.layoutText.split('\n')])
        gameState = pacman.GameState()
        gameState.initialize(lay, 0)
        problem = searchAgents.CornersProblem(gameState)
        path = search.bfs(problem)

        gameState = pacman.GameState()
        gameState.initialize(lay, 0)
        visited = getStatesFromPath(gameState.getPacmanPosition(), path)
        top, right = gameState.getWalls().height-2, gameState.getWalls().width-2
        missedCorners = [p for p in ((1,1), (1,top), (right, 1), (right, top)) if p not in visited]

        return path, missedCorners

    def execute(self, grades: 'Grades', moduleDict: Dict[str, Any], solutionDict: Dict[str, Any]) -> bool:
        """Execute test case and grade solution.
        
        Args:
            grades: Grading object for reporting results
            moduleDict: Dictionary containing student code modules
            solutionDict: Dictionary containing solution data
            
        Returns:
            bool: True if solution passes all tests
        """
        search = moduleDict['search']
        searchAgents = moduleDict['searchAgents']
        gold_length = int(solutionDict['solution_length'])
        solution, missedCorners = self.solution(search, searchAgents)

        if not isinstance(solution, list):
            grades.addMessage(f'FAIL: {self.path}')
            grades.addMessage(f'The result must be a list. (Instead, it is {type(solution)})')
            return False

        if len(missedCorners) != 0:
            grades.addMessage(f'FAIL: {self.path}')
            grades.addMessage(f'Corners missed: {missedCorners}')
            return False

        if len(solution) != gold_length:
            grades.addMessage(f'FAIL: {self.path}')
            grades.addMessage('Optimal solution not found.')
            grades.addMessage(f'\tstudent solution length:\n{len(solution)}')
            grades.addMessage('')
            grades.addMessage(f'\tcorrect solution length:\n{gold_length}')
            return False

        grades.addMessage(f'PASS: {self.path}')
        grades.addMessage(f'\tpacman layout:\t\t{self.layoutName}')
        grades.addMessage(f'\tsolution length:\t\t{len(solution)}')
        return True

    def writeSolution(self, moduleDict: Dict[str, Any], filePath: str) -> bool:
        """Write solution for test to file.
        
        Args:
            moduleDict: Dictionary containing student code modules
            filePath: Path to write solution file
            
        Returns:
            bool: True if solution written successfully
        """
        search = moduleDict['search']
        searchAgents = moduleDict['searchAgents']
        
        # open file and write comments
        with open(filePath, 'w') as handle:
            handle.write(f'# This is the solution file for {self.path}.\n')

            print(f"Solving problem {self.layoutName}")
            print(self.layoutText)

            path, _ = self.solution(search, searchAgents)
            length = len(path)
            print("Problem solved")

            handle.write(f'solution_length: "{length}"\n')

        return True


class HeuristicTest(testClasses.TestCase):
    """Test case for evaluating heuristic functions.
    
    Tests if a heuristic function satisfies required properties like admissibility,
    consistency, and non-triviality.
    
    Attributes:
        layoutText (str): Text representation of Pacman layout
        layoutName (str): Name of layout being tested
        searchProblemClassName (str): Name of search problem class to use
        heuristicName (str): Name of heuristic function to test
    """

    def __init__(self, question: 'Question', testDict: Dict[str, Any]) -> None:
        """Initialize HeuristicTest.
        
        Args:
            question: Question object this test belongs to
            testDict: Dictionary containing test parameters
        """
        super(HeuristicTest, self).__init__(question, testDict)
        self.layoutText = testDict['layout']
        self.layoutName = testDict['layoutName']
        self.searchProblemClassName = testDict['searchProblemClass']
        self.heuristicName = testDict['heuristic']

    def setupProblem(self, searchAgents: Any) -> Tuple[SearchProblem, Any, Callable]:
        """Set up search problem and heuristic for testing.
        
        Args:
            searchAgents: Search agents module
            
        Returns:
            Tuple containing:
            - Search problem instance
            - Initial state
            - Heuristic function
        """
        lay = layout.Layout([l.strip() for l in self.layoutText.split('\n')])
        gameState = pacman.GameState()
        gameState.initialize(lay, 0)
        problemClass = getattr(searchAgents, self.searchProblemClassName)
        problem = problemClass(gameState)
        state = problem.getStartState()
        heuristic = getattr(searchAgents, self.heuristicName)

        return problem, state, heuristic

    def checkHeuristic(self, heuristic: Callable, problem: SearchProblem, 
                      state: Any, solutionCost: int) -> Tuple[bool, str]:
        """Check if heuristic satisfies required properties.
        
        Args:
            heuristic: Heuristic function to test
            problem: Search problem instance
            state: Current state to evaluate
            solutionCost: Cost of optimal solution
            
        Returns:
            Tuple containing:
            - Boolean indicating if heuristic passed all tests
            - Error message if failed, empty string if passed
        """
        h0 = heuristic(state, problem)

        if solutionCost == 0:
            if h0 == 0:
                return True, ''
            else:
                return False, 'Heuristic failed H(goal) == 0 test'

        if h0 < 0:
            return False, 'Heuristic failed H >= 0 test'
        if not h0 > 0:
            return False, 'Heuristic failed non-triviality test'
        if not h0 <= solutionCost:
            return False, 'Heuristic failed admissibility test'

        for succ, action, stepCost in problem.getSuccessors(state):
            h1 = heuristic(succ, problem)
            if h1 < 0: 
                return False, 'Heuristic failed H >= 0 test'
            if h0 - h1 > stepCost: 
                return False, 'Heuristic failed consistency test'

        return True, ''

    def execute(self, grades: Any, moduleDict: Dict[str, Any], 
               solutionDict: Dict[str, Any]) -> bool:
        """Execute heuristic tests.
        
        Args:
            grades: Grading object
            moduleDict: Dictionary containing student code modules
            solutionDict: Dictionary containing solution data
            
        Returns:
            bool: True if heuristic passes all tests, False otherwise
        """
        search = moduleDict['search']
        searchAgents = moduleDict['searchAgents']
        solutionCost = int(solutionDict['solution_cost'])
        problem, state, heuristic = self.setupProblem(searchAgents)

        passed, message = self.checkHeuristic(heuristic, problem, state, solutionCost)

        if not passed:
            grades.addMessage(f'FAIL: {self.path}')
            grades.addMessage(message)
            return False
        else:
            grades.addMessage(f'PASS: {self.path}')
            return True

    def writeSolution(self, moduleDict: Dict[str, Any], filePath: str) -> bool:
        """Write solution for test to file.
        
        Args:
            moduleDict: Dictionary containing student code modules
            filePath: Path to write solution file
            
        Returns:
            bool: True if solution written successfully
        """
        search = moduleDict['search']
        searchAgents = moduleDict['searchAgents']
        
        with open(filePath, 'w') as handle:
            handle.write(f'# This is the solution file for {self.path}.\n')

            print(f"Solving problem {self.layoutName} {self.heuristicName}")
            print(self.layoutText)
            problem, _, heuristic = self.setupProblem(searchAgents)
            path = search.astar(problem, heuristic)
            cost = problem.getCostOfActions(path)
            print("Problem solved")

            handle.write(f'solution_cost: "{cost}"\n')
            
        return True


class HeuristicGrade(testClasses.TestCase):
    """Test case for grading heuristic performance.
    
    Grades heuristic functions based on number of nodes expanded during search.
    
    Attributes:
        layoutText (str): Text representation of Pacman layout
        layoutName (str): Name of layout being tested
        searchProblemClassName (str): Name of search problem class to use
        heuristicName (str): Name of heuristic function to test
        basePoints (int): Base points awarded for finding solution
        thresholds (List[int]): Node expansion thresholds for additional points
    """

    def __init__(self, question: 'Question', testDict: Dict[str, Any]) -> None:
        """Initialize HeuristicGrade.
        
        Args:
            question: Question object this test belongs to
            testDict: Dictionary containing test parameters
        """
        super(HeuristicGrade, self).__init__(question, testDict)
        self.layoutText = testDict['layout']
        self.layoutName = testDict['layoutName']
        self.searchProblemClassName = testDict['searchProblemClass']
        self.heuristicName = testDict['heuristic']
        self.basePoints = int(testDict['basePoints'])
        self.thresholds = [int(t) for t in testDict['gradingThresholds'].split()]

    def setupProblem(self, searchAgents: Any) -> Tuple[SearchProblem, Any, Callable]:
        """Set up search problem and heuristic for testing.
        
        Args:
            searchAgents: Search agents module
            
        Returns:
            Tuple containing:
            - Search problem instance
            - Initial state
            - Heuristic function
        """
        lay = layout.Layout([l.strip() for l in self.layoutText.split('\n')])
        gameState = pacman.GameState()
        gameState.initialize(lay, 0)
        problemClass = getattr(searchAgents, self.searchProblemClassName)
        problem = problemClass(gameState)
        state = problem.getStartState()
        heuristic = getattr(searchAgents, self.heuristicName)

        return problem, state, heuristic

    def execute(self, grades: Any, moduleDict: Dict[str, Any], 
               solutionDict: Dict[str, Any]) -> bool:
        """Execute heuristic grading.
        
        Args:
            grades: Grading object
            moduleDict: Dictionary containing student code modules
            solutionDict: Dictionary containing solution data
            
        Returns:
            bool: True if solution found, False otherwise
        """
        search = moduleDict['search']
        searchAgents = moduleDict['searchAgents']
        problem, _, heuristic = self.setupProblem(searchAgents)

        path = search.astar(problem, heuristic)
        expanded = problem._expanded

        if not checkSolution(problem, path):
            grades.addMessage(f'FAIL: {self.path}')
            grades.addMessage('\tReturned path is not a solution.')
            grades.addMessage(f'\tpath returned by astar: {expanded}')
            return False

        grades.addPoints(self.basePoints)
        points = 0
        for threshold in self.thresholds:
            if expanded <= threshold:
                points += 1
        grades.addPoints(points)
        if points >= len(self.thresholds):
            grades.addMessage(f'PASS: {self.path}')
        else:
            grades.addMessage(f'FAIL: {self.path}')
        grades.addMessage(f'\texpanded nodes: {expanded}')
        grades.addMessage(f'\tthresholds: {self.thresholds}')

        return True

    def writeSolution(self, moduleDict: Dict[str, Any], filePath: str) -> bool:
        """Write solution for test to file.
        
        Args:
            moduleDict: Dictionary containing student code modules
            filePath: Path to write solution file
            
        Returns:
            bool: True if solution written successfully
        """
        with open(filePath, 'w') as handle:
            handle.write(f'# This is the solution file for {self.path}.\n')
            handle.write('# File intentionally blank.\n')
        return True


class ClosestDotTest(testClasses.TestCase):
    """Test case for finding path to closest dot.
    
    Tests that search agents can find valid paths to the closest food dot
    in a Pacman maze layout.
    
    Attributes:
        layoutText (str): Text representation of maze layout
        layoutName (str): Name of layout being tested
    """

    def __init__(self, question: 'Question', testDict: Dict[str, Any]) -> None:
        """Initialize ClosestDotTest.
        
        Args:
            question: Question object this test belongs to
            testDict: Dictionary containing test parameters
        """
        super(ClosestDotTest, self).__init__(question, testDict)
        self.layoutText = testDict['layout']
        self.layoutName = testDict['layoutName']

    def solution(self, searchAgents: Any) -> List[str]:
        """Find solution path to closest dot.
        
        Args:
            searchAgents: Search agents module
            
        Returns:
            List of actions in solution path
        """
        lay = layout.Layout([l.strip() for l in self.layoutText.split('\n')])
        gameState = pacman.GameState()
        gameState.initialize(lay, 0)
        path = searchAgents.ClosestDotSearchAgent().findPathToClosestDot(gameState)
        return path

    def execute(self, grades: 'Grades', moduleDict: Dict[str, Any], solutionDict: Dict[str, Any]) -> bool:
        """Execute test case and grade solution.
        
        Args:
            grades: Grading object for scoring
            moduleDict: Dictionary containing student code modules
            solutionDict: Dictionary containing solution data
            
        Returns:
            bool: True if solution correct, False otherwise
        """
        search = moduleDict['search']
        searchAgents = moduleDict['searchAgents']
        gold_length = int(solutionDict['solution_length'])
        solution = self.solution(searchAgents)

        if not isinstance(solution, list):
            grades.addMessage(f'FAIL: {self.path}')
            grades.addMessage(f'\tThe result must be a list. (Instead, it is {type(solution)})')
            return False

        if len(solution) != gold_length:
            grades.addMessage(f'FAIL: {self.path}')
            grades.addMessage('Closest dot not found.')
            grades.addMessage(f'\tstudent solution length:\n{len(solution)}')
            grades.addMessage('')
            grades.addMessage(f'\tcorrect solution length:\n{gold_length}')
            return False

        grades.addMessage(f'PASS: {self.path}')
        grades.addMessage(f'\tpacman layout:\t\t{self.layoutName}')
        grades.addMessage(f'\tsolution length:\t\t{len(solution)}')
        return True

    def writeSolution(self, moduleDict: Dict[str, Any], filePath: str) -> bool:
        """Write solution for test to file.
        
        Args:
            moduleDict: Dictionary containing student code modules
            filePath: Path to write solution file
            
        Returns:
            bool: True if solution written successfully
        """
        search = moduleDict['search']
        searchAgents = moduleDict['searchAgents']
        
        # open file and write comments
        with open(filePath, 'w') as handle:
            handle.write(f'# This is the solution file for {self.path}.\n')

            print(f"Solving problem {self.layoutName}")
            print(self.layoutText)

            length = len(self.solution(searchAgents))
            print("Problem solved")

            handle.write(f'solution_length: "{length}"\n')
            
        return True


class CornerHeuristicSanity(testClasses.TestCase):
    """Test case for checking corner heuristic properties.
    
    Tests if the corner heuristic satisfies required properties like admissibility,
    consistency, non-triviality, and proper behavior at goal states.
    
    Attributes:
        layout_text (str): Text representation of Pacman layout
    """

    def __init__(self, question: 'Question', testDict: Dict[str, Any]) -> None:
        """Initialize CornerHeuristicSanity test.
        
        Args:
            question: Question object this test belongs to
            testDict: Dictionary containing test parameters
        """
        super(CornerHeuristicSanity, self).__init__(question, testDict)
        self.layout_text = testDict['layout']

    def execute(self, grades: 'Grades', moduleDict: Dict[str, Any], 
                solutionDict: Dict[str, Any]) -> bool:
        """Execute the test case.
        
        Tests corner heuristic for:
        - Consistency between states
        - Non-triviality (not always 0)
        - Admissibility (never overestimates)
        - Non-negative values
        - Zero at goal states
        
        Args:
            grades: Grading object for scoring
            moduleDict: Dictionary containing student code modules
            solutionDict: Dictionary containing solution data
            
        Returns:
            bool: True if heuristic passes all tests, False otherwise
        """
        search = moduleDict['search']
        searchAgents = moduleDict['searchAgents']
        game_state = pacman.GameState()
        lay = layout.Layout([l.strip() for l in self.layout_text.split('\n')])
        game_state.initialize(lay, 0)
        problem = searchAgents.CornersProblem(game_state)
        start_state = problem.getStartState()
        h0 = searchAgents.cornersHeuristic(start_state, problem)
        succs = problem.getSuccessors(start_state)
        # cornerConsistencyA
        for succ in succs:
            h1 = searchAgents.cornersHeuristic(succ[0], problem)
            if h0 - h1 > 1:
                grades.addMessage('FAIL: inconsistent heuristic')
                return False
        heuristic_cost = searchAgents.cornersHeuristic(start_state, problem)
        true_cost = float(solutionDict['cost'])
        # cornerNontrivial
        if heuristic_cost == 0:
            grades.addMessage('FAIL: must use non-trivial heuristic')
            return False
        # cornerAdmissible
        if heuristic_cost > true_cost:
            grades.addMessage('FAIL: Inadmissible heuristic')
            return False
        path = solutionDict['path'].split()
        states = followPath(path, problem)
        heuristics = []
        for state in states:
            heuristics.append(searchAgents.cornersHeuristic(state, problem))
        for i in range(0, len(heuristics) - 1):
            h0 = heuristics[i]
            h1 = heuristics[i+1]
            # cornerConsistencyB
            if h0 - h1 > 1:
                grades.addMessage('FAIL: inconsistent heuristic')
                return False
            # cornerPosH
            if h0 < 0 or h1 <0:
                grades.addMessage('FAIL: non-positive heuristic')
                return False
        # cornerGoalH
        if heuristics[len(heuristics) - 1] != 0:
            grades.addMessage('FAIL: heuristic non-zero at goal')
            return False
        grades.addMessage('PASS: heuristic value less than true cost at start state')
        return True

    def writeSolution(self, moduleDict: Dict[str, Any], filePath: str) -> bool:
        """Write solution for test to file.
        
        Args:
            moduleDict: Dictionary containing student code modules
            filePath: Path to write solution file
            
        Returns:
            bool: True if solution written successfully
        """
        search = moduleDict['search']
        searchAgents = moduleDict['searchAgents']
        
        # write comment
        with open(filePath, 'w') as handle:
            handle.write('# In order for a heuristic to be admissible, the value\n')
            handle.write('# of the heuristic must be less at each state than the\n')
            handle.write('# true cost of the optimal path from that state to a goal.\n')

            # solve problem and write solution
            lay = layout.Layout([l.strip() for l in self.layout_text.split('\n')])
            start_state = pacman.GameState()
            start_state.initialize(lay, 0)
            problem = searchAgents.CornersProblem(start_state)
            solution = search.astar(problem, searchAgents.cornersHeuristic)
            handle.write(f'cost: "{len(solution)}"\n')
            handle.write(f'path: """\n{wrap_solution(solution)}\n"""\n')
            
        return True


class CornerHeuristicPacman(testClasses.TestCase):
    """Test case for evaluating corner heuristic performance.
    
    Tests if the corner heuristic is admissible and consistent, and grades its
    performance based on number of nodes expanded during A* search.
    
    Attributes:
        layout_text (str): Text representation of Pacman layout
    """

    def __init__(self, question: 'Question', testDict: Dict[str, Any]) -> None:
        """Initialize CornerHeuristicPacman test.
        
        Args:
            question: Question object this test belongs to
            testDict: Dictionary containing test parameters
        """
        super(CornerHeuristicPacman, self).__init__(question, testDict)
        self.layout_text = testDict['layout']

    def execute(self, grades: 'Grades', moduleDict: Dict[str, Any], 
                solutionDict: Dict[str, Any]) -> bool:
        """Execute test case and grade performance.
        
        Args:
            grades: Grading object to record results
            moduleDict: Dictionary containing student code modules
            solutionDict: Dictionary containing solution data
            
        Returns:
            bool: True if heuristic passes all tests, False otherwise
        """
        search = moduleDict['search']
        searchAgents = moduleDict['searchAgents']
        
        true_cost = float(solutionDict['cost'])
        thresholds = [int(x) for x in solutionDict['thresholds'].split()]
        
        # Set up game state and problem
        game_state = pacman.GameState()
        lay = layout.Layout([l.strip() for l in self.layout_text.split('\n')])
        game_state.initialize(lay, 0)
        problem = searchAgents.CornersProblem(game_state)
        start_state = problem.getStartState()
        
        # Check admissibility
        if searchAgents.cornersHeuristic(start_state, problem) > true_cost:
            grades.addMessage('FAIL: Inadmissible heuristic')
            return False
            
        # Run A* search
        path = search.astar(problem, searchAgents.cornersHeuristic)
        print(f"path: {path}")
        print(f"path length: {len(path)}")
        
        # Check consistency
        cost = problem.getCostOfActions(path)
        if cost > true_cost:
            grades.addMessage('FAIL: Inconsistent heuristic')
            return False
            
        # Grade based on nodes expanded
        expanded = problem._expanded
        points = sum(1 for threshold in thresholds if expanded <= threshold)
        grades.addPoints(points)
        
        if points >= len(thresholds):
            grades.addMessage(f'PASS: Heuristic resulted in expansion of {expanded} nodes')
        else:
            grades.addMessage(f'FAIL: Heuristic resulted in expansion of {expanded} nodes')
        return True

    def writeSolution(self, moduleDict: Dict[str, Any], filePath: str) -> bool:
        """Write solution for test to file.
        
        Args:
            moduleDict: Dictionary containing student code modules
            filePath: Path to write solution file
            
        Returns:
            bool: True if solution written successfully
        """
        search = moduleDict['search']
        searchAgents = moduleDict['searchAgents']
        
        # Write solution file
        with open(filePath, 'w') as handle:
            handle.write('# This solution file specifies the length of the optimal path\n')
            handle.write('# as well as the thresholds on number of nodes expanded to be\n')
            handle.write('# used in scoring.\n')

            # Solve problem and write solution
            lay = layout.Layout([l.strip() for l in self.layout_text.split('\n')])
            start_state = pacman.GameState()
            start_state.initialize(lay, 0)
            problem = searchAgents.CornersProblem(start_state)
            solution = search.astar(problem, searchAgents.cornersHeuristic)
            
            handle.write(f'cost: "{len(solution)}"\n')
            handle.write(f'path: """\n{wrap_solution(solution)}\n"""\n')
            handle.write('thresholds: "2000 1600 1200"\n')
            
        return True

