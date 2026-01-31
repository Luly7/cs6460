"""Search algorithms for the Pacman AI project.

This module implements generic search algorithms that are used by Pacman agents
to find paths through the maze. The algorithms include depth-first search,
breadth-first search, uniform cost search, and A* search.

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
    - Made SearchProblem a Python ABC using abc module
    - Improved docstrings and documentation
    - Verified to run with Python 3.13

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

# pylint: disable=invalid-name

"""
================================================================================
                               SEARCH ALGORITHMS
================================================================================

In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).

Please implement the requested search algorithms below. The search algorithms will
be used by the Pacman agents to find paths through the maze.
================================================================================
"""
from typing import List, Tuple, Any, Optional, Dict, Callable
from util import Stack, Queue, PriorityQueue, Counter
import util
import abc
from game import Directions


class SearchProblem(metaclass=abc.ABCMeta):
    """Abstract base class defining the interface for search problems.

    This class outlines the required methods that any search problem must implement,
    but does not provide implementations (an abstract base class).

    All search problems must implement methods for:
    - Getting the initial state
    - Checking if a state is a goal
    - Getting successor states and actions
    - Calculating cost of action sequences
    """

    @abc.abstractmethod
    def getStartState(self) -> Any:
        """Get the initial state for the search problem.

        Returns:
            Any: The start state in the problem's state space
        """
        return

    @abc.abstractmethod
    def isGoalState(self, state: Any) -> bool:
        """Check if a state is a valid goal state.

        Args:
            state: Current state in the search

        Returns:
            bool: True if state is a goal state, False otherwise
        """
        return

    @abc.abstractmethod
    def getSuccessors(self, state: Any) -> List[Tuple[Any, str, float]]:
        """Get successor states and their associated actions and costs.

        Args:
            state: Current state in the search

        Returns:
            List of tuples, each containing:
                - successor: A successor state
                - action: Action required to reach successor
                - stepCost: Cost of taking the action
        """
        return

    @abc.abstractmethod
    def getCostOfActions(self, actions: List[str]) -> float:
        """Calculate total cost of a sequence of actions.

        Args:
            actions: List of actions to take

        Returns:
            float: Total cost of the action sequence

        Note:
            The sequence must be composed of legal moves.
        """
        return


def tinyMazeSearch(problem: 'SearchProblem') -> List[str]:
    """Return a fixed sequence of moves that solves tinyMaze.

    This function returns a hardcoded solution that only works for the tinyMaze layout.
    For any other maze, the sequence of moves will be incorrect.

    Args:
        problem: A SearchProblem instance representing the maze to solve

    Returns:
        List[str]: A sequence of direction strings (SOUTH, WEST) that solve tinyMaze
    """
    s = Directions.SOUTH
    w = Directions.WEST
    return [s, s, w, s, w, w, s, w]


def depthFirstSearch(problem: 'SearchProblem') -> List[str]:
    """Search the deepest nodes in the search tree first using DFS.

    Implements a graph search version of depth-first search that avoids
    expanding previously visited states.

    Args:
        problem: A SearchProblem instance defining the search space

    Returns:
        List[str]: A sequence of actions that reaches the goal state,
                  or empty list if no solution exists

    Example:
        To understand the search problem:
        >>> print(f"Start: {problem.getStartState()}")
        >>> print(f"Is start a goal? {problem.isGoalState(problem.getStartState())}")
        >>> print(f"Start's successors: {problem.getSuccessors(problem.getStartState())}")
    """
# =================DFS STARTS HERE =======================
# DFS acts like a LIFO stack of paths.  DFS uses a stack so it goes deep before exploring others
    expansion_order = Stack()
    expansion_order.push((problem.getStartState(), []))
    visited = set()  # Track visited states

    while not expansion_order.isEmpty():
        state, path = expansion_order.pop()  # Pop the next state
        if state in visited:  # Skip if already visited
            continue
        visited.add(state)  # Mark the state as visited
        if problem.isGoalState(state):  # Check if this is the goal
            return path
        # Expands successors
        for successor, action, cost in problem.getSuccessors(state):
            if successor not in visited:
                expansion_order.push((successor, path + [action]))
    return []
# ================ DFS ends here ===================


def breadthFirstSearch(problem: 'SearchProblem') -> List[str]:
    """Search the shallowest nodes in the search tree first using BFS.

    Implements a graph search version of breadth-first search that avoids
    expanding previously visited states.

    Args:
        problem: A SearchProblem instance defining the search space

    Returns:
        List[str]: A sequence of actions that reaches the goal state,
                  or empty list if no solution exists
    """
# ================= BFS STARTS HERE =========================
    # BFS is a FIFO data structure
    expansion_order = Queue()
    expansion_order.push((problem.getStartState(), []))
    visited = set()
    visited.add(problem.getStartState())

    while not expansion_order.isEmpty():
        state, path = expansion_order.pop()
        if problem.isGoalState(state):
            return path
        for successor, action, cost in problem.getSuccessors(state):
            if successor not in visited:
                visited.add(successor)
                expansion_order.push((successor, path + [action]))
    return []  # No goal reached


# ==============BFS ENDS HERE==========================


def uniformCostSearch(problem: 'SearchProblem') -> List[str]:
    """Search the node of least total cost first using uniform cost search.

Implements a graph search version of uniform cost search that expands nodes
in order of their path cost from the start state.

Args:
    problem: A SearchProblem instance defining the search space

Returns:
    List[str]: A sequence of actions that reaches the goal state with minimum
              total cost, or empty list if no solution exists
"""
# ====================UCS STARTS HERE===============================

    # UCS expands the cheapest node first
    expansion_order = PriorityQueue()
    expansion_order.push((problem.getStartState(), [], 0), 0)
    visited = set()

    while not expansion_order.isEmpty():
        state, path, total_cost = expansion_order.pop()
        if state in visited:
            continue
        visited.add(state)
        if problem.isGoalState(state):
            return path
        for successor, action, step_cost in problem.getSuccessors(state):
            if successor not in visited:
                new_cost = total_cost + step_cost
                new_path = path + [action]
                expansion_order.push((successor, new_path, new_cost), new_cost)
    return []
# ===================UCS ENDS HERE ==========================


def nullHeuristic(state: Any, problem: Optional['SearchProblem'] = None) -> float:
    """Return a trivial heuristic estimate of 0 for any state.

    This heuristic function provides a baseline by always estimating zero cost
    to reach the goal from any state. It is admissible but not very informative.

    Args:
        state: Current state in the search space
        problem: Optional SearchProblem instance defining the search space

    Returns:
        float: Always returns 0 as the heuristic estimate
    """
    return 0


def aStarSearch(problem: 'SearchProblem', heuristic: Callable = nullHeuristic) -> List[str]:
    """Search the node that has the lowest combined cost and heuristic first using A* search.

    Implements A* graph search that expands nodes in order of f(n) = g(n) + h(n), where:
    - g(n) is the actual cost from start to node n
    - h(n) is the heuristic estimate from n to goal

    Args:
        problem: A SearchProblem instance defining the search space
        heuristic: A function that estimates remaining cost to goal (default: nullHeuristic)

    Returns:
        List[str]: A sequence of actions that reaches the goal state with optimal cost,
                  or empty list if no solution exists
    """
   # =================ASTAR STARTS HERE=================

    expansion_order = PriorityQueue()
    start_state = problem.getStartState()
    expansion_order.push((start_state, [], 0), heuristic(start_state, problem))
    visited = set()

    while not expansion_order.isEmpty():
        state, path, g_cost = expansion_order.pop()
        if state in visited:
            continue
        visited.add(state)

        if problem.isGoalState(state):
            return path
        for successor, action, step_cost in problem.getSuccessors(state):
            if successor not in visited:
                new_g_cost = g_cost + step_cost
                new_path = path + [action]
                f_cost = new_g_cost + heuristic(successor, problem)
                expansion_order.push((successor, new_path, new_g_cost), f_cost)
    return []  # No results
# ================ ASTAR ENDS HERE========================
    # Abbreviations - Common search algorithm aliases with type hints
    bfs: Callable[[SearchProblem], List[str]] = breadthFirstSearch
    dfs: Callable[[SearchProblem], List[str]] = depthFirstSearch
    astar: Callable[[SearchProblem, Callable], List[str]] = aStarSearch
    ucs: Callable[[SearchProblem], List[str]] = uniformCostSearch


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
