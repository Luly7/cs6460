"""
Text-based display for Pacman game.

This module provides simple text-based visualization for the Pacman game,
including a null display and basic Pacman display that prints game state
to the console. The displays support both regular and learning game modes.

Classes:
    NullGraphics: A no-op display that does nothing
    PacmanGraphics: Basic text display showing game state, scores, and game info

Functions:
    None

Python Version: 3.13
Last Modified: 23 Nov 2024
Modified by: George Rudolph

Changes:
- Added comprehensive module docstring
- Added function section to docstring
- Improved class descriptions
- Verified Python 3.13 compatibility
- Added modifier attribution

# textDisplay.py
# -------------
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

import time
try:
    import pacman
except:
    pass

DRAW_EVERY = 1
SLEEP_TIME = 0  # This can be overwritten by __init__
DISPLAY_MOVES = False
QUIET = False  # Supresses output


class NullGraphics:
    """A no-op display class that does nothing."""
    
    def initialize(self, state: "GameState", isBlue: bool = False) -> None:
        """Initialize the null display.
        
        Args:
            state: Current game state
            isBlue: Whether Pacman is blue (default False)
        """
        pass

    def update(self, state: "GameState") -> None:
        """Update display with new state.
        
        Args:
            state: Current game state
        """
        pass

    def checkNullDisplay(self) -> bool:
        """Check if this is a null display.
        
        Returns:
            True, always
        """
        return True

    def pause(self) -> None:
        """Pause display for SLEEP_TIME seconds."""
        time.sleep(SLEEP_TIME)

    def draw(self, state: "GameState") -> None:
        """Draw the state.
        
        Args:
            state: Current game state
        """
        print(state)

    def updateDistributions(self, dist: dict) -> None:
        """Update belief distributions.
        
        Args:
            dist: Dictionary of belief distributions
        """
        pass

    def finish(self) -> None:
        """Clean up display."""
        pass


class PacmanGraphics:
    """Text-based display for Pacman game."""

    def __init__(self, speed: float = None) -> None:
        """Initialize PacmanGraphics display.
        
        Args:
            speed: Optional sleep time between frames
        """
        if speed != None:
            global SLEEP_TIME
            SLEEP_TIME = speed

    def initialize(self, state: "GameState", isBlue: bool = False) -> None:
        """Initialize the game display.
        
        Args:
            state: Initial game state
            isBlue: Whether Pacman is blue (default False)
        """
        self.draw(state)
        self.pause()
        self.turn = 0
        self.agentCounter = 0

    def update(self, state: "GameState") -> None:
        """Update display with new state.
        
        Args:
            state: Current game state
        """
        numAgents = len(state.agentStates)
        self.agentCounter = (self.agentCounter + 1) % numAgents
        if self.agentCounter == 0:
            self.turn += 1
            if DISPLAY_MOVES:
                ghosts = [pacman.nearestPoint(
                    state.getGhostPosition(i)) for i in range(1, numAgents)]
                print(f"{self.turn:4d}) P: {str(pacman.nearestPoint(state.getPacmanPosition())):<8s} | Score: {state.score:<5d} | Ghosts: {ghosts}")
            if self.turn % DRAW_EVERY == 0:
                self.draw(state)
                self.pause()
        if state._win or state._lose:
            self.draw(state)

    def pause(self) -> None:
        """Pause display for SLEEP_TIME seconds."""
        time.sleep(SLEEP_TIME)

    def draw(self, state: "GameState") -> None:
        """Draw the state.
        
        Args:
            state: Current game state
        """
        print(state)

    def finish(self) -> None:
        """Clean up display."""
        pass
