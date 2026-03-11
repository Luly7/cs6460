"""
Layout management for Pacman game boards.

This module provides the Layout class and helper functions for managing game board layouts.
It handles loading layout files, processing layout characters, and managing static game 
board information like walls, food, capsules and agent positions.

The Layout class represents the static game board configuration and provides methods for:
- Loading layouts from text files
- Processing layout characters into game elements
- Managing wall, food, capsule and agent positions
- Querying board state and positions
- Calculating visibility information

Functions:
    getLayout: Load a layout file by name from the layouts directory
    tryToLoad: Attempt to load a layout from a specified file path

Python Version: 3.13
Last Modified: 24 Nov 2024
Modified by: George Rudolph

Changes:
- Added comprehensive module docstring
- Added detailed class and function descriptions
- Added type hints
- Added Python version compatibility note
- Added last modified date and modifier
- Verified Python 3.13 compatibility

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
"""

from util import manhattanDistance
from game import Grid
import os
import random
from functools import reduce
from typing import List, Tuple, Dict, Set, Optional, Union

VISIBILITY_MATRIX_CACHE: Dict[str, Grid] = {}


class Layout:
    """
    Manages the static information about the game board.
    
    Handles the layout grid including walls, food, capsules and agent positions.
    Provides methods for querying board state and positions.
    
    Attributes:
        width (int): Width of the game board in cells
        height (int): Height of the game board in cells
        walls (Grid): Grid marking wall locations
        food (Grid): Grid marking food pellet locations 
        capsules (List[Tuple[int, int]]): List of capsule coordinates
        agentPositions (List[Tuple[bool, Tuple[int, int]]]): List of agent positions
        numGhosts (int): Number of ghosts in the layout
        totalFood (int): Total number of food pellets
        visibility (Grid): Visibility information for each cell
    """

    def __init__(self, layoutText: List[str]) -> None:
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
        return self.numGhosts

    def initializeVisibilityMatrix(self) -> None:
        global VISIBILITY_MATRIX_CACHE
        if reduce(str.__add__, self.layoutText) not in VISIBILITY_MATRIX_CACHE:
            from game import Directions
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
        x, col = pos
        return self.walls[x][col]

    def getRandomLegalPosition(self) -> Tuple[int, int]:
        x = random.choice(list(range(self.width)))
        y = random.choice(list(range(self.height)))
        while self.isWall((x, y)):
            x = random.choice(list(range(self.width)))
            y = random.choice(list(range(self.height)))
        return (x, y)

    def getRandomCorner(self) -> Tuple[int, int]:
        poses = [(1, 1), (1, self.height - 2), (self.width - 2, 1),
                 (self.width - 2, self.height - 2)]
        return random.choice(poses)

    def getFurthestCorner(self, pacPos: Tuple[int, int]) -> Tuple[int, int]:
        poses = [(1, 1), (1, self.height - 2), (self.width - 2, 1),
                 (self.width - 2, self.height - 2)]
        dist, pos = max([(manhattanDistance(p, pacPos), p) for p in poses])
        return pos

    def isVisibleFrom(self, ghostPos: Tuple[float, float], pacPos: Tuple[int, int], pacDirection: str) -> bool:
        row, col = [int(x) for x in pacPos]
        return ghostPos in self.visibility[row][col][pacDirection]

    def __str__(self) -> str:
        return "\n".join(self.layoutText)

    def deepCopy(self) -> 'Layout':
        return Layout(self.layoutText[:])

    def processLayoutText(self, layoutText: List[str]) -> None:
        """
        Process the layout text to initialize the game board.

        Coordinates are flipped from the input format to the (x,y) convention.
        The shape of the maze uses characters to represent different objects:
         % - Wall
         . - Food
         o - Capsule
         G - Ghost
         P - Pacman
        Other characters are ignored.

        Args:
            layoutText: List of strings representing layout rows
        """
        maxY = self.height - 1
        for y in range(self.height):
            for x in range(self.width):
                layoutChar = layoutText[maxY - y][x]
                self.processLayoutChar(x, y, layoutChar)
        self.agentPositions.sort()
        self.agentPositions = [(i == 0, pos) for i, pos in self.agentPositions]

    def processLayoutChar(self, x: int, y: int, layoutChar: str) -> None:
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
    """
    Load a layout by name from the layouts directory.
    
    Args:
        name: Name of layout file to load
        back: Number of directory levels to search back
        
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
    """
    Attempt to load a layout from a file path.
    
    Args:
        fullname: Full file path to layout file
        
    Returns:
        Layout object if file exists and loads successfully, None otherwise
    """
    if(not os.path.exists(fullname)):
        return None
    f = open(fullname)
    try:
        return Layout([line.strip() for line in f])
    finally:
        f.close()
