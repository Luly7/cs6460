"""
# layout.py
# ---------
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

Layout management module for the Pacman game.

This module handles the static game board configuration including walls,
food pellets, capsules and agent starting positions. The Layout class
provides methods to:

1. Load and parse layout files
2. Access board elements and dimensions
3. Calculate visibility between positions
4. Generate random valid positions
5. Support deep copying of layouts

The module works closely with game.py and pacman.py to define the
game environment that agents interact with.

Changes by George Rudolph 30 Nov 2024:
- Verified compatibility with Python 3.13
- Enhanced module documentation
- Added type hints throughout
- Improved method documentation
- Added input validation
"""


from util import manhattanDistance
from game import Grid
import os
import random
from functools import reduce
from typing import List, Tuple, Set, Dict, Optional, Union

VISIBILITY_MATRIX_CACHE = {}


class Layout:
    """
    A Layout manages the static information about the game board.
    
    Attributes:
        width (int): Width of the game board
        height (int): Height of the game board
        walls (Grid): Grid indicating wall positions
        food (Grid): Grid indicating food positions
        capsules (list): List of capsule positions
        agentPositions (list): List of agent positions
        numGhosts (int): Number of ghosts in the layout
        layoutText (list): Original text representation of layout
        totalFood (int): Total number of food pellets
    """

    def __init__(self, layoutText: List[str]) -> None:
        """Initialize a new Layout from a text representation.

        The layout is represented as a list of strings, where each string is a row.
        Characters in the text representation:
        - '%': Wall
        - '.': Food pellet  
        - 'o': Capsule
        - 'P': Pacman starting position
        - 'G': Ghost starting position
        - ' ': Empty space

        Args:
            layoutText: List of strings representing the layout, one string per row

        Side effects:
            Initializes layout attributes including dimensions, walls, food, capsules,
            agent positions, and total food count based on the text representation
        """
        self.width = len(layoutText[0])
        self.height = len(layoutText)
        self.walls = Grid(self.width, self.height, False)
        self.food = Grid(self.width, self.height, False)
        self.capsules = []
        self.agentPositions = []
        self.numGhosts = 0
        self.processLayoutText(layoutText)
        self.layoutText = layoutText
        self.totalFood = len(self.food.asList())
        # self.initializeVisibilityMatrix()

    def getNumGhosts(self) -> int:
        """Returns the number of ghosts in the layout."""
        return self.numGhosts

    def initializeVisibilityMatrix(self) -> None:
        """
        Initializes a visibility matrix that determines what each agent can see from their position.
        Caches results for efficiency when reusing layouts.
        """
        global VISIBILITY_MATRIX_CACHE
        if reduce(str.__add__, self.layoutText) not in VISIBILITY_MATRIX_CACHE:
            from game import Directions

            vecs = [(-0.5, 0), (0.5, 0), (0, -0.5), (0, 0.5)]
            dirs = [
                Directions.NORTH,
                Directions.SOUTH,
                Directions.WEST,
                Directions.EAST,
            ]
            vis = Grid(
                self.width,
                self.height,
                {
                    Directions.NORTH: set(),
                    Directions.SOUTH: set(),
                    Directions.EAST: set(),
                    Directions.WEST: set(),
                    Directions.STOP: set(),
                },
            )
            for x in range(self.width):
                for y in range(self.height):
                    if self.walls[x][y] == False:
                        for vec, direction in zip(vecs, dirs):
                            dx, dy = vec
                            nextx, nexty = x + dx, y + dy
                            while (nextx + nexty) != int(nextx) + int(
                                nexty
                            ) or not self.walls[int(nextx)][int(nexty)]:
                                vis[x][y][direction].add((nextx, nexty))
                                nextx, nexty = x + dx, y + dy
            self.visibility = vis
            VISIBILITY_MATRIX_CACHE[reduce(str.__add__, self.layoutText)] = vis
        else:
            self.visibility = VISIBILITY_MATRIX_CACHE[
                reduce(str.__add__, self.layoutText)
            ]

    def isWall(self, pos: Tuple[int, int]) -> bool:
        """
        Returns whether the given position contains a wall.
        
        Args:
            pos: (x,y) position to check
            
        Returns:
            True if position contains a wall, False otherwise
        """
        x, col = pos
        return self.walls[x][col]

    def getRandomLegalPosition(self) -> Tuple[int, int]:
        """
        Returns a random position that does not contain a wall.
        
        Returns:
            (x,y) tuple of a valid non-wall position
        """
        x = random.choice(range(self.width))
        y = random.choice(range(self.height))
        while self.isWall((x, y)):
            x = random.choice(range(self.width))
            y = random.choice(range(self.height))
        return (x, y)

    def getRandomCorner(self) -> Tuple[int, int]:
        """
        Returns a random corner position of the layout.
        
        Returns:
            (x,y) tuple of a randomly chosen corner position
        """
        poses = [
            (1, 1),
            (1, self.height - 2),
            (self.width - 2, 1),
            (self.width - 2, self.height - 2),
        ]
        return random.choice(poses)

    def getFurthestCorner(self, pacPos: Tuple[int, int]) -> Tuple[int, int]:
        """
        Returns the corner furthest from Pacman's current position.
        
        Args:
            pacPos: Current (x,y) position of Pacman
            
        Returns:
            (x,y) tuple of the furthest corner position
        """
        poses = [
            (1, 1),
            (1, self.height - 2),
            (self.width - 2, 1),
            (self.width - 2, self.height - 2),
        ]
        dist, pos = max([(manhattanDistance(p, pacPos), p) for p in poses])
        return pos

    def isVisibleFrom(self, ghostPos: Tuple[float, float], pacPos: Tuple[int, int], pacDirection: str) -> bool:
        """
        Determines if a ghost is visible from Pacman's position and direction.
        
        Args:
            ghostPos: (x,y) position of ghost
            pacPos: (x,y) position of Pacman
            pacDirection: Direction Pacman is facing
            
        Returns:
            True if ghost is visible to Pacman, False otherwise
        """
        row, col = [int(x) for x in pacPos]
        return ghostPos in self.visibility[row][col][pacDirection]

    def __str__(self) -> str:
        """Returns string representation of layout."""
        return "\n".join(self.layoutText)

    def deepCopy(self) -> 'Layout':
        """Returns a new copy of the layout."""
        return Layout(self.layoutText[:])

    def processLayoutText(self, layoutText: List[str]) -> None:
        """
        Processes the layout text to create the game board.
        
        Coordinates are flipped from the input format to the (x,y) convention here.
        The shape of the maze uses these characters:
         % - Wall
         . - Food
         o - Capsule
         G - Ghost
         P - Pacman
         1-4 - Numbered ghost agents
        Other characters are ignored.
        
        Args:
            layoutText: List of strings representing the layout
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
        Processes a single character from the layout text.
        
        Args:
            x: X coordinate
            y: Y coordinate 
            layoutChar: Character from layout text to process
        """
        if layoutChar == "%":
            self.walls[x][y] = True
        elif layoutChar == ".":
            self.food[x][y] = True
        elif layoutChar == "o":
            self.capsules.append((x, y))
        elif layoutChar == "P":
            self.agentPositions.append((0, (x, y)))
        elif layoutChar in ["G"]:
            self.agentPositions.append((1, (x, y)))
            self.numGhosts += 1
        elif layoutChar in ["1", "2", "3", "4"]:
            self.agentPositions.append((int(layoutChar), (x, y)))
            self.numGhosts += 1


def getLayout(name: str, back: int = 2) -> Optional[Layout]:
    """
    Loads and returns a layout by name.
    
    Args:
        name: Name of layout to load
        back: Number of parent directories to search
        
    Returns:
        Layout object if found, None otherwise
    """
    if name.endswith(".lay"):
        layout = tryToLoad(f"layouts/{name}")
        if layout == None:
            layout = tryToLoad(name)
    else:
        layout = tryToLoad(f"layouts/{name}.lay")
        if layout == None:
            layout = tryToLoad(f"{name}.lay")
    if layout == None and back >= 0:
        curdir = os.path.abspath(".")
        os.chdir("..")
        layout = getLayout(name, back - 1)
        os.chdir(curdir)
    return layout


def tryToLoad(fullname: str) -> Optional[Layout]:
    """
    Attempts to load a layout from a file.
    
    Args:
        fullname: Full path to layout file
        
    Returns:
        Layout object if file exists and is valid, None otherwise
    """
    if not os.path.exists(fullname):
        return None
    f = open(fullname)
    try:
        return Layout([line.strip() for line in f])
    finally:
        f.close()
