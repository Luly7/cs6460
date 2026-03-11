"""
# keyboardAgents.py
# -----------------
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

Keyboard control module for the Pacman game.

This module provides agents that can be controlled via keyboard input.
The KeyboardAgent class allows controlling Pacman using either WASD keys
or arrow keys for movement. The module includes:

1. KeyboardAgent - Basic keyboard-controlled agent
2. KeyboardAgent2 - Alternative keyboard agent for 2-player games

The module works with game.py and graphicsUtils.py to handle user input
and agent movement in the game environment.

Changes by George Rudolph 30 Nov 2024:
- Verified compatibility with Python 3.13
- Enhanced module documentation
- Added type hints throughout
- Improved class and method documentation
- Added input validation
"""


from game import Agent
from game import Directions
import random
from typing import List, Optional


class KeyboardAgent(Agent):
    """
    An agent controlled by keyboard input.
    
    Uses WASD keys or arrow keys for movement control.
    'q' key can be used to stop movement.
    
    Attributes:
        WEST_KEY (str): Key for moving west ('a')
        EAST_KEY (str): Key for moving east ('d') 
        NORTH_KEY (str): Key for moving north ('w')
        SOUTH_KEY (str): Key for moving south ('s')
        STOP_KEY (str): Key for stopping ('q')
        lastMove (str): Direction of the last move made
        index (int): Index of this agent
        keys (List[str]): List of currently pressed keys
    """

    # NOTE: Arrow keys also work.
    WEST_KEY = "a"
    EAST_KEY = "d" 
    NORTH_KEY = "w"
    SOUTH_KEY = "s"
    STOP_KEY = "q"

    def __init__(self, index: int = 0) -> None:
        self.lastMove = Directions.STOP
        self.index = index
        self.keys = []

    def getAction(self, state) -> str:
        """
        Get the next action for the agent based on keyboard input.

        Args:
            state: Current game state

        Returns:
            str: Direction to move (one of Directions.{NORTH,SOUTH,EAST,WEST,STOP})
        """
        from graphicsUtils import keys_waiting
        from graphicsUtils import keys_pressed

        keys = list(keys_waiting()) + list(keys_pressed())
        if keys != []:
            self.keys = keys

        legal = state.getLegalActions(self.index)
        move = self.getMove(legal)

        if move == Directions.STOP:
            # Try to move in the same direction as before
            if self.lastMove in legal:
                move = self.lastMove

        if (self.STOP_KEY in self.keys) and Directions.STOP in legal:
            move = Directions.STOP

        if move not in legal:
            move = random.choice(legal)

        self.lastMove = move
        return move

    def getMove(self, legal: List[str]) -> str:
        """
        Determine move direction based on currently pressed keys.

        Args:
            legal: List of legal moves in current state

        Returns:
            str: Direction to move (one of Directions.{NORTH,SOUTH,EAST,WEST,STOP})
        """
        move = Directions.STOP
        if (
            self.WEST_KEY in self.keys or "Left" in self.keys
        ) and Directions.WEST in legal:
            move = Directions.WEST
        if (
            self.EAST_KEY in self.keys or "Right" in self.keys
        ) and Directions.EAST in legal:
            move = Directions.EAST
        if (
            self.NORTH_KEY in self.keys or "Up" in self.keys
        ) and Directions.NORTH in legal:
            move = Directions.NORTH
        if (
            self.SOUTH_KEY in self.keys or "Down" in self.keys
        ) and Directions.SOUTH in legal:
            move = Directions.SOUTH
        return move


class KeyboardAgent2(KeyboardAgent):
    """
    A second keyboard-controlled agent using IJKL keys.
    
    Uses IJKL keys for movement control:
    i: north
    j: west  
    k: south
    l: east
    u: stop
    
    Attributes:
        WEST_KEY (str): Key for moving west ('j')
        EAST_KEY (str): Key for moving east ('l')
        NORTH_KEY (str): Key for moving north ('i') 
        SOUTH_KEY (str): Key for moving south ('k')
        STOP_KEY (str): Key for stopping ('u')
    """

    # NOTE: Arrow keys also work.
    WEST_KEY = "j"
    EAST_KEY = "l"
    NORTH_KEY = "i"
    SOUTH_KEY = "k"
    STOP_KEY = "u"

    def getMove(self, legal: List[str]) -> str:
        """
        Determine move direction based on currently pressed keys.

        Args:
            legal: List of legal moves in current state

        Returns:
            str: Direction to move (one of Directions.{NORTH,SOUTH,EAST,WEST,STOP})
        """
        move = Directions.STOP
        if (self.WEST_KEY in self.keys) and Directions.WEST in legal:
            move = Directions.WEST
        if (self.EAST_KEY in self.keys) and Directions.EAST in legal:
            move = Directions.EAST
        if (self.NORTH_KEY in self.keys) and Directions.NORTH in legal:
            move = Directions.NORTH
        if (self.SOUTH_KEY in self.keys) and Directions.SOUTH in legal:
            move = Directions.SOUTH
        return move
