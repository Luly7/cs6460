"""Keyboard-controlled agents for Pacman.

This module provides agents that can be controlled via keyboard input, allowing
for manual play of the Pacman game. It includes both a basic keyboard agent
and a directional keyboard agent with different control schemes.

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

from game import Agent
from game import Directions
from pacman import GameState
from typing import List, Optional
import random

class KeyboardAgent(Agent):
    """
    An agent controlled by keyboard input.
    
    This agent maps keyboard keys to Pacman movement directions. Both WASD keys
    and arrow keys can be used for control. The 'q' key stops movement.
    
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
    WEST_KEY  = 'a'
    EAST_KEY  = 'd'
    NORTH_KEY = 'w'
    SOUTH_KEY = 's'
    STOP_KEY = 'q'

    def __init__(self, index: int = 0) -> None:
        """
        Initialize the keyboard agent.
        
        Args:
            index: Index of this agent in the game
        """
        self.lastMove = Directions.STOP
        self.index = index
        self.keys: List[str] = []

    def getAction(self, state: GameState) -> str:
        """
        Get the action to take based on current keyboard input.
        
        Args:
            state: Current game state
            
        Returns:
            Direction to move in based on keyboard input and legal moves
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
        Get the move direction based on current keyboard input and legal moves.
        
        Args:
            legal: List of legal moves available
            
        Returns:
            Direction to move based on keyboard input
        """
        move = Directions.STOP
        if (self.WEST_KEY in self.keys or 'Left' in self.keys) and Directions.WEST in legal:  move = Directions.WEST
        if (self.EAST_KEY in self.keys or 'Right' in self.keys) and Directions.EAST in legal: move = Directions.EAST
        if (self.NORTH_KEY in self.keys or 'Up' in self.keys) and Directions.NORTH in legal:   move = Directions.NORTH
        if (self.SOUTH_KEY in self.keys or 'Down' in self.keys) and Directions.SOUTH in legal: move = Directions.SOUTH
        return move

class KeyboardAgent2(KeyboardAgent):
    """
    A second keyboard-controlled agent using alternate keys.
    
    This agent uses IJKL keys instead of WASD for movement control.
    The 'u' key stops movement.
    """
    WEST_KEY  = 'j'
    EAST_KEY  = "l"
    NORTH_KEY = 'i'
    SOUTH_KEY = 'k'
    STOP_KEY = 'u'

    def getMove(self, legal: List[str]) -> str:
        """
        Get the move direction based on current keyboard input and legal moves.
        
        Args:
            legal: List of legal moves available
            
        Returns:
            Direction to move based on keyboard input
        """
        move = Directions.STOP
        if (self.WEST_KEY in self.keys) and Directions.WEST in legal:  move = Directions.WEST
        if (self.EAST_KEY in self.keys) and Directions.EAST in legal: move = Directions.EAST
        if (self.NORTH_KEY in self.keys) and Directions.NORTH in legal:   move = Directions.NORTH
        if (self.SOUTH_KEY in self.keys) and Directions.SOUTH in legal: move = Directions.SOUTH
        return move
