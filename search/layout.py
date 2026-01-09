"""Layout management for Pacman game board.

This module handles the static layout information for the Pacman game board,
including walls, food pellets, power capsules, and agent starting positions.
It provides functionality to load and process layout files that define the
game maze structure.

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
    - Added type hints throughout
    - Improved docstrings and documentation
    - Reorganized imports
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


from typing import List, Tuple, Set, Dict, Optional
from util import manhattanDistance
from game import Grid, Directions
import os
import random
from functools import reduce

VISIBILITY_MATRIX_CACHE: Dict[str, Grid] = {}

class Layout:
    """
    A Layout manages the static information about the game board.
    
    Attributes:
        width (int): Width of the board in grid cells
        height (int): Height of the board in grid cells
        walls (Grid): Grid marking wall locations
        food (Grid): Grid marking food pellet locations  
        capsules (List[Tuple[int, int]]): List of power capsule coordinates
        agentPositions (List[Tuple[bool, Tuple[int, int]]]): List of (isPacman, position) tuples
        numGhosts (int): Number of ghosts in the layout
        layoutText (List[str]): Original text representation of layout
        totalFood (int): Total number of food pellets
        visibility (Grid): Visibility information for each position (optional)
    """

    def __init__(self, layoutText: List[str]) -> None:
        """
        Initialize a new layout from text representation.
        
        Args:
            layoutText: List of strings representing the maze layout
        """
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

    def getNumGhosts(self) -> int:
        """Return the number of ghosts in the layout."""
        return self.numGhosts

    def initializeVisibilityMatrix(self) -> None:
        """
        Initialize the visibility matrix for the layout.
        This computes what positions are visible from each position in the maze.
        Results are cached globally to avoid recomputation.
        """
        global VISIBILITY_MATRIX_CACHE
        layout_key = reduce(str.__add__, self.layoutText)
        
        if layout_key not in VISIBILITY_MATRIX_CACHE:
            vecs = [(-0.5,0), (0.5,0), (0,-0.5), (0,0.5)]
            dirs = [Directions.NORTH, Directions.SOUTH, Directions.WEST, Directions.EAST]
            vis = Grid(self.width, self.height, {Directions.NORTH:set(), Directions.SOUTH:set(), 
                                               Directions.EAST:set(), Directions.WEST:set(), 
                                               Directions.STOP:set()})
            
            for x in range(self.width):
                for y in range(self.height):
                    if not self.walls[x][y]:
                        for vec, direction in zip(vecs, dirs):
                            dx, dy = vec
                            nextx, nexty = x + dx, y + dy
                            while (nextx + nexty) != int(nextx) + int(nexty) or not self.walls[int(nextx)][int(nexty)]:
                                vis[x][y][direction].add((nextx, nexty))
                                nextx, nexty = x + dx, y + dy
            self.visibility = vis
            VISIBILITY_MATRIX_CACHE[layout_key] = vis
        else:
            self.visibility = VISIBILITY_MATRIX_CACHE[layout_key]

    def isWall(self, pos: Tuple[int, int]) -> bool:
        """
        Check if given position contains a wall.
        
        Args:
            pos: (x,y) position to check
            
        Returns:
            True if position contains a wall, False otherwise
        """
        x, col = pos
        return self.walls[x][col]

    def getRandomLegalPosition(self) -> Tuple[int, int]:
        """Return a random non-wall position in the layout."""
        x = random.choice(range(self.width))
        y = random.choice(range(self.height))
        while self.isWall((x, y)):
            x = random.choice(range(self.width))
            y = random.choice(range(self.height))
        return (x,y)

    def getRandomCorner(self) -> Tuple[int, int]:
        """Return a random corner position from the layout."""
        poses = [(1,1), (1, self.height - 2), (self.width - 2, 1), (self.width - 2, self.height - 2)]
        return random.choice(poses)

    def getFurthestCorner(self, pacPos: Tuple[int, int]) -> Tuple[int, int]:
        """
        Get the corner furthest from Pacman's position.
        
        Args:
            pacPos: Current position of Pacman
            
        Returns:
            Position of furthest corner
        """
        poses = [(1,1), (1, self.height - 2), (self.width - 2, 1), (self.width - 2, self.height - 2)]
        dist, pos = max([(manhattanDistance(p, pacPos), p) for p in poses])
        return pos

    def isVisibleFrom(self, ghostPos: Tuple[float, float], pacPos: Tuple[float, float], 
                      pacDirection: str) -> bool:
        """
        Check if a ghost is visible from Pacman's position and direction.
        
        Args:
            ghostPos: Position of ghost
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
        """Return a new copy of the layout."""
        return Layout(self.layoutText[:])

    def processLayoutText(self, layoutText: List[str]) -> None:
        """
        Process the layout text to initialize the game state.
        
        Coordinates are flipped from the input format to the (x,y) convention here.
        The shape of the maze uses these characters:
         % - Wall
         . - Food
         o - Capsule
         G - Ghost
         P - Pacman
         1-4 - Ghost numbers
        Other characters are ignored.
        
        Args:
            layoutText: List of strings representing maze layout
        """
        maxY = self.height - 1
        for y in range(self.height):
            for x in range(self.width):
                layoutChar = layoutText[maxY - y][x]
                self.processLayoutChar(x, y, layoutChar)
        self.agentPositions.sort()
        self.agentPositions = [(i == 0, pos) for i, pos in self.agentPositions]

    def processLayoutChar(self, x: int, y: int, layoutChar: str) -> None:
        """
        Process a single character from the layout text.
        
        Args:
            x: X coordinate
            y: Y coordinate 
            layoutChar: Character from layout text
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
            self.agentPositions.append((int(layoutChar), (x,y)))
            self.numGhosts += 1

def getLayout(name: str, back: int = 2) -> Optional[Layout]:
    """
    Load a layout from a file.
    
    Args:
        name: Name of layout file
        back: Number of directory levels to search back
        
    Returns:
        Layout object if found, None otherwise
    """
    if name.endswith('.lay'):
        layout = tryToLoad(f'layouts/{name}')
        if layout is None: 
            layout = tryToLoad(name)
    else:
        layout = tryToLoad(f'layouts/{name}.lay')
        if layout is None:
            layout = tryToLoad(f'{name}.lay')
    if layout is None and back >= 0:
        curdir = os.path.abspath('.')
        os.chdir('..')
        layout = getLayout(name, back - 1)
        os.chdir(curdir)
    return layout

def tryToLoad(fullname: str) -> Optional[Layout]:
    """
    Try to load a layout from a file.
    
    Args:
        fullname: Full path to layout file
        
    Returns:
        Layout object if file exists and is valid, None otherwise
    """
    if not os.path.exists(fullname):
        return None
    with open(fullname) as f:
        return Layout([line.strip() for line in f])
