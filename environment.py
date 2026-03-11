"""
Environment abstraction for reinforcement learning.

This module provides the Environment base class that defines the core interface
for reinforcement learning environments in the Pacman domain. Key functionality:

- State management and transitions
- Action space definition
- Reward signals
- Environment reset capability

The Environment class serves as an abstract interface that specific game 
environments must implement. It provides the essential methods needed for
agents to interact with and learn from the environment:

- getCurrentState: Get current environment state
- getPossibleActions: Get valid actions for a state  
- doAction: Execute action and get reward/next state
- reset: Reset environment to initial state

Most code originally by Dan Klein and John Denero for CS188 at UC Berkeley.

Python Version: 3.13
Last Modified: 24 Nov 2024
Modified by: George Rudolph

Changes:
- Added comprehensive module docstring
- Added detailed interface documentation
- Added type hints
- Added Python version compatibility note
- Added last modified date and modifier
- Verified Python 3.13 compatibility

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

from typing import Any, List, Tuple

class Environment:

    def getCurrentState(self) -> Any:
        """
        Returns the current state of the environment.
        
        Returns:
            Any: The current state representation
        """
        abstract

    def getPossibleActions(self, state: Any) -> List[Any]:
        """
        Returns possible actions available in the given state.
        
        Args:
            state: The current environment state
            
        Returns:
            List[Any]: List of valid actions that can be taken from this state.
                      Returns empty list for terminal states.
        """
        abstract

    def doAction(self, action: Any) -> Tuple[float, Any]:
        """
        Executes the given action in the current environment state.
        
        Args:
            action: The action to perform
            
        Returns:
            Tuple[float, Any]: A tuple containing:
                - float: The reward received for the action
                - Any: The next state after performing the action
        """
        abstract

    def reset(self) -> None:
        """
        Resets the environment to its initial state.
        
        Returns:
            None
        """
        abstract

    def isTerminal(self) -> bool:
        """
        Checks if the environment has reached a terminal state.
        
        A terminal state is one where no further actions are possible.
        
        Returns:
            bool: True if current state is terminal, False otherwise
        """
        state = self.getCurrentState()
        actions = self.getPossibleActions(state)
        return len(actions) == 0
