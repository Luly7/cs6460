"""Text-based display module for Pacman game visualization.

This module provides text-based visualization capabilities for the Pacman game,
including:
- Null graphics implementation for headless execution
- Basic text display of game state and moves
- Configurable display timing and update frequency

Changes by George Rudolph 30 Nov 2024:
- Added comprehensive module docstring
- Added type hints throughout
- Improved class and method documentation
- Enhanced display formatting
- Standardized code style


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
from typing import List, Any, Optional

try:
    import pacman
except:
    pass

DRAW_EVERY = 1
SLEEP_TIME = 0  # This can be overwritten by __init__
DISPLAY_MOVES = False
QUIET = False  # Supresses output


class NullGraphics:
    """A null graphics implementation that performs no display."""
    
    def initialize(self, state: Any, isBlue: bool = False) -> None:
        """Initialize the null display.
        
        Args:
            state: The game state to initialize with
            isBlue: Whether Pacman is blue (default False)
        """
        pass

    def update(self, state: Any) -> None:
        """Update the null display.
        
        Args:
            state: The game state to update with
        """
        pass

    def checkNullDisplay(self) -> bool:
        """Check if this is a null display.
        
        Returns:
            True since this is a null display
        """
        return True

    def pause(self) -> None:
        """Pause the display for SLEEP_TIME seconds."""
        time.sleep(SLEEP_TIME)

    def draw(self, state: Any) -> None:
        """Draw the state as a string.
        
        Args:
            state: The game state to draw
        """
        print(state)

    def updateDistributions(self, dist: Any) -> None:
        """Update the displayed distributions.
        
        Args:
            dist: The distributions to display
        """
        pass

    def finish(self) -> None:
        """Clean up the display."""
        pass


class PacmanGraphics:
    """A basic text-based Pacman graphics implementation."""

    def __init__(self, speed: Optional[float] = None) -> None:
        """Initialize the Pacman graphics.
        
        Args:
            speed: Optional speed to set SLEEP_TIME to
        """
        if speed != None:
            global SLEEP_TIME
            SLEEP_TIME = speed

    def initialize(self, state: Any, isBlue: bool = False) -> None:
        """Initialize the display with the given state.
        
        Args:
            state: The game state to initialize with
            isBlue: Whether Pacman is blue (default False)
        """
        self.draw(state)
        self.pause()
        self.turn = 0
        self.agentCounter = 0

    def update(self, state: Any) -> None:
        """Update the display with a new state.
        
        Args:
            state: The game state to update with
        """
        numAgents = len(state.agentStates)
        self.agentCounter = (self.agentCounter + 1) % numAgents
        if self.agentCounter == 0:
            self.turn += 1
            if DISPLAY_MOVES:
                ghosts = [
                    pacman.nearestPoint(state.getGhostPosition(i))
                    for i in range(1, numAgents)
                ]
                print(
                    f"{self.turn:4d}) P: {str(pacman.nearestPoint(state.getPacmanPosition())):<8}"
                    f"| Score: {state.score:<5d}"
                    f"| Ghosts: {ghosts}"
                )
            if self.turn % DRAW_EVERY == 0:
                self.draw(state)
                self.pause()
        if state._win or state._lose:
            self.draw(state)

    def pause(self) -> None:
        """Pause the display for SLEEP_TIME seconds."""
        time.sleep(SLEEP_TIME)

    def draw(self, state: Any) -> None:
        """Draw the state as a string.
        
        Args:
            state: The game state to draw
        """
        print(state)

    def finish(self) -> None:
        """Clean up the display."""
        pass
