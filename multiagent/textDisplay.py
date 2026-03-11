"""Text-based display implementation for the Pacman AI projects.

This module provides text-based visualization capabilities for the Pacman game,
including a null display that performs no visualization and a basic ASCII display.
It's useful for debugging or when graphical display is not needed or available.

Originally developed at UC Berkeley for CS188 Intro to AI.
Modified by George Rudolph on 12 Nov 2024:
- Added type hints throughout the codebase
- Improved documentation and docstrings
- Verified compatibility with Python 3.13

Original Licensing Information:  
You are free to use or extend these projects for educational purposes provided that
(1) you do not distribute or publish solutions
(2) you retain this notice
(3) you provide clear attribution to UC Berkeley, including a link to http://ai.berkeley.edu

Original Attribution:
The Pacman AI projects were developed at UC Berkeley.
Core projects and autograders created by John DeNero (denero@cs.berkeley.edu) 
and Dan Klein (klein@cs.berkeley.edu).
Student side autograding added by Brad Miller, Nick Hay, and Pieter Abbeel (pabbeel@cs.berkeley.edu).
"""


from typing import Any, Optional
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
    """A null graphics implementation that performs no visualization.
    
    This class provides a no-op implementation of the graphics interface
    used by the game. It's useful when visualization is not needed or desired.
    """
    
    def initialize(self, state: Any, isBlue: bool = False) -> None:
        """Initialize the null display with the given state.
        
        Args:
            state: The game state to initialize with
            isBlue: Whether Pacman is blue (powered up)
        """
        pass

    def update(self, state: Any) -> None:
        """Update the null display with a new state.
        
        Args:
            state: The new game state
        """
        pass

    def checkNullDisplay(self) -> bool:
        """Check if this is a null display.
        
        Returns:
            True, as this is always a null display
        """
        return True

    def pause(self) -> None:
        """Pause for the configured sleep time."""
        time.sleep(SLEEP_TIME)

    def draw(self, state: Any) -> None:
        """Draw the current state.
        
        Args:
            state: The game state to draw
        """
        print(state)

    def updateDistributions(self, dist: Any) -> None:
        """Update probability distributions (no-op).
        
        Args:
            dist: The distributions to update
        """
        pass

    def finish(self) -> None:
        """Clean up the display (no-op)."""
        pass


class PacmanGraphics:
    """Graphics class for displaying Pacman game state in text mode."""
    
    def __init__(self, speed: Optional[float] = None) -> None:
        """Initialize the graphics with optional speed setting.
        
        Args:
            speed: Sleep time between frames in seconds. If provided, overrides default SLEEP_TIME.
        """
        if speed is not None:
            global SLEEP_TIME
            SLEEP_TIME = speed

    def initialize(self, state: Any, isBlue: bool = False) -> None:
        """Initialize display with starting game state.
        
        Args:
            state: Initial game state
            isBlue: Whether Pacman is in powered-up (blue) state
        """
        self.draw(state)
        self.pause()
        self.turn = 0
        self.agentCounter = 0

    def update(self, state: Any) -> None:
        """Update display with new game state.
        
        Args:
            state: Current game state to display
        """
        numAgents = len(state.agentStates)
        self.agentCounter = (self.agentCounter + 1) % numAgents
        if self.agentCounter == 0:
            self.turn += 1
            if DISPLAY_MOVES:
                ghosts = [pacman.nearestPoint(
                    state.getGhostPosition(i)) for i in range(1, numAgents)]
                print(f"{self.turn:4d}) P: {str(pacman.nearestPoint(state.getPacmanPosition())):<8s} "
                      f"| Score: {state.score:<5d} | Ghosts: {ghosts}")
            if self.turn % DRAW_EVERY == 0:
                self.draw(state)
                self.pause()
        if state._win or state._lose:
            self.draw(state)

    def pause(self) -> None:
        """Pause display for the configured sleep time."""
        time.sleep(SLEEP_TIME)

    def draw(self, state: Any) -> None:
        """Draw the current game state.
        
        Args:
            state: Game state to display
        """
        print(state)

    def finish(self) -> None:
        """Clean up display resources (no-op)."""
        pass
