"""Text-based display for Pacman game.

This module provides text-based visualization for the Pacman game,
with options for controlling display speed and verbosity. It implements
a simple text-based interface for displaying game state and agent movements.

Original Licensing Information:
You are free to use or extend these projects for educational purposes provided that
(1) you do not distribute or publish solutions, (2) you retain this notice, and
(3) you provide clear attribution to UC Berkeley, including a link to 
http://ai.berkeley.edu.

Original Attribution:
The Pacman AI projects were developed at UC Berkeley. The core projects and
autograders were primarily created by John DeNero (denero@cs.berkeley.edu) and
Dan Klein (klein@cs.berkeley.edu). Student side autograding was added by
Brad Miller, Nick Hay, and Pieter Abbeel (pabbeel@cs.berkeley.edu).

Author: George Rudolph
Date: 9 Nov 2024
Changes:
- Added type hints throughout
- Improved documentation and docstrings
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
    """A no-op graphics class that performs no drawing."""
    
    def initialize(self, state: 'pacman.GameState', isBlue: bool = False) -> None:
        """Initialize the null display.
        
        Args:
            state: Current game state
            isBlue: Whether Pacman team is blue (for capture games)
        """
        pass

    def update(self, state: 'pacman.GameState') -> None:
        """Update the null display.
        
        Args:
            state: Current game state
        """
        pass

    def checkNullDisplay(self) -> bool:
        """Check if this is a null display.
        
        Returns:
            bool: Always returns True for NullGraphics
        """
        return True

    def pause(self) -> None:
        """Pause the display for SLEEP_TIME seconds."""
        time.sleep(SLEEP_TIME)

    def draw(self, state: 'pacman.GameState') -> None:
        """Draw the state as text.
        
        Args:
            state: Current game state
        """
        print(state)

    def updateDistributions(self, dist: dict) -> None:
        """Update belief distributions (no-op).
        
        Args:
            dist: Dictionary of belief distributions
        """
        pass

    def finish(self) -> None:
        """Clean up display (no-op)."""
        pass

class PacmanGraphics:
    """A text-based graphics class for displaying Pacman games."""

    def __init__(self, speed: float = None) -> None:
        """Initialize graphics with optional speed setting.
        
        Args:
            speed: Time to sleep between frames (overrides SLEEP_TIME)
        """
        if speed is not None:
            global SLEEP_TIME
            SLEEP_TIME = speed

    def initialize(self, state: 'pacman.GameState', isBlue: bool = False) -> None:
        """Initialize the display with given state.
        
        Args:
            state: Initial game state
            isBlue: Whether Pacman team is blue (for capture games)
        """
        self.draw(state)
        self.pause()
        self.turn = 0
        self.agentCounter = 0

    def update(self, state: 'pacman.GameState') -> None:
        """Update the display with a new state.
        
        Args:
            state: Current game state
        """
        numAgents = len(state.agentStates)
        self.agentCounter = (self.agentCounter + 1) % numAgents
        if self.agentCounter == 0:
            self.turn += 1
            if DISPLAY_MOVES:
                ghosts = [pacman.nearestPoint(state.getGhostPosition(i)) for i in range(1, numAgents)]
                print(f"{self.turn:4d}) P: {str(pacman.nearestPoint(state.getPacmanPosition())):<8} | Score: {state.score:<5d} | Ghosts: {ghosts}")
            if self.turn % DRAW_EVERY == 0:
                self.draw(state)
                self.pause()
        if state._win or state._lose:
            self.draw(state)

    def pause(self) -> None:
        """Pause the display for SLEEP_TIME seconds."""
        time.sleep(SLEEP_TIME)

    def draw(self, state: 'pacman.GameState') -> None:
        """Draw the state as text.
        
        Args:
            state: Current game state
        """
        print(state)

    def finish(self) -> None:
        """Clean up display (no-op)."""
        pass
