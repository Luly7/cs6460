"""
Keyboard-controlled agents for Pacman.

This module provides agent classes that can be controlled via keyboard input,
allowing for manual control of Pacman during gameplay. The main class is
KeyboardAgent which maps WASD and arrow keys to movement directions.

Key mappings:
- W/Up Arrow: Move North
- A/Left Arrow: Move West
- S/Down Arrow: Move South  
- D/Right Arrow: Move East
- Q: Stop movement

The agents handle keyboard input processing and legal move validation to ensure
valid actions are taken based on user input.

Python Version: 3.13
Last Modified: 24 Nov 2024
Modified by: George Rudolph

Changes:
- Added comprehensive module docstring
- Added type hints
- Added detailed key mapping documentation
- Added Python version compatibility note
- Added last modified date and modifier
- Verified Python 3.13 compatibility

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
"""


from game import Agent
from game import Directions
import random
from typing import List, Any


class KeyboardAgent(Agent):
    """
    An agent controlled by keyboard input.
    
    Uses WASD keys or arrow keys for movement control:
    - W/Up Arrow: Move North
    - A/Left Arrow: Move West  
    - S/Down Arrow: Move South
    - D/Right Arrow: Move East
    - Q: Stop movement
    """
    # NOTE: Arrow keys also work.
    WEST_KEY = 'a'
    EAST_KEY = 'd' 
    NORTH_KEY = 'w'
    SOUTH_KEY = 's'
    STOP_KEY = 'q'

    def __init__(self, index: int = 0) -> None:
        self.lastMove = Directions.STOP
        self.index = index
        self.keys: List[str] = []

    def getAction(self, state: Any) -> str:
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
        """
        Get the next move based on keyboard input and legal actions.
        
        Args:
            legal: List of legal actions available in current state
            
        Returns:
            The selected move direction
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
    """
    A second keyboard-controlled agent using IJKL keys.
    
    Movement controls:
    - I: Move North
    - J: Move West
    - K: Move South  
    - L: Move East
    - U: Stop movement
    """
    # NOTE: Arrow keys also work.
    WEST_KEY = 'j'
    EAST_KEY = "l"
    NORTH_KEY = 'i'
    SOUTH_KEY = 'k'
    STOP_KEY = 'u'

    def getMove(self, legal: List[str]) -> str:
        """
        Get the next move based on IJKL keyboard input and legal actions.
        
        Args:
            legal: List of legal actions available in current state
            
        Returns:
            The selected move direction
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
