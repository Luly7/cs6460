"""Search agents for the Pacman AI project.

This module contains various search agents that control Pacman's movement through
the maze using different search algorithms and heuristics.

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
    - verified to run with Python 3.13
    

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

"""
================================================================================
                               SEARCH AGENTS
================================================================================

This file contains all of the agents that can be selected to control Pacman.  To
select an agent, use the '-p' option when running pacman.py.  Arguments can be
passed to your agent using '-a'.  For example, to load a SearchAgent that uses
depth first search (dfs), run the following command:

> python pacman.py -p SearchAgent -a fn=depthFirstSearch

Commands to invoke other search strategies can be found in the project
description.

Please only change the parts of the file you are asked to.  Look for the lines
that say

"*** YOUR CODE HERE ***"

The parts you fill in start about 3/4 of the way down.  Follow the project
description for details.

Good luck and happy searching!
================================================================================
"""

import math
from math import dist
from game import Directions
from game import Agent
from game import Actions
import util
import time
import search
from typing import List, Tuple, Any, Optional, Callable, Dict


class GoWestAgent(Agent):
    """An agent that goes West until it can't.
    
    Attributes:
        None
    """

    def getAction(self, state: Any) -> str:
        """Returns the next action for the agent based on the game state.
        
        Args:
            state: A GameState object representing the current game state
            
        Returns:
            str: Either Directions.WEST if possible, or Directions.STOP otherwise
        """
        if Directions.WEST in state.getLegalPacmanActions():
            return Directions.WEST
        else:
            return Directions.STOP


class SearchAgent(Agent):
    """A general search agent that finds paths using specified search algorithms.
    
    This agent uses a supplied search algorithm and problem to find a path to a goal,
    then follows that path one step at a time.
    
    Attributes:
        searchFunction (Callable): The search algorithm to use (e.g. DFS, BFS)
        searchType (Any): The type of search problem to solve
        actions (List[str]): The sequence of actions to reach the goal
        actionIndex (int): Index tracking current position in action sequence
    """

    def __init__(self, fn: str = 'depthFirstSearch', 
                 prob: str = 'PositionSearchProblem',
                 heuristic: str = 'nullHeuristic') -> None:
        """Initialize the SearchAgent.
        
        Args:
            fn: Name of search function to use (default: 'depthFirstSearch')
            prob: Name of search problem type (default: 'PositionSearchProblem') 
            heuristic: Name of heuristic function (default: 'nullHeuristic')
            
        Raises:
            AttributeError: If search function, problem, or heuristic not found
        """
        if fn not in dir(search):
            raise AttributeError(f'{fn} is not a search function in search.py.')
        func = getattr(search, fn)
        if 'heuristic' not in func.__code__.co_varnames:
            print(f'[SearchAgent] using function {fn}')
            self.searchFunction = func
        else:
            if heuristic in globals().keys():
                heur = globals()[heuristic]
            elif heuristic in dir(search):
                heur = getattr(search, heuristic)
            else:
                raise AttributeError(f'{heuristic} is not a function in searchAgents.py or search.py.')
            print(f'[SearchAgent] using function {fn} and heuristic {heuristic}')
            self.searchFunction = lambda x: func(x, heuristic=heur)

        if prob not in globals().keys() or not prob.endswith('Problem'):
            raise AttributeError(f'{prob} is not a search problem type in SearchAgents.py.')
        self.searchType = globals()[prob]
        print(f'[SearchAgent] using problem type {prob}')

    def registerInitialState(self, state: Any) -> None:
        """Find path to goal when first seeing game board layout.
        
        This method computes the path to the goal and stores it for later use
        by getAction().
        
        Args:
            state: A GameState object representing initial state
            
        Raises:
            Exception: If no search function was provided
        """
        if self.searchFunction == None: 
            raise Exception("No search function provided for SearchAgent")
        starttime = time.time()
        problem = self.searchType(state)
        self.actions = self.searchFunction(problem)
        totalCost = problem.getCostOfActions(self.actions)
        print(f'Path found with total cost of {totalCost} in {time.time() - starttime:.1f} seconds')
        if '_expanded' in dir(problem): 
            print(f'Search nodes expanded: {problem._expanded}')

    def getAction(self, state: Any) -> str:
        """Return next action in the stored path.
        
        Args:
            state: A GameState object (unused)
            
        Returns:
            str: Next action to take, or Directions.STOP if no more actions
        """
        if 'actionIndex' not in dir(self): 
            self.actionIndex = 0
        i = self.actionIndex
        self.actionIndex += 1
        if i < len(self.actions):
            return self.actions[i]
        else:
            return Directions.STOP

class PositionSearchProblem(search.SearchProblem):
    """A search problem for finding paths to a particular position on the Pacman board.
    
    The state space consists of (x,y) positions in a Pacman game. This search problem
    is fully specified and should not be modified.
    
    Attributes:
        walls: 2D array of booleans indicating wall positions
        startState: Initial (x,y) position of Pacman
        goal: Target (x,y) position to reach
        costFn: Function that returns cost for moving to a position
        visualize: Whether to visualize search progress
        _visited: Dict tracking visited states
        _visitedlist: List of visited states for visualization
        _expanded: Number of states expanded during search
    """

    def __init__(self, gameState: Any, costFn: Callable = lambda x: 1, 
                 goal: Tuple[int, int] = (1,1), start: Optional[Tuple[int, int]] = None, 
                 warn: bool = True, visualize: bool = True) -> None:
        """Initialize position search problem.
        
        Args:
            gameState: A GameState object representing game state
            costFn: Function that returns cost for moving to a position
            goal: Target (x,y) position to reach
            start: Optional starting position, defaults to Pacman's position
            warn: Whether to show warning for invalid maze configurations
            visualize: Whether to visualize search progress
        """
        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition()
        if start is not None: 
            self.startState = start
        self.goal = goal
        self.costFn = costFn
        self.visualize = visualize
        if warn and (gameState.getNumFood() != 1 or not gameState.hasFood(*goal)):
            print('Warning: this does not look like a regular search maze')

        # For display purposes
        self._visited, self._visitedlist, self._expanded = {}, [], 0 # DO NOT CHANGE

    def getStartState(self) -> Tuple[int, int]:
        """Return initial state.
        
        Returns:
            Initial (x,y) position
        """
        return self.startState

    def isGoalState(self, state: Tuple[int, int]) -> bool:
        """Check if state is goal state.
        
        Args:
            state: Current (x,y) position
            
        Returns:
            True if state is goal state, False otherwise
        """
        isGoal = state == self.goal

        # For display purposes only
        if isGoal and self.visualize:
            self._visitedlist.append(state)
            import __main__
            if '_display' in dir(__main__):
                if 'drawExpandedCells' in dir(__main__._display):
                    __main__._display.drawExpandedCells(self._visitedlist)

        return isGoal

    def getSuccessors(self, state: Tuple[int, int]) -> List[Tuple[Tuple[int, int], str, float]]:
        """Get successor states and actions to reach them.
        
        For a given state, returns list of (successor, action, stepCost) tuples,
        where:
        - successor is a successor state
        - action is the action required to get there
        - stepCost is the cost of taking that action
        
        Args:
            state: Current (x,y) position
            
        Returns:
            List of (successor, action, cost) tuples
        """
        successors = []
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x, y = state
            dx, dy = Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextState = (nextx, nexty)
                cost = self.costFn(nextState)
                successors.append((nextState, action, cost))

        # Bookkeeping for display purposes
        self._expanded += 1 # DO NOT CHANGE
        if state not in self._visited:
            self._visited[state] = True
            self._visitedlist.append(state)

        return successors

    def getCostOfActions(self, actions: Optional[List[str]]) -> float:
        """Calculate total cost of a sequence of actions.
        
        Args:
            actions: List of actions to take
            
        Returns:
            Total cost of actions, or 999999 if actions include illegal moves
        """
        if actions is None: 
            return 999999
        x, y = self.getStartState()
        cost = 0
        for action in actions:
            # Check figure out the next state and see whether its' legal
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]: 
                return 999999
            cost += self.costFn((x,y))
        return cost

        
class StayEastSearchAgent(SearchAgent):
    """An agent that prefers positions on the East side of the board.
    
    This agent uses uniform cost search with a cost function that penalizes 
    positions on the West side of the board by making them more expensive.
    
    Attributes:
        searchFunction (Callable): Set to uniform cost search algorithm
        searchType (Callable): Factory function that creates position search problem
            with custom cost function
    """
    def __init__(self) -> None:
        """Initialize the StayEastSearchAgent with custom cost function."""
        self.searchFunction = search.uniformCostSearch
        costFn = lambda pos: 0.5 ** pos[0]  # Cost decreases exponentially going East
        self.searchType = lambda state: PositionSearchProblem(
            state, costFn, goal=(1, 1), warn=False, visualize=False)

class StayWestSearchAgent(SearchAgent):
    """An agent that prefers positions on the West side of the board.
    
    This agent uses uniform cost search with a cost function that penalizes 
    positions on the East side of the board by making them more expensive.
    
    Attributes:
        searchFunction (Callable): Set to uniform cost search algorithm
        searchType (Callable): Factory function that creates position search problem
            with custom cost function
    """
    def __init__(self) -> None:
        """Initialize the StayWestSearchAgent with custom cost function."""
        self.searchFunction = search.uniformCostSearch
        costFn = lambda pos: 2 ** pos[0]  # Cost increases exponentially going East
        self.searchType = lambda state: PositionSearchProblem(
            state, costFn, warn=False, visualize=False)

def manhattanHeuristic(position: Tuple[int, int], problem: 'PositionSearchProblem', 
                       info: Dict = {}) -> float:
    """Calculate the Manhattan distance heuristic for a PositionSearchProblem.
    
    Args:
        position: Current (x,y) position
        problem: PositionSearchProblem instance containing goal state
        info: Optional dictionary for caching information
        
    Returns:
        float: Manhattan distance from current position to goal
    """
    return sum(abs(v1-v2) for v1,v2 in zip(position, problem.goal))

def euclideanHeuristic(position: Tuple[int, int], problem: 'PositionSearchProblem',
                      info: Dict = {}) -> float:
    """Calculate the Euclidean distance heuristic for a PositionSearchProblem.
    
    Args:
        position: Current (x,y) position
        problem: PositionSearchProblem instance containing goal state
        info: Optional dictionary for caching information
        
    Returns:
        float: Euclidean distance from current position to goal
    """
    return dist(position, problem.goal)

###############################################################################
#                                                                             #
#                     THIS SECTION NEEDS TO BE COMPLETED                      #
#                          TIME TO WRITE YOUR CODE!                           #
#                                                                             #
###############################################################################

class CornersProblem(search.SearchProblem):
    """A search problem that finds paths through all four corners of a layout.
    
    This search problem requires finding a path that visits all four corners of the maze.
    The state space consists of Pacman's position and the list of corners visited so far.
    
    Attributes:
        walls: Grid of maze walls
        startingPosition: Initial (x,y) position of Pacman
        corners: Tuple of (x,y) coordinates of the four corners
        _expanded: Number of search nodes expanded
        sGS: Starting game state
    """

    def __init__(self, startingGameState: 'GameState') -> None:
        """Initialize the corners problem with walls, starting position and corners.
        
        Args:
            startingGameState: Initial game state containing maze layout
        """
        self.walls = startingGameState.getWalls()
        self.startingPosition = startingGameState.getPacmanPosition()
        top, right = self.walls.height-2, self.walls.width-2 
        self.corners = ((1,1), (1,top), (right, 1), (right, top))
        for corner in self.corners:
            if not startingGameState.hasFood(*corner):
                print(f'Warning: no food in corner {corner}')
        self._expanded = 0 # DO NOT CHANGE; Number of search nodes expanded
        
        "*** YOUR CODE HERE ***"

    def getStartState(self) -> Tuple[Tuple[int, int], List[Tuple[int, int]]]:
        """Get the initial search state.
        
        Returns:
            Tuple containing:
                - Current position as (x,y) coordinates
                - Empty list of visited corners
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

    def isGoalState(self, state: Tuple[Tuple[int, int], List[Tuple[int, int]]]) -> bool:
        """Check if current state is a goal state.
        
        A goal state is reached when all four corners have been visited.
        
        Args:
            state: Current state containing position and visited corners
            
        Returns:
            bool: True if all corners visited, False otherwise
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

    def getSuccessors(self, state: Tuple[Tuple[int, int], List[Tuple[int, int]]]) -> List[Tuple[Tuple[Tuple[int, int], List[Tuple[int, int]]], str, int]]:
        """Get successor states and their associated actions and costs.
        
        Args:
            state: Current state containing position and visited corners
            
        Returns:
            List of tuples, each containing:
                - Successor state (position and updated visited corners)
                - Action required to reach successor
                - Step cost (always 1)

            # Add a successor state to the successor list if the action is legal
            # Here's a code snippet for figuring out whether a new position hits a wall:
            #   x,y = currentPosition
            #   dx, dy = Actions.directionToVector(action)
            #   nextx, nexty = int(x + dx), int(y + dy)
            #   hitsWall = self.walls[nextx][nexty]

        """
        "*** YOUR CODE HERE ***"

        self._expanded += 1 # DO NOT CHANGE
        return successors

    def getCostOfActions(self, actions: Optional[List[str]]) -> int:
        """Calculate total cost of a sequence of actions.
        
        Args:
            actions: List of actions to take
            
        Returns:
            int: Total cost (999999 if illegal move, otherwise length of path)
        """
        if actions == None: return 999999
        x,y = self.startingPosition
        for action in actions:
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]: return 999999
        return len(actions)


def cornersHeuristic(state: Tuple[Tuple[int, int], List[Tuple[int, int]]], 
                     problem: 'CornersProblem') -> float:
    """Calculate an admissible heuristic for the CornersProblem.
    
    This heuristic estimates the minimum distance needed to visit all unvisited corners
    from the current position by iteratively finding the nearest unvisited corner.
    
    Args:
        state: Current search state containing:
            - Position as (x,y) tuple
            - List of visited corner coordinates
        problem: The CornersProblem instance for this layout
            
    Returns:
        float: A lower bound on the shortest path distance to visit all remaining corners
    """
    corners = problem.corners # These are the corner coordinates
    walls = problem.walls # These are the walls of the maze, as a Grid (game.py)
    
    "*** YOUR CODE HERE ***"
        
    return 0 # Default to trivial solution


class AStarCornersAgent(SearchAgent):
    """A SearchAgent that uses A* search with the corners heuristic.
    
    This agent specializes SearchAgent to use A* search with the cornersHeuristic
    to find paths to visit all corner dots in a Pacman game.
    
    Attributes:
        searchFunction (Callable): A* search with corners heuristic
        searchType (Any): CornersProblem search problem type
    """
    def __init__(self) -> None:
        """Initialize the A* corners search agent."""
        self.searchFunction = lambda prob: search.aStarSearch(prob, cornersHeuristic)
        self.searchType = CornersProblem

class FoodSearchProblem:
    """A search problem for finding paths to collect all food dots in Pacman.
    
    A search state in this problem consists of:
        - Pacman's position as (x,y) coordinates
        - A food grid indicating remaining food dots
        
    Attributes:
        start (Tuple[Tuple[int, int], Grid]): Initial state with Pacman position and food grid
        walls (Grid): Grid indicating wall locations
        startingGameState (GameState): Initial game state
        _expanded (int): Number of search nodes expanded
        heuristicInfo (Dict): Storage for heuristic computations
    """
    def __init__(self, startingGameState: 'GameState') -> None:
        """Initialize the food search problem.
        
        Args:
            startingGameState: Initial game state containing maze layout and food
        """
        self.start = (startingGameState.getPacmanPosition(), startingGameState.getFood())
        self.walls = startingGameState.getWalls()
        self.startingGameState = startingGameState
        self._expanded = 0 # DO NOT CHANGE
        self.heuristicInfo = {} # Storage for heuristic computations

    def getStartState(self) -> Tuple[Tuple[int, int], 'Grid']:
        """Get the initial search state.
        
        Returns:
            Tuple containing Pacman's starting position and initial food grid
        """
        return self.start

    def isGoalState(self, state: Tuple[Tuple[int, int], 'Grid']) -> bool:
        """Check if current state is a goal state.
        
        A goal state is reached when all food has been collected.
        
        Args:
            state: Current state with position and food grid
            
        Returns:
            bool: True if no food remains, False otherwise
        """
        return state[1].count() == 0

    def getSuccessors(self, state: Tuple[Tuple[int, int], 'Grid']) -> List[Tuple[Tuple[Tuple[int, int], 'Grid'], str, int]]:
        """Get successor states and actions from current state.
        
        Args:
            state: Current state with position and food grid
            
        Returns:
            List of tuples, each containing:
                - Successor state (position and updated food grid)
                - Action required to reach successor
                - Cost of action (always 1)
        """
        successors = []
        self._expanded += 1 # DO NOT CHANGE
        for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x,y = state[0]
            dx, dy = Actions.directionToVector(direction)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextFood = state[1].copy()
                nextFood[nextx][nexty] = False
                successors.append( ( ((nextx, nexty), nextFood), direction, 1) )
        return successors

    def getCostOfActions(self, actions: List[str]) -> int:
        """Calculate total cost of a sequence of actions.
        
        Args:
            actions: List of actions to evaluate
            
        Returns:
            int: Total cost (999999 if sequence includes illegal moves)
        """
        x,y = self.getStartState()[0]
        cost = 0
        for action in actions:
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]:
                return 999999
            cost += 1
        return cost

class AStarFoodSearchAgent(SearchAgent):
    """A SearchAgent that uses A* search with foodHeuristic for FoodSearchProblem.
    
    This agent uses A* search algorithm with a custom food heuristic to find optimal
    paths for collecting all food pellets in the maze.
    
    Attributes:
        searchFunction (Callable): Set to A* search with foodHeuristic
        searchType (Type): Set to FoodSearchProblem
    """
    def __init__(self) -> None:
        """Initialize the A* food search agent with custom heuristic."""
        self.searchFunction = lambda prob: search.aStarSearch(prob, foodHeuristic)
        self.searchType = FoodSearchProblem

def foodHeuristic(state: Tuple[Tuple[int, int], 'Grid'], problem: 'FoodSearchProblem') -> float:
    """Calculate an admissible heuristic for the FoodSearchProblem.
    
    This heuristic estimates the minimum distance needed to collect all remaining food
    by finding the food pellet at the greatest depth from the current position using BFS.
    
    Args:
        state: Current search state containing:
            - Position as (x,y) tuple
            - Grid of food locations (True = food present)
        problem: The FoodSearchProblem instance for this layout
            
    Returns:
        float: A lower bound on the shortest path distance to collect all food
        
    Note:
        The heuristic must be consistent to ensure correctness. An admissible 
        heuristic will typically also be consistent. If A* finds a solution worse
        than UCS, the heuristic is not consistent/admissible.
        
        The problem.heuristicInfo dict can be used to cache values between calls.
    """
    position, food_grid = state
    
    "*** YOUR CODE HERE ***"                                                                         
    return 0


class ClosestDotSearchAgent(SearchAgent):
    """Search for all food using a sequence of searches.
    
    This agent finds paths to collect all food pellets by repeatedly finding
    paths to the closest remaining food dot.
    
    Attributes:
        actions (List[str]): Sequence of actions to collect all food
        actionIndex (int): Current position in action sequence
    """
    def registerInitialState(self, state: 'GameState') -> None:
        """Find complete path to collect all food when first seeing game board.
        
        This method repeatedly finds paths to the closest remaining food dot
        until all food is collected.
        
        Args:
            state: Initial game state
            
        Raises:
            Exception: If findPathToClosestDot returns an illegal move
        """
        self.actions = []
        currentState = state
        while(currentState.getFood().count() > 0):
            nextPathSegment = self.findPathToClosestDot(currentState)
            self.actions += nextPathSegment
            for action in nextPathSegment:
                legal = currentState.getLegalActions()
                if action not in legal:
                    t = (str(action), str(currentState))
                    raise Exception(f'findPathToClosestDot returned an illegal move: {t}')
                currentState = currentState.generateSuccessor(0, action)
        self.actionIndex = 0
        print(f'Path found with cost {len(self.actions)}')

    def findPathToClosestDot(self, gameState: 'GameState') -> List[str]:
        """Find a path to the closest food dot from the current state.
        
        Uses uniform cost search to find shortest path to nearest food pellet.
        
        Args:
            gameState: Current game state
            
        Returns:
            List[str]: Sequence of actions to reach closest food dot
        """
        # Get useful elements from the game state
        startPosition = gameState.getPacmanPosition()
        food = gameState.getFood()
        walls = gameState.getWalls()
        problem = AnyFoodSearchProblem(gameState)
        
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()


class AnyFoodSearchProblem(PositionSearchProblem):
    """A search problem for finding a path to any food dot.
    
    This search problem extends PositionSearchProblem but modifies the goal test
    to consider any food dot as a valid goal state. The state space and successor
    function remain unchanged from PositionSearchProblem.
    
    Attributes:
        food: Grid of boolean values indicating food locations
        walls: Grid of boolean values indicating wall locations  
        startState: Initial (x,y) position of Pacman
        costFn: Function that returns cost of moving to a position
        _visited: Dictionary tracking visited states
        _visitedlist: List of visited states
        _expanded: Number of search nodes expanded
    """

    def __init__(self, gameState: 'GameState') -> None:
        """Initialize search problem with game state information.
        
        Args:
            gameState: Current game state containing maze layout and food
        """
        # Store the food grid for goal testing
        self.food = gameState.getFood()

        # Initialize PositionSearchProblem attributes
        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition()
        self.costFn = lambda x: 1
        self._visited, self._visitedlist, self._expanded = {}, [], 0 # DO NOT CHANGE

    def isGoalState(self, state: Tuple[int, int]) -> bool:
        """Check if current state contains a food dot.
        
        Args:
            state: Current (x,y) position
            
        Returns:
            bool: True if position contains food, False otherwise
        """
        x, y = state
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()


def mazeDistance(point1: Tuple[int, int], point2: Tuple[int, int], 
                 gameState: 'GameState') -> int:
    """Calculate the shortest path distance between two points in the maze.
    
    Uses breadth-first search to find the shortest path between points through
    the maze, ignoring Pacman's current position in the game state.
    
    Args:
        point1: Starting (x,y) coordinates
        point2: Goal (x,y) coordinates  
        gameState: GameState object containing maze layout
        
    Returns:
        int: Length of shortest path between points
        
    Raises:
        AssertionError: If either point1 or point2 is located on a wall
        
    Example:
        >>> mazeDistance((2,4), (5,6), gameState)
        8
    """
    x1, y1 = point1
    x2, y2 = point2
    walls = gameState.getWalls()
    assert not walls[x1][y1], f'point1 is a wall: {point1}'
    assert not walls[x2][y2], f'point2 is a wall: {point2}'
    prob = PositionSearchProblem(gameState, start=point1, goal=point2, warn=False, visualize=False)
    return len(search.bfs(prob))
