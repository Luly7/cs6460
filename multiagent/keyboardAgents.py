"""keyboardAgents.py - Keyboard Control Agents for Pacman
=======================================================

This module provides agents that can be controlled via keyboard input.
It includes two agent classes:
- KeyboardAgent: Uses WASD/arrow keys for control
- KeyboardAgent2: Uses IJKL keys for control (for 2-player games)

Usage:
    These agents allow human players to control Pacman via keyboard.
    They can be selected when launching the game.

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

from game import Agent
from game import Directions
from typing import List, Any
import random


class KeyboardAgent(Agent):
    """An agent controlled by keyboard input.
    
    This agent responds to both WASD keys and arrow keys for movement control.
    The 'q' key can be used to stop movement.
    
    Attributes:
        WEST_KEY (str): Key for moving west ('a')
        EAST_KEY (str): Key for moving east ('d') 
        NORTH_KEY (str): Key for moving north ('w')
        SOUTH_KEY (str): Key for moving south ('s')
        STOP_KEY (str): Key for stopping movement ('q')
        lastMove (str): Direction of the last move made
        index (int): Index of this agent
        keys (List[str]): List of currently pressed keys
    """
    WEST_KEY = 'a'
    EAST_KEY = 'd'
    NORTH_KEY = 'w'
    SOUTH_KEY = 's'
    STOP_KEY = 'q'

    def __init__(self, index: int = 0) -> None:
        """Initialize the keyboard agent.
        
        Args:
            index: Index of this agent in the game (default 0)
        """
        self.lastMove = Directions.STOP
        self.index = index
        self.keys: List[str] = []

    def getAction(self, state: Any) -> str:
        """Get the action based on current keyboard input and game state.
        
        Args:
            state: Current game state
            
        Returns:
            str: Direction to move (from Directions constants)
        """
        from graphicsUtils import keys_waiting
        from graphicsUtils import keys_pressed
        keys = keys_waiting() + keys_pressed()
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
        """Get the move direction based on pressed keys and legal moves.
        
        Args:
            legal: List of legal moves available
            
        Returns:
            str: Direction to move (from Directions constants)
        """
        move = Directions.STOP
        if (self.WEST_KEY in self.keys or 'Left' in self.keys) and Directions.WEST in legal:
            move = Directions.WEST
        if (self.EAST_KEY in self.keys or 'Right' in self.keys) and Directions.EAST in legal:
            move = Directions.EAST
        if (self.NORTH_KEY in self.keys or 'Up' in self.keys) and Directions.NORTH in legal:
            move = Directions.NORTH
        if (self.SOUTH_KEY in self.keys or 'Down' in self.keys) and Directions.SOUTH in legal:
            move = Directions.SOUTH
        return move


class KeyboardAgent2(KeyboardAgent):
    """A second keyboard-controlled agent using IJKL keys.
    
    This agent is similar to KeyboardAgent but uses different keys,
    allowing two human players to control different agents simultaneously.
    
    Attributes:
        WEST_KEY (str): Key for moving west ('j')
        EAST_KEY (str): Key for moving east ('l')
        NORTH_KEY (str): Key for moving north ('i')
        SOUTH_KEY (str): Key for moving south ('k')
        STOP_KEY (str): Key for stopping movement ('u')
    """
    WEST_KEY = 'j'
    EAST_KEY = "l"
    NORTH_KEY = 'i'
    SOUTH_KEY = 'k'
    STOP_KEY = 'u'

    def getMove(self, legal: List[str]) -> str:
        """Get the move direction based on pressed keys and legal moves.
        
        Args:
            legal: List of legal moves available
            
        Returns:
            str: Direction to move (from Directions constants)
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
