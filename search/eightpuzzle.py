"""Eight Puzzle game implementation and search problem.

This module provides classes for representing and solving the Eight Puzzle game,
where tiles numbered 1-8 must be arranged in order by sliding them into an empty space.

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
    - Added comprehensive docstrings
    - Added type hints throughout
    - Improved code organization
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


import search
import random
from typing import List, Tuple, Optional

class EightPuzzleState:
    """
    The Eight Puzzle is described in the course textbook on
    page 64.

    This class defines the mechanics of the puzzle itself. The
    task of recasting this puzzle as a search problem is left to
    the EightPuzzleSearchProblem class.

    Attributes:
        cells (List[List[int]]): 2D list representing the puzzle grid
        blankLocation (Tuple[int, int]): Row,col coordinates of blank space
    """

    def __init__(self, numbers: List[int]) -> None:
        """
        Constructs a new eight puzzle from an ordering of numbers.

        Args:
            numbers: A list of integers from 0 to 8 representing an
                instance of the eight puzzle. 0 represents the blank
                space. For example, [1, 0, 2, 3, 4, 5, 6, 7, 8]
                represents:
                -------------
                | 1 |   | 2 |
                -------------
                | 3 | 4 | 5 |
                -------------
                | 6 | 7 | 8 |
                ------------

        The configuration of the puzzle is stored in a 2-dimensional
        list (a list of lists) 'cells'.
        """
        self.cells: List[List[int]] = []
        numbers = numbers[:]  # Make a copy so as not to cause side-effects.
        numbers.reverse()
        for row in range(3):
            self.cells.append([])
            for col in range(3):
                self.cells[row].append(numbers.pop())
                if self.cells[row][col] == 0:
                    self.blankLocation = (row, col)

    def isGoal(self) -> bool:
        """
        Checks if the puzzle is in its goal state.

        The goal state is:
            -------------
            |   | 1 | 2 |
            -------------
            | 3 | 4 | 5 |
            -------------
            | 6 | 7 | 8 |
            -------------

        Returns:
            bool: True if puzzle is in goal state, False otherwise

        Examples:
            >>> EightPuzzleState([0, 1, 2, 3, 4, 5, 6, 7, 8]).isGoal()
            True
            >>> EightPuzzleState([1, 0, 2, 3, 4, 5, 6, 7, 8]).isGoal()
            False
        """
        current = 0
        for row in range(3):
            for col in range(3):
                if current != self.cells[row][col]:
                    return False
                current += 1
        return True

    def legalMoves(self) -> List[str]:
        """
        Returns a list of legal moves from the current state.

        Moves consist of moving the blank space up, down, left or right.
        These are encoded as 'up', 'down', 'left' and 'right' respectively.

        Returns:
            List[str]: List of legal move strings

        Example:
            >>> EightPuzzleState([0, 1, 2, 3, 4, 5, 6, 7, 8]).legalMoves()
            ['down', 'right']
        """
        moves = []
        row, col = self.blankLocation
        if row != 0:
            moves.append('up')
        if row != 2:
            moves.append('down')
        if col != 0:
            moves.append('left')
        if col != 2:
            moves.append('right')
        return moves

    def result(self, move: str) -> 'EightPuzzleState':
        """
        Returns a new EightPuzzleState with the current state and blankLocation
        updated based on the provided move.

        Args:
            move: String representing the move ('up', 'down', 'left', 'right')

        Returns:
            EightPuzzleState: New puzzle state after applying the move

        Raises:
            ValueError: If move is invalid

        Note:
            This function does not modify the current object. Instead,
            it returns a new object.
        """
        row, col = self.blankLocation
        if move == 'up':
            newrow = row - 1
            newcol = col
        elif move == 'down':
            newrow = row + 1
            newcol = col
        elif move == 'left':
            newrow = row
            newcol = col - 1
        elif move == 'right':
            newrow = row
            newcol = col + 1
        else:
            raise ValueError("Illegal Move")

        # Create a copy of the current eightPuzzle
        newPuzzle = EightPuzzleState([0, 0, 0, 0, 0, 0, 0, 0, 0])
        newPuzzle.cells = [values[:] for values in self.cells]
        # And update it to reflect the move
        newPuzzle.cells[row][col] = self.cells[newrow][newcol]
        newPuzzle.cells[newrow][newcol] = self.cells[row][col]
        newPuzzle.blankLocation = (newrow, newcol)

        return newPuzzle

    # Utilities for comparison and display
    def __eq__(self, other: object) -> bool:
        """
        Overloads '==' such that two eightPuzzles with the same configuration
        are equal.

        Args:
            other: Another EightPuzzleState to compare with

        Returns:
            bool: True if puzzles have identical configurations

        Example:
            >>> EightPuzzleState([0, 1, 2, 3, 4, 5, 6, 7, 8]) == \
                EightPuzzleState([1, 0, 2, 3, 4, 5, 6, 7, 8]).result('left')
            True
        """
        if not isinstance(other, EightPuzzleState):
            return False
        for row in range(3):
            if self.cells[row] != other.cells[row]:
                return False
        return True

    def __hash__(self) -> int:
        """Returns hash of the puzzle state."""
        return hash(str(self.cells))

    def __getAsciiString(self) -> str:
        """
        Returns a display string for the maze.

        Returns:
            str: ASCII representation of puzzle
        """
        lines = []
        horizontalLine = ('-' * 13)
        lines.append(horizontalLine)
        for row in self.cells:
            rowLine = '|'
            for col in row:
                if col == 0:
                    col = ' '
                rowLine = f'{rowLine} {col} |'
            lines.append(rowLine)
            lines.append(horizontalLine)
        return '\n'.join(lines)

    def __str__(self) -> str:
        """Returns string representation of the puzzle."""
        return self.__getAsciiString()

# TODO: Implement The methods in this class

class EightPuzzleSearchProblem(search.SearchProblem):
    """
    Implementation of a SearchProblem for the Eight Puzzle domain.

    Each state is represented by an instance of an eightPuzzle.
    """
    def __init__(self, puzzle: EightPuzzleState) -> None:
        """
        Creates a new EightPuzzleSearchProblem which stores search information.

        Args:
            puzzle: Initial puzzle state
        """
        self.puzzle = puzzle

    def getStartState(self) -> EightPuzzleState:
        """Returns the initial puzzle state."""
        return self.puzzle

    def isGoalState(self, state: EightPuzzleState) -> bool:
        """
        Checks if given state is the goal state.

        Args:
            state: Puzzle state to check

        Returns:
            bool: True if state is goal state
        """
        return state.isGoal()

    def getSuccessors(self, state: EightPuzzleState) -> List[Tuple[EightPuzzleState, str, float]]:
        """
        Returns list of (successor, action, stepCost) pairs where
        each successor is either left, right, up, or down
        from the original state and the cost is 1.0 for each.

        Args:
            state: Current puzzle state

        Returns:
            List of (successor state, action, cost) tuples
        """
        succ = []
        for a in state.legalMoves():
            succ.append((state.result(a), a, 1))
        return succ

    def getCostOfActions(self, actions: List[str]) -> float:
        """
        Calculate total cost of a sequence of actions.

        Args:
            actions: A list of actions to take

        Returns:
            float: Total cost of sequence (equal to number of moves)

        Note: The sequence must be composed of legal moves
        """
        return len(actions)

EIGHT_PUZZLE_DATA = [[1, 0, 2, 3, 4, 5, 6, 7, 8],
                     [1, 7, 8, 2, 3, 4, 5, 6, 0],
                     [4, 3, 2, 7, 0, 5, 1, 6, 8],
                     [5, 1, 3, 4, 0, 2, 6, 7, 8],
                     [1, 2, 5, 7, 6, 8, 0, 4, 3],
                     [0, 3, 1, 6, 8, 2, 7, 5, 4]]

def loadEightPuzzle(puzzleNumber: int) -> EightPuzzleState:
    """
    Load one of the predefined eight puzzles.

    Args:
        puzzleNumber: The number of the eight puzzle to load (0-5)

    Returns:
        EightPuzzleState: Puzzle object generated from EIGHT_PUZZLE_DATA

    Example:
        >>> print(loadEightPuzzle(0))
        -------------
        | 1 |   | 2 |
        -------------
        | 3 | 4 | 5 |
        -------------
        | 6 | 7 | 8 |
        -------------
    """
    return EightPuzzleState(EIGHT_PUZZLE_DATA[puzzleNumber])

def createRandomEightPuzzle(moves: int = 100) -> EightPuzzleState:
    """
    Creates a random eight puzzle by applying random moves to solved puzzle.

    Args:
        moves: Number of random moves to apply (default: 100)

    Returns:
        EightPuzzleState: Randomly generated puzzle state
    """
    puzzle = EightPuzzleState([0,1,2,3,4,5,6,7,8])
    for i in range(moves):
        # Execute a random legal move
        puzzle = puzzle.result(random.sample(puzzle.legalMoves(), 1)[0])
    return puzzle

def main():
    puzzle = createRandomEightPuzzle(25)
    print('A random puzzle:')
    print(puzzle)

    problem = EightPuzzleSearchProblem(puzzle)
    path = search.breadthFirstSearch(problem)
    print(f'BFS found a path of {len(path)} moves: {path}')
    curr = puzzle
    i = 1
    for a in path:
        curr = curr.result(a)
        print(f'After {i} move{"s" if i>1 else ""}: {a}')
        print(curr)

        input("Press return for the next state...")   # wait for key stroke
        i += 1

if __name__ == '__main__':
    main()
