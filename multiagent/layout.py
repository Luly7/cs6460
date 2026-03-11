"""layout.py - Game Board Layout Management for Pacman
====================================================

This module manages the static layout information for the Pacman game board,
including walls, food pellets, capsules, and agent starting positions.

The module provides functionality to:
- Load and parse maze layouts from text files
- Track positions of walls, food, capsules and agents
- Calculate visibility between board positions
- Support layout queries needed by game logic

Key Classes:
    Layout: Manages the game board layout and provides access methods

Usage:
    This module is used by the Pacman game to load and manage maze layouts.
    Layouts can be loaded from text files or created programmatically.

Author: George Rudolph
Date: 14 Nov 2024
Major Changes:
1. Added type hints throughout for better code clarity and IDE support
2. Improved docstrings with detailed descriptions
3. Enhanced code organization and naming

This code runs on Python 3.13

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


from util import manhattanDistance
from game import Grid, Directions
import os
import random
from functools import reduce
from typing import List, Tuple, Set, Dict, Optional, Union

VISIBILITY_MATRIX_CACHE: Dict[str, Grid] = {}


class Layout:
    """A Layout manages the static information about the game board.
    
    The Layout class stores and processes the maze layout including walls, food,
    capsules, and agent positions. It provides methods to access and manipulate
    this information.
    
    Attributes:
        width (int): Width of the game board
        height (int): Height of the game board
        walls (Grid): Grid marking wall locations
        food (Grid): Grid marking food pellet locations 
        capsules (List[Tuple[int, int]]): List of capsule coordinates
        agentPositions (List[Tuple[bool, Tuple[int, int]]]): List of agent positions
        numGhosts (int): Number of ghosts in the layout
        layoutText (List[str]): Original layout text representation
        totalFood (int): Total number of food pellets
        visibility (Grid): Visibility information for each position (optional)
    """

    def __init__(self, layoutText: List[str]) -> None:
        self.width = len(layoutText[0])
        self.height = len(layoutText)
        self.walls = Grid(self.width, self.height, False)
        self.food = Grid(self.width, self.height, False)
        self.capsules: List[Tuple[int, int]] = []
        self.agentPositions: List[Tuple[bool, Tuple[int, int]]] = []
        self.numGhosts = 0
        self.processLayoutText(layoutText)
        self.layoutText = layoutText
        self.totalFood = len(self.food.asList())
        # self.initializeVisibilityMatrix()

    def getNumGhosts(self) -> int:
        """Return the number of ghosts in the layout."""
        return self.numGhosts

    def initializeVisibilityMatrix(self) -> None:
        """Initialize the visibility matrix for line-of-sight calculations.
        
        Creates a grid storing which positions are visible from each position
        in each direction. Results are cached globally for reuse.
        """
        global VISIBILITY_MATRIX_CACHE
        if reduce(str.__add__, self.layoutText) not in VISIBILITY_MATRIX_CACHE:
            vecs = [(-0.5, 0), (0.5, 0), (0, -0.5), (0, 0.5)]
            dirs = [Directions.NORTH, Directions.SOUTH,
                    Directions.WEST, Directions.EAST]
            vis = Grid(self.width, self.height, {Directions.NORTH: set(), Directions.SOUTH: set(
            ), Directions.EAST: set(), Directions.WEST: set(), Directions.STOP: set()})
            for x in range(self.width):
                for y in range(self.height):
                    if self.walls[x][y] == False:
                        for vec, direction in zip(vecs, dirs):
                            dx, dy = vec
                            nextx, nexty = x + dx, y + dy
                            while (nextx + nexty) != int(nextx) + int(nexty) or not self.walls[int(nextx)][int(nexty)]:
                                vis[x][y][direction].add((nextx, nexty))
                                nextx, nexty = x + dx, y + dy
            self.visibility = vis
            VISIBILITY_MATRIX_CACHE[reduce(str.__add__, self.layoutText)] = vis
        else:
            self.visibility = VISIBILITY_MATRIX_CACHE[reduce(
                str.__add__, self.layoutText)]

    def isWall(self, pos: Tuple[int, int]) -> bool:
        """Return whether the given position contains a wall.
        
        Args:
            pos: (x,y) position to check
            
        Returns:
            True if position contains a wall, False otherwise
        """
        x, col = pos
        return self.walls[x][col]

    def getRandomLegalPosition(self) -> Tuple[int, int]:
        """Return a random non-wall position in the layout."""
        x = random.choice(list(range(self.width)))
        y = random.choice(list(range(self.height)))
        while self.isWall((x, y)):
            x = random.choice(list(range(self.width)))
            y = random.choice(list(range(self.height)))
        return (x, y)

    def getRandomCorner(self) -> Tuple[int, int]:
        """Return a random corner position from the layout."""
        poses = [(1, 1), (1, self.height - 2), (self.width - 2, 1),
                 (self.width - 2, self.height - 2)]
        return random.choice(poses)

    def getFurthestCorner(self, pacPos: Tuple[int, int]) -> Tuple[int, int]:
        """Return the corner furthest from Pacman's position.
        
        Args:
            pacPos: Current position of Pacman
            
        Returns:
            Corner position furthest from pacPos
        """
        poses = [(1, 1), (1, self.height - 2), (self.width - 2, 1),
                 (self.width - 2, self.height - 2)]
        dist, pos = max([(manhattanDistance(p, pacPos), p) for p in poses])
        return pos

    def isVisibleFrom(self, ghostPos: Tuple[float, float], pacPos: Tuple[int, int], pacDirection: str) -> bool:
        """Check if a ghost is visible from Pacman's position and direction.
        
        Args:
            ghostPos: Position of the ghost
            pacPos: Position of Pacman
            pacDirection: Direction Pacman is facing
            
        Returns:
            True if ghost is visible to Pacman, False otherwise
        """
        row, col = [int(x) for x in pacPos]
        return ghostPos in self.visibility[row][col][pacDirection]

    def __str__(self) -> str:
        """Return string representation of layout."""
        return "\n".join(self.layoutText)

    def deepCopy(self) -> 'Layout':
        """Return a new copy of this layout."""
        return Layout(self.layoutText[:])

    def processLayoutText(self, layoutText: List[str]) -> None:
        """Process the layout text to initialize the game state.
        
        Coordinates are flipped from the input format to the (x,y) convention here.
        
        The shape of the maze. Each character represents a different type of object:
         % - Wall
         . - Food
         o - Capsule
         G - Ghost
         P - Pacman
        Other characters are ignored.
        
        Args:
            layoutText: List of strings representing the maze layout
        """
        maxY = self.height - 1
        for y in range(self.height):
            for x in range(self.width):
                layoutChar = layoutText[maxY - y][x]
                self.processLayoutChar(x, y, layoutChar)
        self.agentPositions.sort()
        self.agentPositions = [(i == 0, pos) for i, pos in self.agentPositions]

    def processLayoutChar(self, x: int, y: int, layoutChar: str) -> None:
        """Process a single character from the layout text.
        
        Args:
            x: X coordinate
            y: Y coordinate 
            layoutChar: Character from layout text to process
        """
        if layoutChar == '%':
            self.walls[x][y] = True
        elif layoutChar == '.':
            self.food[x][y] = True
        elif layoutChar == 'o':
            self.capsules.append((x, y))
        elif layoutChar == 'P':
            self.agentPositions.append((0, (x, y)))
        elif layoutChar in ['G']:
            self.agentPositions.append((1, (x, y)))
            self.numGhosts += 1
        elif layoutChar in ['1', '2', '3', '4']:
            self.agentPositions.append((int(layoutChar), (x, y)))
            self.numGhosts += 1


def getLayout(name: str, back: int = 2) -> Optional[Layout]:
    """Retrieve a layout from disk.
    
    Args:
        name: Name of layout to load
        back: Number of parent directories to search
        
    Returns:
        Layout object if found, None otherwise
    """
    if name.endswith('.lay'):
        layout = tryToLoad(f'layouts/{name}')
        if layout == None:
            layout = tryToLoad(name)
    else:
        layout = tryToLoad(f'layouts/{name}.lay')
        if layout == None:
            layout = tryToLoad(f'{name}.lay')
    if layout == None and back >= 0:
        curdir = os.path.abspath('.')
        os.chdir('..')
        layout = getLayout(name, back - 1)
        os.chdir(curdir)
    return layout


def tryToLoad(fullname: str) -> Optional[Layout]:
    """Attempt to load a layout from a file.
    
    Args:
        fullname: Full path to layout file
        
    Returns:
        Layout object if file exists and is valid, None otherwise
    """
    if(not os.path.exists(fullname)):
        return None
    f = open(fullname)
    try:
        return Layout([line.strip() for line in f])
    finally:
        f.close()
